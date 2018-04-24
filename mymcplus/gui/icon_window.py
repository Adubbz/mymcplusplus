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

import wx
from wx import glcanvas

from OpenGL.GL import *

from .. import ps2icon


lighting_none = {"lighting": False,
         "vertex_diffuse": False,
         "alt_lighting": False,
         "light_dirs": [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
         "light_colours": [[0, 0, 0, 0], [0, 0, 0, 0],
                   [0, 0, 0, 0]],
         "ambient": [0, 0, 0, 0]}

lighting_diffuse = {"lighting": False,
            "vertex_diffuse": True,
            "alt_lighting": False,
            "light_dirs": [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
            "light_colours": [[0, 0, 0, 0], [0, 0, 0, 0],
                      [0, 0, 0, 0]],
            "ambient": [0, 0, 0, 0]}

lighting_icon = {"lighting": True,
         "vertex_diffuse": True,
         "alt_lighting": False,
         "light_dirs": [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
         "light_colours": [[0, 0, 0, 0], [0, 0, 0, 0],
                   [0, 0, 0, 0]],
         "ambient": [0, 0, 0, 0]}

lighting_alternate = {"lighting": True,
              "vertex_diffuse": True,
              "alt_lighting": True,
              "light_dirs": [[1, -1, 2, 0],
                     [-1, 1, -2, 0],
                     [0, 1, 0, 0]],
              "light_colours": [[1, 1, 1, 1],
                    [1, 1, 1, 1],
                    [0.7, 0.7, 0.7, 1]],
              "ambient": [0.5, 0.5, 0.5, 1]}

lighting_alternate2 = {"lighting": True,
               "vertex_diffuse": False,
               "alt_lighting": True,
               "light_dirs": [[1, -1, 2, 0],
                      [-1, 1, -2, 0],
                      [0, 4, 1, 0]],
               "light_colours": [[0.7, 0.7, 0.7, 1],
                     [0.7, 0.7, 0.7, 1],
                     [0.2, 0.2, 0.2, 1]],
               "ambient": [0.3, 0.3, 0.3, 1]}

camera_default = [0, 4, -8]
camera_high = [0, 7, -6]
camera_near = [0, 3, -6]
camera_flat = [0, 2, -7.5]


_glsl_vert = b"""
#version 150

in vec3 vertex_attr;

void main()
{
    gl_Position = vec4(vertex_attr, 1.0);
}
"""

_glsl_frag = b"""
#version 150

out vec4 color_out;

void main()
{
    color_out = vec4(0.0, 1.0, 0.0, 1.0);
}
"""

_ATTRIB_VERTEX_POS = 0


class IconWindow(wx.Window):
    """Displays a save file's 3D icon."""

    ID_CMD_ANIMATE = 201
    ID_CMD_LIGHT_NONE = 202
    ID_CMD_LIGHT_ICON = 203
    ID_CMD_LIGHT_ALT1 = 204
    ID_CMD_LIGHT_ALT2 = 205
    ID_CMD_CAMERA_FLAT = 206
    ID_CMD_CAMERA_DEFAULT = 207
    ID_CMD_CAMERA_NEAR = 209
    ID_CMD_CAMERA_HIGH = 210

    light_options = {ID_CMD_LIGHT_NONE: lighting_none,
                     ID_CMD_LIGHT_ICON: lighting_icon,
                     ID_CMD_LIGHT_ALT1: lighting_alternate,
                     ID_CMD_LIGHT_ALT2: lighting_alternate2}

    camera_options = {ID_CMD_CAMERA_FLAT: camera_flat,
                      ID_CMD_CAMERA_DEFAULT: camera_default,
                      ID_CMD_CAMERA_NEAR: camera_near,
                      ID_CMD_CAMERA_HIGH: camera_high}

    def append_menu_options(self, win, menu):
        menu.AppendCheckItem(IconWindow.ID_CMD_ANIMATE, "Animate Icons")
        menu.AppendSeparator()
        menu.AppendRadioItem(IconWindow.ID_CMD_LIGHT_NONE, "Lighting Off")
        menu.AppendRadioItem(IconWindow.ID_CMD_LIGHT_ICON, "Icon Lighting")
        menu.AppendRadioItem(IconWindow.ID_CMD_LIGHT_ALT1, "Alternate Lighting")
        menu.AppendRadioItem(IconWindow.ID_CMD_LIGHT_ALT2, "Alternate Lighting 2")
        menu.AppendSeparator()
        menu.AppendRadioItem(IconWindow.ID_CMD_CAMERA_FLAT, "Camera Flat")
        menu.AppendRadioItem(IconWindow.ID_CMD_CAMERA_DEFAULT, "Camera Default")
        menu.AppendRadioItem(IconWindow.ID_CMD_CAMERA_NEAR, "Camera Near")
        menu.AppendRadioItem(IconWindow.ID_CMD_CAMERA_HIGH, "Camera High")

        win.Bind(wx.EVT_MENU, self.evt_menu_animate, id=IconWindow.ID_CMD_ANIMATE)
        win.Bind(wx.EVT_MENU, self.evt_menu_light, id=IconWindow.ID_CMD_LIGHT_NONE)
        win.Bind(wx.EVT_MENU, self.evt_menu_light, id=IconWindow.ID_CMD_LIGHT_ICON)
        win.Bind(wx.EVT_MENU, self.evt_menu_light, id=IconWindow.ID_CMD_LIGHT_ALT1)
        win.Bind(wx.EVT_MENU, self.evt_menu_light, id=IconWindow.ID_CMD_LIGHT_ALT2)

        win.Bind(wx.EVT_MENU, self.evt_menu_camera, id=IconWindow.ID_CMD_CAMERA_FLAT)
        win.Bind(wx.EVT_MENU, self.evt_menu_camera, id=IconWindow.ID_CMD_CAMERA_DEFAULT)
        win.Bind(wx.EVT_MENU, self.evt_menu_camera, id=IconWindow.ID_CMD_CAMERA_NEAR)
        win.Bind(wx.EVT_MENU, self.evt_menu_camera, id=IconWindow.ID_CMD_CAMERA_HIGH)

    def __init__(self, parent, focus):
        super().__init__(parent)
        self.failed = False

        attrib_list = [
            glcanvas.WX_GL_MAJOR_VERSION, 3,
            glcanvas.WX_GL_MINOR_VERSION, 2,
            glcanvas.WX_GL_CORE_PROFILE,
            glcanvas.WX_GL_RGBA,
            glcanvas.WX_GL_DOUBLEBUFFER,
            glcanvas.WX_GL_DEPTH_SIZE, 24
        ]

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.canvas = glcanvas.GLCanvas(self, attribList=attrib_list)
        self.context = glcanvas.GLContext(self.canvas)

        self.icon = None

        self.program = None
        self.vbo = None
        self.vao = None
        self.gl_initialized = False

        self.canvas.Bind(wx.EVT_PAINT, self.paint)

        self.sizer.Add(self.canvas, wx.EXPAND, wx.EXPAND)
        self.SetSizer(self.sizer)

        #self.config = config = mymcsup.icon_config()
        #config.animate = True

        self.menu = wx.Menu()
        self.append_menu_options(self, self.menu)
        self.set_lighting(self.ID_CMD_LIGHT_ALT2)
        self.set_camera(self.ID_CMD_CAMERA_DEFAULT)

        self.Bind(wx.EVT_CONTEXT_MENU, self.evt_context_menu)


    def initialize_gl(self):
        self.gl_initialized = True

        shader_vert = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(shader_vert, [_glsl_vert])
        glCompileShader(shader_vert)

        shader_frag = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(shader_frag, [_glsl_frag])
        glCompileShader(shader_frag)

        self.program = glCreateProgram()
        glAttachShader(self.program, shader_vert)
        glAttachShader(self.program, shader_frag)
        glLinkProgram(self.program)

        log = glGetProgramInfoLog(self.program)
        if log:
            print("Failed to compile shader:")
            print(log.decode("utf-8"))
            self.failed = True
            return

        glBindAttribLocation(self.program, _ATTRIB_VERTEX_POS, "vertex_in")


        data = [
            0.0, 0.5, 0.5,
            -0.5, -0.5, 0.5,
            0.5, -0.5, 0.5
        ]

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, len(data) * 4, (GLfloat * len(data))(*data), GL_STATIC_DRAW)
        glVertexAttribPointer(_ATTRIB_VERTEX_POS, 3, GL_FLOAT, GL_FALSE, 0, None)

        glEnableVertexAttribArray(_ATTRIB_VERTEX_POS)


    def paint(self, _):
        self.context.SetCurrent(self.canvas)

        if not self.gl_initialized:
            self.initialize_gl()

        glViewport(0, 0, self.canvas.Size.Width, self.canvas.Size.Height)

        glClearColor(1.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glUseProgram(self.program)

        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, 3)

        self.canvas.SwapBuffers()

    def update_menu(self, menu):
        """Update the content menu according to the current config."""

        menu.Check(IconWindow.ID_CMD_ANIMATE, False)#self.config.animate)
        menu.Check(self.lighting_id, True)
        menu.Check(self.camera_id, True)

    def load_icon(self, icon_sys_data, icon_data):
        """Pass the raw icon data to the support DLL for display."""

        if self.failed:
            return

        if icon_data is None:
            self.icon = None
        else:
            self.icon = ps2icon.Icon(icon_data) # TODO: catch exceptions and set self.icon to None


    def _set_lighting(self, lighting, vertex_diffuse, alt_lighting, light_dirs, light_colours, ambient):
        #if self.failed:
        #    return
        #config = self.config
        #config.lighting = lighting
        #config.vertex_diffuse = vertex_diffuse
        #config.alt_lighting = alt_lighting
        #config.light_dirs = mkvec4arr3(light_dirs)
        #config.light_colours = mkvec4arr3(light_colours)
        #config.ambient = D3DXVECTOR4(*ambient)
        #if mymcsup.set_config(config) == -1:
        #    self.failed = True
        pass

    def set_lighting(self, id):
        self.lighting_id = id
        self._set_lighting(**self.light_options[id])

    def set_animate(self, animate):
        #if self.failed:
        #    return
        #self.config.animate = animate
        #if mymcsup.set_config(self.config) == -1:
        #    self.failed = True
        pass

    def _set_camera(self, camera):
        #if self.failed:
        #    return
        #self.config.camera = mymcsup.D3DXVECTOR3(*camera)
        #if mymcsup.set_config(self.config) == -1:
        #    self.failed = True
        pass

    def set_camera(self, id):
        self.camera_id = id
        self._set_camera(self.camera_options[id])

    def evt_context_menu(self, event):
        self.update_menu(self.menu)
        self.PopupMenu(self.menu)

    def evt_menu_animate(self, event):
        #self.set_animate(not self.config.animate)
        pass

    def evt_menu_light(self, event):
        self.set_lighting(event.GetId())

    def evt_menu_camera(self, event):
        self.set_camera(event.GetId())