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

"""Interface for working with PS2 icons."""

import struct


class Error(Exception):
    """Base for all exceptions specific to this module."""
    pass

class Corrupt(Error):
    """Corrupt icon file."""

    def __init__(self, msg):
        super().__init__(self, "Corrupt icon: " + msg)

class FileTooSmall(Error):
    """Corrupt icon file."""

    def __init__(self):
        super().__init__(self, "Icon file too small.")


_PS2_ICON_MAGIC = 0x010000

_FIXED_POINT_FACTOR = 4096.0


TEXTURE_WIDTH = 128
TEXTURE_HEIGHT = 128

_TEXTURE_SIZE = TEXTURE_WIDTH * TEXTURE_HEIGHT * 2

_icon_hdr_struct = struct.Struct("<IIIII")

_vertex_coords_struct = struct.Struct("<hhhH")
_normal_uv_color_struct = struct.Struct("<hhhHhhBBBB")

_anim_hdr_struct = struct.Struct("<IIfII")
_frame_data_struct = struct.Struct("<IIII")
_frame_key_struct = struct.Struct("<ff")

_texture_compressed_size_struct = struct.Struct("<I")

import ctypes
uint8_t = ctypes.c_uint8
int16_t = ctypes.c_int16


class Icon:
    class Frame:
        class Key:
            def __init__(self):
                self.time = 0.0
                self.value = 0.0
        def __init__(self):
            self.shape_id = 0
            self.keys = []


    def __init__(self, data):
        self.animation_shapes = 0
        self.tex_type = 0
        self.vertex_count = 0
        self.vertex_data = None
        self.normal_uv_data = None
        self.color_data = None
        self.frame_length = 0
        self.anim_speed = 0.0
        self.play_offset = 0
        self.frame_count = 0
        self.texture = None
        self.enable_alpha = False

        length = len(data)
        offset = 0

        offset = self.__load_header(data, length, offset)
        offset = self.__load_vertex_data(data, length, offset)
        offset = self.__load_animation_data(data, length, offset)
        offset = self.__load_texture(data, length, offset)

        if length > offset:
            print("Warning: Icon file larger than expected.")


    def __load_header(self, data, length, offset):
        if length < _icon_hdr_struct.size:
            raise FileTooSmall()

        (magic,
         self.animation_shapes,
         self.tex_type,
         something,
         self.vertex_count) = _icon_hdr_struct.unpack_from(data, offset)

        if magic != _PS2_ICON_MAGIC:
            raise Corrupt("Invalid magic.")

        return offset + _icon_hdr_struct.size


    def __load_vertex_data(self, data, length, offset):
        stride = _vertex_coords_struct.size * self.animation_shapes \
                 + _normal_uv_color_struct.size

        if length < offset + self.vertex_count * stride:
            raise FileTooSmall()

        self.vertex_data = (int16_t * (self.animation_shapes * 3 * self.vertex_count))()
        self.normal_uv_data = (int16_t * (5 * self.vertex_count))()
        self.color_data = (uint8_t * (4 * self.vertex_count))()

        for i in range(self.vertex_count):
            for s in range(self.animation_shapes):
                vertex_offset = (s * self.vertex_count + i) * 3
                (self.vertex_data[vertex_offset],
                 self.vertex_data[vertex_offset+1],
                 self.vertex_data[vertex_offset+2],
                 _) = _vertex_coords_struct.unpack_from(data, offset)
                offset += _vertex_coords_struct.size

            (self.normal_uv_data[i*5],
             self.normal_uv_data[i*5+1],
             self.normal_uv_data[i*5+2],
             _,
             self.normal_uv_data[i*5+3],
             self.normal_uv_data[i*5+4],
             self.color_data[i*4],
             self.color_data[i*4+1],
             self.color_data[i*4+2],
             self.color_data[i*4+3]) = _normal_uv_color_struct.unpack_from(data, offset)

            # This is just a hack to check if every alpha value is 0, which is the case for THPS3 for example.
            # Alpha will then be assumed to be 1 for all vertices when rendering, otherwise nothing will be visible.
            # TODO: There is probably another way to render these icons correctly.
            if self.color_data[i*4+3] > 0:
                self.enable_alpha = True

            offset += _normal_uv_color_struct.size

        return offset


    def __load_animation_data(self, data, length, offset):
        if length < offset + _anim_hdr_struct.size:
            raise FileTooSmall()

        (anim_id_tag,
         self.frame_length,
         self.anim_speed,
         self.play_offset,
         self.frame_count) = _anim_hdr_struct.unpack_from(data, offset)

        offset += _anim_hdr_struct.size

        if anim_id_tag != 0x01:
            raise Corrupt("Invalid ID tag in animation header: {:#x}".format(anim_id_tag))

        self.frames = []
        for i in range(self.frame_count):
            if length < offset + _frame_data_struct.size:
                raise FileTooSmall()

            frame = self.Frame()
            (frame.shape_id,
             key_count,
             _,
             _) = _frame_data_struct.unpack_from(data, offset)

            key_count -= 1

            offset += _frame_data_struct.size

            for k in range(key_count):
                if length < offset + _frame_key_struct.size:
                    raise FileTooSmall()

                key = self.Frame.Key()
                (key.time,
                 key.value) = _frame_key_struct.unpack_from(data, offset)
                frame.keys.append(key)

                offset += _frame_key_struct.size

            self.frames.append(frame)

        return offset


    def __load_texture(self, data, length, offset):
        # No textures to load. This may be the case when vertices are colored without a texture.
        if offset == length:
            self.texture = [0xFFFF]
            return offset
        
        if self.tex_type == 0x7:
            return self.__load_texture_uncompressed(data, length, offset)
        else:
            return self.__load_texture_compressed(data, length, offset)


    def __load_texture_uncompressed(self, data, length, offset):
        if length < offset + _TEXTURE_SIZE:
            raise FileTooSmall()

        self.texture = data[offset:(offset + _TEXTURE_SIZE)]

        return offset + _TEXTURE_SIZE


    def __load_texture_compressed(self, data, length, offset):
        if length < offset + 4:
            raise FileTooSmall()

        compressed_size = _texture_compressed_size_struct.unpack_from(data, offset)[0]
        offset += 4

        if length < offset + compressed_size:
            raise FileTooSmall()

        if compressed_size % 2 != 0:
            raise Corrupt("Compressed data size is odd.")

        texture_buf = bytearray(_TEXTURE_SIZE)

        tex_offset = 0
        rle_offset = 0

        while rle_offset < compressed_size:
            rle_code = int(data[offset + rle_offset]) | (int(data[offset + rle_offset + 1]) << 8)
            rle_offset += 2

            if rle_code & 0xff00 == 0xff00: # use the next (0xffff - rle_code) * 2 bytes as they are
                sublength = (0x10000 - rle_code) * 2
                if compressed_size < rle_offset + sublength:
                    raise Corrupt("Compressed data is too short.")
                if tex_offset + sublength > _TEXTURE_SIZE:
                    raise Corrupt("Decompressed data exceeds texture size.")

                for i in range(sublength):
                    texture_buf[tex_offset] = data[offset + rle_offset]
                    tex_offset += 1
                    rle_offset += 1

            else: # repeat next 2 bytes rle_code times
                rep = rle_code
                if compressed_size < rle_offset + 2:
                    raise Corrupt("Compressed data is too short.")
                if tex_offset + rep * 2 > _TEXTURE_SIZE:
                    raise Corrupt("Decompressed data exceeds texture size.")

                subdata = data[(offset + rle_offset):(offset + rle_offset + 2)]
                rle_offset += 2

                for i in range(rep):
                    texture_buf[tex_offset] = subdata[0]
                    texture_buf[tex_offset+1] = subdata[1]
                    tex_offset += 2

        assert rle_offset == compressed_size

        self.texture = bytes(texture_buf)

        return offset + compressed_size
