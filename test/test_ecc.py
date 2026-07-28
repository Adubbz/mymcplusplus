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
from mymcplusplus import ps2mc_ecc
import base64


_data = [0x36, 0x76, 0x11, 0x24, 0xb1, 0xd2, 0xd2, 0x81, 0xd5, 0x47, 0x15, 0x41, 0xc9, 0x47, 0xb7, 0xf2,
         0x6b, 0x00, 0x25, 0x34, 0x48, 0x1b, 0xbc, 0xcd, 0x07, 0x28, 0x9a, 0x88, 0x9c, 0xd3, 0x69, 0xda,
         0x25, 0xa8, 0x39, 0x62, 0xd4, 0x8c, 0xc0, 0x25, 0x43, 0x04, 0x65, 0x22, 0xa8, 0xef, 0x44, 0x5f,
         0x03, 0x91, 0xda, 0x23, 0x8c, 0x17, 0x24, 0xf5, 0x14, 0xf0, 0xd6, 0x5a, 0xc2, 0xe0, 0x5a, 0xb6,
         0xbe, 0x6b, 0x4d, 0xb1, 0x2e, 0x20, 0x0d, 0x8a, 0x35, 0x19, 0x28, 0x7a, 0xc1, 0x8e, 0x3f, 0x1d,
         0x87, 0xa9, 0x53, 0x96, 0x13, 0xe6, 0x4c, 0x16, 0x1b, 0x49, 0x0a, 0xdb, 0x88, 0xc5, 0xe6, 0xb1,
         0x44, 0xdc, 0x35, 0xbd, 0x92, 0xcf, 0x53, 0x91, 0x81, 0xed, 0x70, 0xf0, 0xc0, 0xab, 0x41, 0xa8,
         0xdd, 0xf2, 0x7d, 0xa4, 0x83, 0xa3, 0xb0, 0x4f, 0x77, 0xe0, 0x80, 0xba, 0xca, 0x5e, 0xf2, 0x01]

_ecc = [97, 19, 108]


def test_ecc_calculate_array():
    s = array.array('B', _data)
    assert ps2mc_ecc.ecc_calculate(s) == _ecc


def test_ecc_calculate_bytes():
    s = bytes(_data)
    assert ps2mc_ecc.ecc_calculate(s) == _ecc


def test_ecc_check_ok():
    s = list(_data)
    s = array.array('B', s)

    ecc = list(_ecc)

    res = ps2mc_ecc.ecc_check(s, ecc)

    assert res == ps2mc_ecc.ECC_CHECK_OK
    assert s.tobytes() == bytes(_data)
    assert ecc == _ecc


def test_ecc_check_correct_data():
    s = list(_data)
    s[42] ^= 1
    s = array.array('B', s)

    ecc = list(_ecc)

    res = ps2mc_ecc.ecc_check(s, ecc)

    assert res == ps2mc_ecc.ECC_CHECK_CORRECTED
    assert s.tobytes() == bytes(_data)
    assert ecc == _ecc


def test_ecc_check_correct_ecc():
    s = list(_data)
    s = array.array('B', s)

    ecc = list(_ecc)
    ecc[0] ^= 1

    res = ps2mc_ecc.ecc_check(s, ecc)

    assert res == ps2mc_ecc.ECC_CHECK_CORRECTED
    assert s.tobytes() == bytes(_data)
    assert ecc == _ecc


def test_ecc_check_fail():
    s = list(_data)
    s[42] ^= 3
    s = array.array('B', s)

    ecc = list(_ecc)

    res = ps2mc_ecc.ecc_check(s, ecc)

    assert res == ps2mc_ecc.ECC_CHECK_FAILED
