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

def read_fixed(f, n):
    """Read a string of a fixed length from a file."""

    s = f.read(n)
    if len(s) != n:
        raise ps2save.Eof(f)
    return s


def read_long_string(f):
    """Read a string prefixed with a 32-bit length from a file."""

    length = struct.unpack("<L", read_fixed(f, 4))[0]
    return read_fixed(f, length)


def read_struct(f, s):
    return s.unpack(read_fixed(f, s.size))
