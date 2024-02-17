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

from . import ps2save
from .. import ps2mc_dir
from .utils import *
from ..round import round_up


FORMAT_ID = "psu"


def poll(hdr):
    #
    # EMS (.psu) save files don't have a magic number.  Check to
    # see if it looks enough like one.
    #

    if len(hdr) < ps2mc_dir.PS2MC_DIRENT_LENGTH * 3:
        return None

    dirent = ps2mc_dir.unpack_dirent(hdr[:ps2mc_dir.PS2MC_DIRENT_LENGTH])
    dotent = ps2mc_dir.unpack_dirent(hdr[ps2mc_dir.PS2MC_DIRENT_LENGTH : ps2mc_dir.PS2MC_DIRENT_LENGTH * 2])
    dotdotent = ps2mc_dir.unpack_dirent(hdr[ps2mc_dir.PS2MC_DIRENT_LENGTH * 2:])

    return ps2mc_dir.mode_is_dir(dirent[0]) and ps2mc_dir.mode_is_dir(dotent[0]) \
            and ps2mc_dir.mode_is_dir(dotdotent[0]) and dirent[2] >= 2 \
            and dotent[8] == b"." and dotdotent[8] == b".."


def load(save, f):
    """Load EMS (.psu) save files."""

    cluster_size = 1024

    dirent = ps2mc_dir.unpack_dirent(read_fixed(f, ps2mc_dir.PS2MC_DIRENT_LENGTH))
    dotent = ps2mc_dir.unpack_dirent(read_fixed(f, ps2mc_dir.PS2MC_DIRENT_LENGTH))
    dotdotent = ps2save.unpack_dirent(read_fixed(f, ps2mc_dir.PS2MC_DIRENT_LENGTH))
    if (not ps2mc_dir.mode_is_dir(dirent[0])
            or not ps2save.mode_is_dir(dotent[0])
            or not ps2save.mode_is_dir(dotdotent[0])
            or dirent[2] < 2):
        raise ps2save.Corrupt("Not a EMS (.psu) save file.", f)

    dirent[2] -= 2
    save.set_directory(dirent)

    for i in range(dirent[2]):
        ent = ps2mc_dir.unpack_dirent(read_fixed(f, ps2mc_dir.PS2MC_DIRENT_LENGTH))
        if not ps2mc_dir.mode_is_file(ent[0]):
            raise ps2save.Subdir(f)
        flen = ent[2]
        save.set_file(i, ent, read_fixed(f, flen))
        read_fixed(f, round_up(flen, cluster_size) - flen)


def save(save, f):
    cluster_size = 1024

    dirent = save.dirent[:]
    dirent[2] += 2
    f.write(ps2mc_dir.pack_dirent(dirent))
    f.write(ps2mc_dir.pack_dirent((ps2mc_dir.DF_RWX | ps2mc_dir.DF_DIR | ps2mc_dir.DF_0400 | ps2mc_dir.DF_EXISTS,
                                   0, 0, dirent[3],
                                   0, 0, dirent[3], 0, b".")))
    f.write(ps2mc_dir.pack_dirent((ps2mc_dir.DF_RWX | ps2mc_dir.DF_DIR | ps2mc_dir.DF_0400 | ps2mc_dir.DF_EXISTS,
                                   0, 0, dirent[3],
                                   0, 0, dirent[3], 0, b"..")))

    for i in range(dirent[2] - 2):
        (ent, data) = save.get_file(i)
        f.write(ps2mc_dir.pack_dirent(ent))
        if not ps2mc_dir.mode_is_file(ent[0]):
            # print ent
            # print hex(ent[0])
            raise ps2save.Error("Directory has a subdirectory.")
        f.write(data)
        f.write(b"\0" * (round_up(len(data), cluster_size) - len(data)))
    f.flush()



