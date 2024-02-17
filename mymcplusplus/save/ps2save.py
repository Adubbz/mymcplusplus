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

"""A simple interface for working with various PS2 save file formats."""

import sys
import os
import binascii

from ..ps2mc_dir import *
from .. import ps2iconsys


from . import format_codebreaker, format_ems, format_max_drive, format_sharkport, format_psv


formats = [
    format_codebreaker,
    format_ems,
    format_max_drive,
    format_sharkport,
    format_psv
]


class Error(Exception):
    """Base for all exceptions specific to this module."""
    pass


class Corrupt(Error):
    """Corrupt save file."""

    def __init__(self, msg, f = None):
        fn = None
        if f != None:
            fn = getattr(f, "name", None)
        self.filename = fn
        Error.__init__(self, "Corrupt save file: " + msg)


class Eof(Corrupt):
    """Save file is truncated."""

    def __init__(self, f = None):
        Corrupt.__init__(self, "Unexpected EOF", f)


class Subdir(Corrupt):
    def __init__(self, f = None):
        Corrupt.__init__(self, "Non-file in save file.", f)


def poll_format(f):
    """Detect the type of PS2 save file.

    The file-like object f should be positioned at the start of the file.
    """

    hdr = f.read(PS2MC_DIRENT_LENGTH * 3)

    for format in formats:
        if format.poll(hdr):
            return format

    return None


def format_for_filename(filename):
    filename = filename.lower()
    if filename.endswith(".max"):
        return format_max_drive
    #elif filename.endswith(".psv"):
    #    return format_psv
    else:
        return format_ems


#
# Set up tables of illegal and problematic characters in file names.
#
_bad_filename_chars = ("".join(map(chr, list(range(32))))
               + "".join(map(chr, list(range(127, 256)))))
_bad_filename_repl = "_" * len(_bad_filename_chars)

if os.name in ["nt", "os2", "ce"]:
    _bad_filename_chars += '<>:"/\\|'
    _bad_filename_repl +=  "()_'___"
    _bad_filename_chars2 = _bad_filename_chars + "?* "
    _bad_filename_repl2 = _bad_filename_repl +   "___"
else:
    _bad_filename_chars += "/"
    _bad_filename_repl += "_"
    _bad_filename_chars2 = _bad_filename_chars + "?*'&|:[<>] \\\""
    _bad_filename_repl2 = _bad_filename_repl +   "______(())___"

_filename_trans = str.maketrans(_bad_filename_chars, _bad_filename_repl)
_filename_trans2 = str.maketrans(_bad_filename_chars2, _bad_filename_repl2)


def fix_filename(filename):
    """Replace illegal or problematic characters from a filename."""
    return filename.translate(_filename_trans)


def make_longname(dirname, sf):
    """Return a string containing a verbose filename for a save file."""

    icon_sys = sf.get_icon_sys()
    title = ""
    if icon_sys is not None:
        title = icon_sys.get_title("ascii")
        title = title[0] + " " + title[1]
        title = " ".join(title.split())
    crc = binascii.crc32(b"")
    for (ent, data) in sf:
        crc = binascii.crc32(data, crc)
    if len(dirname) >= 12 and (dirname[0:2] in ("BA", "BJ", "BE", "BK")):
        if dirname[2:6] == "DATA":
            title = ""
        else:
            #dirname = dirname[2:6] + dirname[7:12]
            dirname = dirname[2:12]

    return fix_filename("%s %s (%08X)" % (dirname, title, crc & 0xFFFFFFFF))







class PS2SaveFile(object):
    """The state of a PlayStation 2 save file."""
    
    def __init__(self):
        self.file_ents = None
        self.file_data = None
        self.dirent = None
        self._defer_load_max_file = None
        self._compressed = None


    def set_directory(self, ent, defer_file = None):
        self._defer_load_max_file = defer_file
        self._compressed = None
        self.file_ents = [None] * ent[2]
        self.file_data = [None] * ent[2]
        self.dirent = list(ent)


    def set_file(self, i, ent, data):
        self.file_ents[i] = ent
        self.file_data[i] = data


    def get_directory(self):
        return self.dirent


    def get_file(self, i):
        if self._defer_load_max_file is not None:
            f = self._defer_load_max_file
            self._defer_load_max_file = None
            format_max_drive.load2(self, f)
        return self.file_ents[i], self.file_data[i]


    def __len__(self):
        return self.dirent[2]


    def __getitem__(self, index):
        return self.get_file(index)

    
    def get_icon_sys(self):
        for i in range(self.dirent[2]):
            (ent, data) = self.get_file(i)
            if ent[8].decode("ascii") == "icon.sys" and len(data) >= 964:
                try:
                    return ps2iconsys.IconSys(data[:964])
                except ps2iconsys.Error:
                    pass
        return None

