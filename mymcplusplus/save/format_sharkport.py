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

from .. import ps2mc_dir
from .. import utils
from . import ps2save
from .utils import *


FORMAT_ID = "sps"

PS2SAVE_SPS_MAGIC = b"\x0d\0\0\0SharkPortSave"


def poll(hdr):
    return hdr.startswith(PS2SAVE_SPS_MAGIC)


def load(save, f):
    magic = f.read(17)
    if magic != PS2SAVE_SPS_MAGIC:
        raise ps2save.Corrupt("Not a SharkPort/X-Port save file.", f)
    (savetype,) = struct.unpack("<L", read_fixed(f, 4))
    dirname = read_long_string(f)
    datestamp = read_long_string(f)
    comment = read_long_string(f)

    (flen,) = struct.unpack("<L", read_fixed(f, 4))

    (hlen, dirname, dirlen, dirmode, created, modified) \
        = struct.unpack("<H64sL8xH2x8s8s", read_fixed(f, 98))
    read_fixed(f, hlen - 98)

    dirname = utils.zero_terminate(dirname)
    created = ps2mc_dir.unpack_tod(created)
    modified = ps2mc_dir.unpack_tod(modified)

    # mode values are byte swapped
    dirmode = dirmode // 256 % 256 + dirmode % 256 * 256
    dirlen -= 2
    if not ps2mc_dir.mode_is_dir(dirmode) or dirlen < 0:
        raise ps2save.Corrupt("Bad values in directory entry.", f)
    save.set_directory((dirmode, 0, dirlen, created, 0, 0, modified, 0, dirname))

    for i in range(dirlen):
        (hlen, name, flen, mode, created, modified) \
            = struct.unpack("<H64sL8xH2x8s8s",
                            read_fixed(f, 98))
        if hlen < 98:
            raise ps2save.Corrupt("Header length too short.", f)
        read_fixed(f, hlen - 98)
        name = utils.zero_terminate(name)
        created = ps2mc_dir.unpack_tod(created)
        modified = ps2mc_dir.unpack_tod(modified)
        mode = mode // 256 % 256 + mode % 256 * 256
        if not ps2mc_dir.mode_is_file(mode):
            raise ps2save.Subdir(f)
        save.set_file(i, (mode, 0, flen, created, 0, 0,
                          modified, 0, name),
                      read_fixed(f, flen))

    # ignore 4 byte checksum at the end



# def sps_check(s):
#     """Calculate the checksum for a SharkPort save."""
#
#     h = 0
#     for c in array.array('B', s):
#         h += c << (h % 24)
#         h &= 0xFFFFFFFF
#     return h