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

import io
import wx
import struct

from . import resources

def single_title(title):
    """Convert the two parts of an icon.sys title into one string."""

    title = title[0] + " " + title[1]
    return " ".join(title.split())

def _get_icon_resource_as_images(name):
    ico = resources.resources[name]
    images = []
    f = io.BytesIO(ico)
    count = struct.unpack("<HHH", ico[0:6])[2]
    # count = wx.Image_GetImageCount(f, wx.BITMAP_TYPE_ICO)
    for i in range(count):
        # f.seek(0)
        images.append(wx.Image(f, wx.BITMAP_TYPE_ICO, i))
    return images

def _get_png_resource(name):
    data = resources.resources[name]
    return wx.Image(io.BytesIO(data), wx.BITMAP_TYPE_PNG)

def get_icon_resource(name):
    """Convert a Window ICO contained in a string to an IconBundle."""

    bundle = wx.IconBundle()
    for img in _get_icon_resource_as_images(name):
        bmp = wx.Bitmap(img)
        icon = wx.Icon(bmp)
        bundle.AddIcon(icon)
    return bundle

def get_icon_resource_bmp(name, size):
    """Get an icon resource as a Bitmap.

    Tries to find the closest matching size if no exact match exists."""

    best = None
    best_size = (0, 0)
    for img in _get_icon_resource_as_images(name):
        sz = (img.GetWidth(), img.GetHeight())
        if sz == size:
            return wx.Bitmap(img)
        if sz[0] >= size[0] and sz[1] >= size[1]:
            if ((best_size[0] < size[0] or best_size[1] < size[1])
                    or sz[0] * sz[1] < best_size[0] * best_size[1]):
                best = img
                best_size = sz
        elif sz[0] * sz[1] > best_size[0] * best_size[1]:
            best = img
            best_size = sz
    img = best.Rescale(size[0], size[1], wx.IMAGE_QUALITY_HIGH)
    return wx.Bitmap(img)


def get_png_resource_bmp(name, size=None):
    img = _get_png_resource(name)
    if size is not None:
        img = img.Rescale(size[0], size[1], wx.IMAGE_QUALITY_HIGH)
    return wx.Bitmap(img)

