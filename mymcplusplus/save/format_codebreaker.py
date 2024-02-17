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

import array
import zlib

from .. import ps2mc_dir
from .. import utils
from .utils import *


FORMAT_ID = "cbs"

PS2SAVE_CBS_MAGIC = b"CFU\0"

# This is the initial permutation state ("S") for the RC4 stream cipher
# algorithm used to encrpyt and decrypt Codebreaker saves.
PS2SAVE_CBS_RC4S = [0x5f, 0x1f, 0x85, 0x6f, 0x31, 0xaa, 0x3b, 0x18,
            0x21, 0xb9, 0xce, 0x1c, 0x07, 0x4c, 0x9c, 0xb4,
            0x81, 0xb8, 0xef, 0x98, 0x59, 0xae, 0xf9, 0x26,
            0xe3, 0x80, 0xa3, 0x29, 0x2d, 0x73, 0x51, 0x62,
            0x7c, 0x64, 0x46, 0xf4, 0x34, 0x1a, 0xf6, 0xe1,
            0xba, 0x3a, 0x0d, 0x82, 0x79, 0x0a, 0x5c, 0x16,
            0x71, 0x49, 0x8e, 0xac, 0x8c, 0x9f, 0x35, 0x19,
            0x45, 0x94, 0x3f, 0x56, 0x0c, 0x91, 0x00, 0x0b,
            0xd7, 0xb0, 0xdd, 0x39, 0x66, 0xa1, 0x76, 0x52,
            0x13, 0x57, 0xf3, 0xbb, 0x4e, 0xe5, 0xdc, 0xf0,
            0x65, 0x84, 0xb2, 0xd6, 0xdf, 0x15, 0x3c, 0x63,
            0x1d, 0x89, 0x14, 0xbd, 0xd2, 0x36, 0xfe, 0xb1,
            0xca, 0x8b, 0xa4, 0xc6, 0x9e, 0x67, 0x47, 0x37,
            0x42, 0x6d, 0x6a, 0x03, 0x92, 0x70, 0x05, 0x7d,
            0x96, 0x2f, 0x40, 0x90, 0xc4, 0xf1, 0x3e, 0x3d,
            0x01, 0xf7, 0x68, 0x1e, 0xc3, 0xfc, 0x72, 0xb5,
            0x54, 0xcf, 0xe7, 0x41, 0xe4, 0x4d, 0x83, 0x55,
            0x12, 0x22, 0x09, 0x78, 0xfa, 0xde, 0xa7, 0x06,
            0x08, 0x23, 0xbf, 0x0f, 0xcc, 0xc1, 0x97, 0x61,
            0xc5, 0x4a, 0xe6, 0xa0, 0x11, 0xc2, 0xea, 0x74,
            0x02, 0x87, 0xd5, 0xd1, 0x9d, 0xb7, 0x7e, 0x38,
            0x60, 0x53, 0x95, 0x8d, 0x25, 0x77, 0x10, 0x5e,
            0x9b, 0x7f, 0xd8, 0x6e, 0xda, 0xa2, 0x2e, 0x20,
            0x4f, 0xcd, 0x8f, 0xcb, 0xbe, 0x5a, 0xe0, 0xed,
            0x2c, 0x9a, 0xd4, 0xe2, 0xaf, 0xd0, 0xa9, 0xe8,
            0xad, 0x7a, 0xbc, 0xa8, 0xf2, 0xee, 0xeb, 0xf5,
            0xa6, 0x99, 0x28, 0x24, 0x6c, 0x2b, 0x75, 0x5d,
            0xf8, 0xd3, 0x86, 0x17, 0xfb, 0xc0, 0x7b, 0xb3,
            0x58, 0xdb, 0xc7, 0x4b, 0xff, 0x04, 0x50, 0xe9,
            0x88, 0x69, 0xc9, 0x2a, 0xab, 0xfd, 0x5b, 0x1b,
            0x8a, 0xd9, 0xec, 0x27, 0x44, 0x0e, 0x33, 0xc8,
            0x6b, 0x93, 0x32, 0x48, 0xb6, 0x30, 0x43, 0xa5]


def _rc4_crypt(s, t):
    """RC4 encrypt/decrypt the string t using the permutation s.

    Returns a byte array."""

    s = array.array('B', s)
    t = array.array('B', t)
    j = 0
    for ii in range(len(t)):
        i = (ii + 1) % 256
        j = (j + s[i]) % 256
        (s[i], s[j]) = (s[j], s[i])
        t[ii] ^= s[(s[i] + s[j]) % 256]
    return t


def poll(hdr):
    return hdr.startswith(PS2SAVE_CBS_MAGIC)


def load(save, f):
    magic = f.read(4)
    if magic != PS2SAVE_CBS_MAGIC:
        raise ps2save.Corrupt("Not a Codebreaker save file.", f)
    (d04, hlen) = struct.unpack("<LL", read_fixed(f, 8))
    if hlen < 92 + 32:
        raise ps2save.Corrupt("Header lengh too short.", f)
    (dlen, flen, dirname, created, modified, d44, d48, dirmode,
     d50, d54, d58, title) = struct.unpack("<LL32s8s8sLLLLLL%ds" % (hlen - 92), read_fixed(f, hlen - 12))
    dirname = utils.zero_terminate(dirname)
    created = ps2mc_dir.unpack_tod(created)
    modified = ps2mc_dir.unpack_tod(modified)
    title = utils.zero_terminate(title)

    # These fields don't always seem to be set correctly.
    if not ps2mc_dir.mode_is_dir(dirmode):
        dirmode = ps2mc_dir.DF_RWX | ps2mc_dir.DF_DIR | ps2mc_dir.DF_0400
    if ps2mc_dir.tod_to_time(created) == 0:
        created = ps2mc_dir.tod_now()
    if ps2mc_dir.tod_to_time(modified) == 0:
        modified = ps2mc_dir.tod_now()

    # flen can either be the total length of the file,
    # or the length of compressed body of the file
    body = f.read(flen)
    clen = len(body)
    if clen != flen and clen != flen - hlen:
        raise ps2save.Eof(f)
    body = _rc4_crypt(PS2SAVE_CBS_RC4S, body)
    dcobj = zlib.decompressobj()
    body = dcobj.decompress(body, dlen)

    files = []
    while body != b"":
        if len(body) < 64:
            raise ps2save.Eof(f)
        header = struct.unpack("<8s8sLHHLL32s", body[:64])
        size = header[2]
        data = body[64 : 64 + size]
        if len(data) != size:
            raise ps2save.Eof(f)
        body = body[64 + size:]
        files.append((header, data))

    save.set_directory((dirmode, 0, len(files), created, 0, 0, modified, 0, dirname))
    for i in range(len(files)):
        (header, data) = files[i]
        (created, modified, size, mode, h06, h08, h0C, name) = header
        name = utils.zero_terminate(name)
        created = ps2mc_dir.unpack_tod(created)
        modified = ps2mc_dir.unpack_tod(modified)
        if not ps2mc_dir.mode_is_file(mode):
            raise ps2save.Subdir(f)
        if ps2mc_dir.tod_to_time(created) == 0:
            created = ps2mc_dir.tod_now()
        if ps2mc_dir.tod_to_time(modified) == 0:
            modified = ps2mc_dir.tod_now()
        save.set_file(i, (mode, 0, size, created, 0, 0, modified, 0, name), data)
