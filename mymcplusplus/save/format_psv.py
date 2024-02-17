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

import struct

from . import ps2save
from .. import ps2mc_dir
from . import utils
from .. import utils as common_utils


FORMAT_ID = "psv"

PSV_MAGIC = b"\x00VSP"


_psv_header_struct = struct.Struct("<4sI40s8xII")

_ps2_header_struct = struct.Struct("<IIIIIIIIII")
_ps2_file_info_struct = struct.Struct("<8s8sII32s")
_ps2_file_offset_struct = struct.Struct("<I")

_ps1_header_struct = struct.Struct("<II20xI4x20s12x")


class PS2FileInfo:
    def __init__(self, d):
        (created_data,
         modified_data,
         self.size,
         self.mode,
         self.filename) = d

        self.created = ps2mc_dir.unpack_tod(created_data)
        self.modified = ps2mc_dir.unpack_tod(modified_data)

        self.filename = common_utils.zero_terminate(self.filename)

    def dirent(self, files_count):
        return (self.mode, 0, files_count, self.created, 0, 0,
                self.modified, 0, self.filename)


def poll(hdr):
    return hdr.startswith(PSV_MAGIC)


def load_ps2(save, f):
    (_, sys_pos, sys_size,
     icon1_pos, icon1_size,
     icon2_pos, icon2_size,
     icon3_pos, icon3_size,
     files_count) = utils.read_struct(f, _ps2_header_struct)

    root_dir_info = PS2FileInfo(utils.read_struct(f, _ps2_file_info_struct))

    if not ps2mc_dir.mode_is_dir(root_dir_info.mode):
        raise ps2save.Corrupt("PSV root file is not a directory.", f)

    save.set_directory(root_dir_info.dirent(files_count))

    files = []
    for i in range(files_count):
        file_info = PS2FileInfo(utils.read_struct(f, _ps2_file_info_struct))
        file_offset = utils.read_struct(f, _ps2_file_offset_struct)[0]

        if ps2mc_dir.mode_is_dir(file_info.mode):
            raise ps2save.Subdir(f)

        files.append((file_info, file_offset))

    for (i, (file_info, file_offset)) in enumerate(files):
        f.seek(file_offset)
        save.set_file(i, file_info.dirent(0), utils.read_fixed(f, file_info.size))


def load_ps1(save, f):
    (save_size, save_offset, _, prod_code) = utils.read_struct(f, _ps1_header_struct)

    dir_mode = ps2mc_dir.DF_RWX | ps2mc_dir.DF_DIR | ps2mc_dir.DF_PSX | ps2mc_dir.DF_EXISTS
    created = modified = ps2mc_dir.tod_now()
    save.set_directory((dir_mode, 0, 1, created, 0, 0, modified, 0, prod_code))

    mode = ps2mc_dir.DF_RWX | ps2mc_dir.DF_FILE \
           | ps2mc_dir.DF_0080 | ps2mc_dir.DF_0400 | ps2mc_dir.DF_EXISTS
    f.seek(save_offset)
    save.set_file(0, (mode, 0, 0, created, 0, 0, modified, 0, prod_code),
                  utils.read_fixed(f, save_size))


def load(save, f):
    (magic, version, signature, _, save_type) = utils.read_struct(f, _psv_header_struct)

    if magic != PSV_MAGIC:
        raise ps2save.Corrupt("Not a PSV file.", f)

    # Not sure if "version" is the correct name for this field,
    # but the PS Vita dumps use it for that and have the same magic.
    if version != 0:
        raise ps2save.Corrupt("Wrong PSV Version.", f)

    if save_type == 2:
        load_ps2(save, f)
    elif save_type == 1:
        load_ps1(save, f)
    else:
        raise ps2save.Corrupt("PSV save type {} not recognized.".format(save_type))


def save_ps2(save, f):
#    f.write(_psv_header_struct.pack(PSV_MAGIC,
#                                    0, # version
#                                    b"\x00" * 40, # TODO: signature
#                                    0x2c, # size of next section?
#                                    2)) # PS2
#
#    dirent = save.dirent
#    files_count = dirent[2]
#
#    base_offset = _psv_header_struct.size + _ps2_header_struct.size \
#                  + _ps2_file_info_struct.size * (files_count + 1) \
#                  + _ps2_file_offset_struct.size * files_count
#
    raise NotImplementedError()


def save_ps1(save, f):
    raise NotImplementedError()


def save(save, f):
    if ps2mc_dir.mode_is_psx_dir(save.dirent[0]):
        save_ps1(save, f)
    else:
        save_ps2(save, f)
