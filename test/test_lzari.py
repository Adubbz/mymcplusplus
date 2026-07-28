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
from mymcplusplus.save import lzari


def bits_to_str(bits):
    return "".join([{0: "0", 1: "1"}[b] for b in bits])


def str_to_bits(s):
    return array.array("B", [{"0": 0, "1": 1}[c] for c in s])


def test_string_to_bit_array():
    bits = lzari.string_to_bit_array(b"Bufudyne\xE2\x9D\x84")
    assert bits_to_str(bits) == "0100001001110101011001100111010101100100011110010110111001100101111000101001110110000100"


def test_bit_array_to_string():
    bits = str_to_bits("0100000101100111011010010110010001111001011011100110010111110000100111111001010010100101")
    s = lzari.bit_array_to_string(bits)
    assert s == b"Agidyne\xf0\x9f\x94\xa5"


def test_bit_array_to_string_pad():
    bits = str_to_bits("00110100"
                       "00110010"
                       "010")
    s = lzari.bit_array_to_string(bits)
    assert s == b"42@"


def test_encode():
    s = b"You'll never see it coming."
    compressed = lzari.encode(s)
    assert compressed == b"\xb7%\xf0\x18\xb2\x123Z\xa4\xe9\xfb3\x892\x0e\xb1nE~\xf6\xdb\x80:\xa6\x92\x11\xf8"


def test_decode():
    original_s = b"\xF0\x9F\x8E\xB5 Every day's great at your Junes \xF0\x9F\x8E\xB5"
    compressed = b";\xeaJrm\xe8\xbe\xd0\xc14(:\xa9\xb4\xd4\x8b\xde\tN\xb7-\xb1D\xac\x8e\xeb{\xa5$R>\xc4\x1b\xb8\xc2:\xb2"
    s = lzari.decode(compressed, len(original_s))
    assert s == original_s


def test_encode_save():
    from data_lzari import max_data_raw as data
    from data_lzari import max_data_compressed as compressed_correct
    compressed = lzari.encode(data)
    assert len(compressed) == 3964
    assert compressed == compressed_correct
