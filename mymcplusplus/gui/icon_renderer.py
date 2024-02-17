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

from ctypes import c_void_p
import time
from OpenGL.GL import *
from .linalg import Matrix4x4, Vector3

from .. import ps2icon


_LIGHTS_COUNT = 3

_glsl_icon_vert = b"""
#version 150

uniform mat4 mvp_matrix_uni;
uniform mat4 transform_matrix_uni;

in vec3 vertex_attr;
in vec3 normal_attr;
in vec2 uv_attr;
in vec4 color_attr;

out vec4 color_var;
out vec2 uv_var;
out vec3 normal_var;

void main()
{
    vec3 pos = (vertex_attr / 4096.0) * vec3(1.0, -1.0, -1.0);
    pos = (transform_matrix_uni * vec4(pos, 1.0)).xyz;
    
    color_var = color_attr;
    
    uv_var = uv_attr / 4096.0;
    
    vec3 normal = normalize(normal_attr / 4096.0) * vec3(1.0, -1.0, -1.0);
    normal = mat3(transform_matrix_uni) * normal;
    normal_var = normal;
    
    gl_Position = mvp_matrix_uni * vec4(pos, 1.0);
}
"""

_glsl_icon_frag = b"""
#version 150

#define LIGHTS_COUNT """ + str(_LIGHTS_COUNT).encode("ascii") + b"""

uniform sampler2D texture_uni;

uniform vec3 light_dir_uni[LIGHTS_COUNT];
uniform vec3 light_color_uni[LIGHTS_COUNT];
uniform vec3 ambient_light_color_uni;

in vec4 color_var;
in vec2 uv_var;
in vec3 normal_var;

out vec4 color_out;

void main()
{
    vec3 normal = normalize(normal_var);

    float alpha = color_var.a;
    
    vec3 tex_color = texture(texture_uni, uv_var).rgb;
    vec3 base_color = color_var.rgb * tex_color;
    
    vec3 color = base_color * ambient_light_color_uni;
    
    for(int i=0; i<LIGHTS_COUNT; i++)
    {
        float lambert = dot(light_dir_uni[i], normal);
        lambert = max(lambert, 0.0);
        color += lambert * light_color_uni[i] * base_color;
    }
    
    color_out = vec4(color, alpha);
}
"""


_ATTRIB_ICON_VERTEX =    0
_ATTRIB_ICON_NORMAL =    1
_ATTRIB_ICON_UV =        2
_ATTRIB_ICON_COLOR =     3

_TEX_UNIT_ICON =         0


_glsl_background_vert = b"""
#version 150

in vec2 vertex_attr;
in vec4 color_attr;

out vec4 color_var;

void main()
{
    color_var = color_attr;
    gl_Position = vec4(vertex_attr, 0.0, 1.0);
}
"""

_glsl_background_frag = b"""
#version 150

in vec4 color_var;

out vec4 color_out;

void main()
{
    color_out = color_var;
}
"""


_ATTRIB_BACKGROUND_VERTEX = 0
_ATTRIB_BACKGROUND_COLOR =  1


class IconRenderer:
    """Render a save file's 3D icon with OpenGL."""

    class LightingConfig:
        def __init__(self, icon_sys = None,
                     light_dirs = ((0.0, 0.0, 0.0),
                                   (0.0, 0.0, 0.0),
                                   (0.0, 0.0, 0.0)),
                     light_colors = ((0.0, 0.0, 0.0),
                                     (0.0, 0.0, 0.0),
                                     (0.0, 0.0, 0.0)),
                     ambient_light_color = (0.0, 0.0, 0.0)):

            if icon_sys is not None:
                self.light_dirs = tuple([d[0:3] for d in icon_sys.light_dirs[0:]])
                self.light_colors = tuple([c[0:3] for c in icon_sys.light_colors])
                self.ambient_light_color = icon_sys.ambient_light_color[0:3]
            else:
                self.light_dirs = light_dirs
                self.light_colors = light_colors
                self.ambient_light_color = ambient_light_color


            light_dir_vectors = [Vector3(v[0], v[1], v[2]) for v in self.light_dirs]
            light_dir_vectors = [v.normalized if v.length_sq > 0.0001 else v for v in light_dir_vectors]

            self.light_dirs_data = (GLfloat * (3 * _LIGHTS_COUNT))(*[f for v in light_dir_vectors for f in (v.x, v.y, v.z)])
            self.light_colors_data = (GLfloat * (3 * _LIGHTS_COUNT))(*[f for t in self.light_colors for f in t])
            self.ambient_color_data = (GLfloat * 3)(*self.ambient_light_color)


    def __init__(self, gl_context):
        self.failed = False

        self.context = gl_context

        self._icon = None
        self._icon_sys = None
        self._default_lighting_config = self.LightingConfig()
        self.lighting_config = None
        self._icon_uploaded = False

        self.camera_rotation = (0.0, 0.0)
        self.camera_distance = 5.0
        self.camera_offset = Vector3(0.0, 0.0, 0.0)

        self.background_color = (0.0, 0.0, 0.0)

        self._program = None
        self._vertex_vbo = None
        self._vertex_data = None
        self._normal_uv_vbo = None
        self._color_vbo = None
        self._vao = None
        self._texture = None

        self._background_program = None
        self._background_vertex_vbo = None
        self._background_color_vbo = None
        self._background_vao = None

        self._mvp_matrix_uni = -1
        self._transform_matrix_uni = -1
        self._light_dir_uni = -1
        self._light_color_uni = -1
        self._ambient_light_color_uni = -1

        self._gl_initialized = False


    def _initialize_gl(self):
        self._gl_initialized = True

        shader_vert = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(shader_vert, [_glsl_icon_vert])
        glCompileShader(shader_vert)

        shader_frag = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(shader_frag, [_glsl_icon_frag])
        glCompileShader(shader_frag)

        self._program = glCreateProgram()
        glBindAttribLocation(self._program, _ATTRIB_ICON_VERTEX, "vertex_attr")
        glBindAttribLocation(self._program, _ATTRIB_ICON_NORMAL, "normal_attr")
        glBindAttribLocation(self._program, _ATTRIB_ICON_UV, "uv_attr")
        glBindAttribLocation(self._program, _ATTRIB_ICON_COLOR, "color_attr")
        glAttachShader(self._program, shader_vert)
        glAttachShader(self._program, shader_frag)
        glLinkProgram(self._program)

        log = glGetProgramInfoLog(self._program)
        if log:
            print("Failed to compile shader:")
            print(log.decode("utf-8"))
            self.failed = True
            return

        shader_vert = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(shader_vert, [_glsl_background_vert])
        glCompileShader(shader_vert)

        shader_frag = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(shader_frag, [_glsl_background_frag])
        glCompileShader(shader_frag)

        self._background_program = glCreateProgram()
        glBindAttribLocation(self._background_program, _ATTRIB_BACKGROUND_VERTEX, "vertex_attr")
        glBindAttribLocation(self._background_program, _ATTRIB_BACKGROUND_COLOR, "color_attr")
        glAttachShader(self._background_program, shader_vert)
        glAttachShader(self._background_program, shader_frag)
        glLinkProgram(self._background_program)

        log = glGetProgramInfoLog(self._program)
        if log:
            print("Failed to compile shader:")
            print(log.decode("utf-8"))
            self.failed = True
            return

        self._mvp_matrix_uni = glGetUniformLocation(self._program, "mvp_matrix_uni")
        self._transform_matrix_uni = glGetUniformLocation(self._program, "transform_matrix_uni")
        self._light_dir_uni = glGetUniformLocation(self._program, "light_dir_uni")
        self._light_color_uni = glGetUniformLocation(self._program, "light_color_uni")
        self._ambient_light_color_uni = glGetUniformLocation(self._program, "ambient_light_color_uni")

        texture_uni = glGetUniformLocation(self._program, "texture_uni")
        glUseProgram(self._program)
        glUniform1i(texture_uni, _TEX_UNIT_ICON)

        self._vao = glGenVertexArrays(1)
        glBindVertexArray(self._vao)

        (self._vertex_vbo, self._normal_uv_vbo, self._color_vbo) = glGenBuffers(3)

        glBindBuffer(GL_ARRAY_BUFFER, self._vertex_vbo)
        glVertexAttribPointer(_ATTRIB_ICON_VERTEX, 3, GL_SHORT, GL_FALSE, 0, c_void_p(0))

        glBindBuffer(GL_ARRAY_BUFFER, self._normal_uv_vbo)
        glVertexAttribPointer(_ATTRIB_ICON_NORMAL, 3, GL_SHORT, GL_FALSE, 5 * 2, c_void_p(0))
        glVertexAttribPointer(_ATTRIB_ICON_UV, 2, GL_SHORT, GL_FALSE, 5 * 2, c_void_p(3 * 2))

        glBindBuffer(GL_ARRAY_BUFFER, self._color_vbo)
        glVertexAttribPointer(_ATTRIB_ICON_COLOR, 4, GL_UNSIGNED_BYTE, GL_TRUE, 0, c_void_p(0))

        glEnableVertexAttribArray(_ATTRIB_ICON_VERTEX)
        glEnableVertexAttribArray(_ATTRIB_ICON_NORMAL)
        glEnableVertexAttribArray(_ATTRIB_ICON_UV)
        glEnableVertexAttribArray(_ATTRIB_ICON_COLOR)

        self._texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self._texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB5_A1, ps2icon.TEXTURE_WIDTH, ps2icon.TEXTURE_HEIGHT, 0, GL_RGBA, GL_UNSIGNED_SHORT_1_5_5_5_REV, c_void_p(0))

        self._background_vao = glGenVertexArrays(1)
        glBindVertexArray(self._background_vao)

        (self._background_vertex_vbo, self._background_color_vbo) = glGenBuffers(2)

        glBindBuffer(GL_ARRAY_BUFFER, self._background_vertex_vbo)
        background_vertex_data = [
            -1.0, 1.0,
            -1.0, -1.0,
            1.0, 1.0,
            1.0, -1.0
        ]
        glBufferData(GL_ARRAY_BUFFER, 8*4, (GLfloat * 8)(*background_vertex_data), GL_STATIC_DRAW)
        glVertexAttribPointer(_ATTRIB_BACKGROUND_VERTEX, 2, GL_FLOAT, GL_FALSE, 0, c_void_p(0))

        glBindBuffer(GL_ARRAY_BUFFER, self._background_color_vbo)
        glBufferData(GL_ARRAY_BUFFER, 4*4, c_void_p(0), GL_DYNAMIC_DRAW)
        glVertexAttribPointer(_ATTRIB_BACKGROUND_COLOR, 4, GL_UNSIGNED_BYTE, GL_TRUE, 0, c_void_p(0))

        glEnableVertexAttribArray(_ATTRIB_BACKGROUND_VERTEX)
        glEnableVertexAttribArray(_ATTRIB_BACKGROUND_COLOR)


    def calculate_camera(self):
        camera_pos = Vector3(0.0, 0.0, 1.0)
        camera_pos = camera_pos * self.camera_distance

        return camera_pos, Vector3(0.0, 0.0, 0.0), Vector3(0.0, 1.0, 0.0)


    def _write_animated_vertices(self, anim_time, vertex_data):
        duration = float(self._icon.frame_length)
        if duration > 0.0:
            anim_time = ((time.time() - anim_time) * 8.0) % duration
        else:
            anim_time = 0.0

        shape_values = {}

        for frame in self._icon.frames:
            keys = frame.keys
            if frame.shape_id == 0:
                k = ps2icon.Icon.Frame.Key()
                k.time = 0.0
                k.value = 1.0
                keys.append(k)

            last = None
            last_time = 0.0
            next = None
            next_time = 0.0

            for key in keys:
                t = key.time if key.time <= anim_time else key.time - duration
                if last is None or t > last_time:
                    last = key
                    last_time = t

                t = key.time if key.time >= anim_time else key.time + duration
                if next is None or t < next_time:
                    next = key
                    next_time = t

            if next_time > last_time:
                progress = (anim_time - last_time) / (next_time - last_time)
            else:
                progress = 0.0

            if last is not None and next is not None:
                shape_values[frame.shape_id] = (1.0 - progress) * last.value + progress * next.value

        if shape_values == {}:
            shape_values = {0: 1.0}

        sum = 0.0
        for shape_id, value in shape_values.items():
            sum += value

        if sum <= 0.0:
            shape_values = {0: 1.0}
        else:
            for shape_id in shape_values:
                shape_values[shape_id] /= sum

        for i in range(3 * self._icon.vertex_count):
            acc = 0.0
            for shape_id, value in shape_values.items():
                acc += value * self._icon.vertex_data[shape_id * 3 * self._icon.vertex_count + i]
            vertex_data[i] = int(acc)


    def _update_vertex_vbo(self, anim_time):
        if anim_time is not None:
            self._write_animated_vertices(anim_time, self._vertex_data)
            vertex_data = self._vertex_data
        else:
            vertex_data = self._icon.vertex_data

        glBindBuffer(GL_ARRAY_BUFFER, self._vertex_vbo)
        glBufferData(GL_ARRAY_BUFFER, self._icon.vertex_count * 3 * 2, vertex_data, GL_DYNAMIC_DRAW)


    def _upload_icon(self):
        if self._icon is None or self._icon_uploaded:
            return

        glBindBuffer(GL_ARRAY_BUFFER, self._vertex_vbo)
        glBufferData(GL_ARRAY_BUFFER,
                     self._icon.vertex_count * 3 * 2,
                     c_void_p(0),
                     GL_DYNAMIC_DRAW)

        self._vertex_data = (GLshort * (self._icon.vertex_count * 3))()

        glBindBuffer(GL_ARRAY_BUFFER, self._normal_uv_vbo)
        glBufferData(GL_ARRAY_BUFFER,
                     self._icon.vertex_count * 5 * 2,
                     self._icon.normal_uv_data,
                     GL_STATIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, self._color_vbo)
        glBufferData(GL_ARRAY_BUFFER,
                     self._icon.vertex_count * 4,
                     self._icon.color_data,
                     GL_STATIC_DRAW)

        glBindTexture(GL_TEXTURE_2D, self._texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB5_A1, ps2icon.TEXTURE_WIDTH, ps2icon.TEXTURE_HEIGHT, 0, GL_RGBA, GL_UNSIGNED_SHORT_1_5_5_5_REV, self._icon.texture)
        glGenerateMipmap(GL_TEXTURE_2D)

        bg_colors = self._icon_sys.bg_colors
        bg_alpha = self._icon_sys.background_transparency
        colors = [int((c / 0x80) * 255) for c in [
            *bg_colors[0][0:3], bg_alpha,
            *bg_colors[2][0:3], bg_alpha,
            *bg_colors[1][0:3], bg_alpha,
            *bg_colors[3][0:3], bg_alpha]]

        color_data = (GLubyte * (4*4))(*colors)
        glBindBuffer(GL_ARRAY_BUFFER, self._background_color_vbo)
        glBufferData(GL_ARRAY_BUFFER, 4*4, color_data, GL_DYNAMIC_DRAW)

        self._icon_uploaded = True


    def paint(self, canvas, animation_time):
        self.context.SetCurrent(canvas)

        if not self._gl_initialized:
            self._initialize_gl()

        if self.failed:
            return

        self._upload_icon()

        size = canvas.Size

        glViewport(0, 0, size.Width, size.Height)

        if self.background_color is not None:
            glClearColor(*self.background_color, 1.0)
        else:
            glClearColor(0.0, 0.0, 0.0, 1.0)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if self.background_color is None and self._icon is not None:
            glUseProgram(self._background_program)
            glDisable(GL_DEPTH_TEST)
            glDepthMask(GL_FALSE)

            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

            glBindVertexArray(self._background_vao)
            glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

        if self._icon is not None:
            glUseProgram(self._program)

            glEnable(GL_DEPTH_TEST)
            glDepthMask(GL_TRUE)

            glActiveTexture(GL_TEXTURE0 + _TEX_UNIT_ICON)
            glBindTexture(GL_TEXTURE_2D, self._texture)

            modelview_matrix = Matrix4x4.look_at(*self.calculate_camera())
            aspect = 1.0
            if size.Height > 0 and size.Width > 0:
                aspect = float(size.Width) / float(size.Height)
            projection_matrix = Matrix4x4.perspective(80.0, aspect, 0.1, 500.0)
            glUniformMatrix4fv(self._mvp_matrix_uni, 1, GL_FALSE, (projection_matrix * modelview_matrix).ctypes_array)

            transform_matrix = Matrix4x4.translate(self.camera_offset * -1.0 + Vector3(0.0, 2.5, 0.0)) \
                               * Matrix4x4.rotate_x(self.camera_rotation[1]) \
                               * Matrix4x4.rotate_y(self.camera_rotation[0]) \
                               * Matrix4x4.translate(Vector3(0.0, -2.5, 0.0))
            glUniformMatrix4fv(self._transform_matrix_uni, 1, GL_FALSE, transform_matrix.ctypes_array)

            lighting_config = self.lighting_config if self.lighting_config is not None else self._default_lighting_config
            glUniform3fv(self._light_dir_uni, 3, lighting_config.light_dirs_data)
            glUniform3fv(self._light_color_uni, 3, lighting_config.light_colors_data)
            glUniform3fv(self._ambient_light_color_uni, 1, lighting_config.ambient_color_data)

            glEnable(GL_CULL_FACE)

            if self._icon.enable_alpha:
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            else:
                glDisable(GL_BLEND)

            self._update_vertex_vbo(animation_time)

            glBindVertexArray(self._vao)
            glDrawArrays(GL_TRIANGLES, 0, self._icon.vertex_count)

        canvas.SwapBuffers()


    def set_icon(self, icon_sys, icon):
        if self.failed:
            return

        self._icon = icon
        self._icon_sys = icon_sys

        self._default_lighting_config = self.LightingConfig(icon_sys=icon_sys)

        self._icon_uploaded = False
