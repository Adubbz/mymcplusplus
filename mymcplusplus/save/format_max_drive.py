#
# This file is part of mymc+, based on mymc by Ross Ridge.
#
# mymc+ is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# mymc+ is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with mymc+.  If not, see <http://www.gnu.org/licenses/>.
#

import binascii

from .. import ps2mc_dir
from .. import utils
from . import ps2save
from . import lzari
from ..round import round_up
from .utils import *


FORMAT_ID = "max"

PS2SAVE_MAX_MAGIC = b"Ps2PowerSave"


def poll(hdr):
    return hdr.startswith(PS2SAVE_MAX_MAGIC)


def load2(save, f):
    (length, s) = save._compressed
    save._compressed = None

    if lzari is None:
        raise ps2mc_dir.Error("The lzari module is needed to decompress MAX Drive saves.")
    s = lzari.decode(s, length, "decompressing " + save.dirent[8].decode("ascii") + ": ")
    dirlen = save.dirent[2]
    timestamp = save.dirent[3]
    off = 0
    for i in range(dirlen):
        if len(s) - off < 36:
            raise ps2save.Eof(f)
        (l, name) = struct.unpack("<L32s", s[off: off + 36])
        name = utils.zero_terminate(name)
        # print "%08x %08x %s" % (off, l, name)
        off += 36
        data = s[off: off + l]
        if len(data) != l:
            raise ps2save.Eof(f)
        save.set_file(i,
                      (ps2mc_dir.DF_RWX | ps2mc_dir.DF_FILE | ps2mc_dir.DF_0400 | ps2mc_dir.DF_EXISTS,
                       0, l, timestamp, 0, 0, timestamp, 0,
                       name),
                      data)
        off += l
        off = round_up(off + 8, 16) - 8


def load(save, f, timestamp=None):
    s = f.read(0x5C)
    magic = None
    if len(s) == 0x5C:
        (magic, crc, dirname, iconsysname, clen, dirlen,
         length) = struct.unpack("<12sL32s32sLLL", s)
    if magic != PS2SAVE_MAX_MAGIC:
        raise ps2save.Corrupt("Not a MAX Drive save file", f)
    if clen == length:
        # some saves have the uncompressed size here
        # instead of the compressed size
        s = f.read()
    else:
        s = read_fixed(f, clen - 4)
    dirname = utils.zero_terminate(dirname)
    if timestamp == None:
        timestamp = ps2mc_dir.tod_now()
    save.set_directory((ps2mc_dir.DF_RWX | ps2mc_dir.DF_DIR | ps2mc_dir.DF_0400 | ps2mc_dir.DF_EXISTS,
                        0, dirlen, timestamp, 0, 0, timestamp, 0,
                        dirname),
                       f)
    save._compressed = (length, s)


def save(save, f):
    if lzari is None:
        raise ps2mc_dir.Error("The lzari module is needed to decompress MAX Drive saves.")

    iconsysname = ""
    icon_sys = save.get_icon_sys()
    if icon_sys != None:
        title = icon_sys.get_title("ascii")
        if len(title[0]) > 0 and title[0][-1] != ' ':
            iconsysname = title[0] + " " + title[1].strip()
        else:
            iconsysname = title[0] + title[1].rstrip()
    s = b""
    dirent = save.dirent
    for i in range(dirent[2]):
        (ent, data) = save.get_file(i)
        if not ps2mc_dir.mode_is_file(ent[0]):
            raise ps2mc_dir.Error("Non-file in save file.")
        s += struct.pack("<L32s", ent[2], ent[8])
        s += data
        s += b"\0" * (round_up(len(s) + 8, 16) - 8 - len(s))
    length = len(s)
    progress = "compressing " + dirent[8].decode("ascii") + ": "
    compressed = lzari.encode(s, progress)
    hdr = struct.pack("<12sL32s32sLLL", PS2SAVE_MAX_MAGIC,
                      0, dirent[8], iconsysname.encode("ascii"),
                      len(compressed) + 4, dirent[2], length)
    crc = binascii.crc32(hdr)
    crc = binascii.crc32(compressed, crc)
    f.write(struct.pack("<12sL32s32sLLL", PS2SAVE_MAX_MAGIC,
                        crc & 0xFFFFFFFF, dirent[8], iconsysname.encode("ascii"),
                        len(compressed) + 4, dirent[2], length))
    f.write(compressed)
    f.flush()
