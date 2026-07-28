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

from enum import Enum, IntEnum
import wx

from .. import ps2mc, ps2iconsys
from ..save import ps2save

from . import utils


def get_dialog_units(win):
    return win.ConvertDialogToPixels((1, 1))[0]


class DirListControl(wx.ListCtrl):
    """Lists all the save files in a memory card image."""

    class Column(IntEnum):
        DIRECTORY = 0
        SIZE = 1
        MODIFIED = 2
        DESCRIPTION = 3

    class TableEntry:
        class Type(Enum):
            PS2 = 0
            PS1 = 1

        def __init__(self, type, dirent, icon_sys, size, title):
            self.type = type
            self.dirent = dirent
            self.icon_sys = icon_sys
            self.size = size
            self.title = title

    _PARENT_ENTRY = 0x7FFFFFFE

    def __init__(self, parent, evt_focus, evt_select, config):
        self.config = config
        self.selected = set()
        self.dirtable = []
        self.current_path = "/"
        self._mc = None
        self._on_navigate = None
        self._updating = False
        # current sort state for column header clicks
        self.sort_column = self.Column.DIRECTORY
        self.sort_reverse = False

        self.evt_select = evt_select
        self.evt_focus = evt_focus
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY,
                             style=wx.LC_REPORT)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.evt_col_click)
        self.Bind(wx.EVT_LIST_ITEM_FOCUSED, self._evt_focus_wrapper)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.evt_item_selected)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.evt_item_deselected)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.evt_item_activated)

    def _evt_focus_wrapper(self, event):
        """Skip focus events for the '..' entry or during updates."""
        if self._updating:
            return
        if event.GetData() == self._PARENT_ENTRY:
            return
        self.evt_focus(event)

    def _update_dirtable(self, mc, dir):
        self.dirtable = table = []
        enc = "unicode"
        if self.config.get_ascii():
            enc = "ascii"
        for ent in dir:
            mode = ent[0]
            if not (mode & ps2mc.DF_EXISTS):
                continue
            name = ent[8].decode("ascii")
            if name in (".", ".."):
                continue

            if ps2mc.mode_is_dir(mode):
                dirpath = self.current_path.rstrip("/") + "/" + name
                if ps2mc.mode_is_psx_dir(mode):
                    type = self.TableEntry.Type.PS1
                    title = (name, "")
                    icon_sys = None
                else:
                    type = self.TableEntry.Type.PS2
                    icon_sys_data = mc.get_icon_sys(dirpath)
                    if icon_sys_data is None:
                        type = self.TableEntry.Type.PS1
                        title = (name, "")
                        icon_sys = None
                    else:
                        icon_sys = ps2iconsys.IconSys(icon_sys_data)
                        title = icon_sys.get_title(enc)
                size = mc.dir_size(dirpath)
                table.append(self.TableEntry(type, ent, icon_sys, size, title))
            elif self.current_path != "/":
                # Show files when inside a subdirectory
                table.append(self.TableEntry(
                    self.TableEntry.Type.PS2, ent, None, ent[2], (name, "")))

    def update_dirtable(self, mc):
        self.dirtable = []
        if mc is None:
            return
        dir = mc.dir_open(self.current_path)
        try:
            self._update_dirtable(mc, dir)
        finally:
            dir.close()

    def update_column_headers(self):
        """Update column texts with an arrow on the active sort column."""

        # Base titles for each column
        columns = [
            (self.Column.DIRECTORY,   "Directory"),
            (self.Column.SIZE,        "Size"),
            (self.Column.MODIFIED,    "Modified"),
            (self.Column.DESCRIPTION, "Description"),
        ]

        # Unicode arrows for clarity; switch to " ^"/" v" if you prefer ASCII
        arrow_up = " ▲"
        arrow_down = " ▼"

        for col_enum, base in columns:
            text = base
            if col_enum == self.sort_column:
                text += arrow_down if self.sort_reverse else arrow_up

            item = self.GetColumn(col_enum.value)
            item.SetText(text)
            self.SetColumn(col_enum.value, item)

    def _apply_sort_direction(self, result):
        """Flip the comparison result if we're in reverse-sort mode.

        wx.ListCtrl.SortItems expects a negative/zero/positive integer.
        """
        if self.sort_reverse:
            return -result
        return result

    def cmp_dir_name(self, i1, i2):
        if i1 == self._PARENT_ENTRY:
            return -1
        if i2 == self._PARENT_ENTRY:
            return 1
        v1 = self.dirtable[i1].dirent[8]
        v2 = self.dirtable[i2].dirent[8]
        if v1 < v2:
            result = -1
        elif v1 > v2:
            result = 1
        else:
            result = 0
        return self._apply_sort_direction(result)

    def cmp_dir_title(self, i1, i2):
        if i1 == self._PARENT_ENTRY:
            return -1
        if i2 == self._PARENT_ENTRY:
            return 1
        v1 = self.dirtable[i1].title
        v2 = self.dirtable[i2].title
        if v1 < v2:
            result = -1
        elif v1 > v2:
            result = 1
        else:
            result = 0
        return self._apply_sort_direction(result)

    def cmp_dir_size(self, i1, i2):
        if i1 == self._PARENT_ENTRY:
            return -1
        if i2 == self._PARENT_ENTRY:
            return 1
        v1 = self.dirtable[i1].size
        v2 = self.dirtable[i2].size
        if v1 < v2:
            result = -1
        elif v1 > v2:
            result = 1
        else:
            result = 0
        return self._apply_sort_direction(result)

    def cmp_dir_modified(self, i1, i2):
        if i1 == self._PARENT_ENTRY:
            return -1
        if i2 == self._PARENT_ENTRY:
            return 1
        m1 = list(self.dirtable[i1].dirent[6])
        m2 = list(self.dirtable[i2].dirent[6])
        # dirent[6] is a tuple like (sec, min, hour, day, month, year)
        # Reverse so that comparisons happen in chronological order.
        m1.reverse()
        m2.reverse()
        if m1 < m2:
            result = -1
        elif m1 > m2:
            result = 1
        else:
            result = 0
        return self._apply_sort_direction(result)

    def evt_col_click(self, event):
        col = self.Column(event.Column)

        # Clicking the same column toggles ascending/descending.
        if col == self.sort_column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False

        if col == self.Column.DIRECTORY:
            cmp = self.cmp_dir_name
        elif col == self.Column.SIZE:
            cmp = self.cmp_dir_size
        elif col == self.Column.MODIFIED:
            cmp = self.cmp_dir_modified
        elif col == self.Column.DESCRIPTION:
            cmp = self.cmp_dir_title
        else:
            return

        # Update header text to show the arrow for the active sort
        self.update_column_headers()

        # Apply the sort
        self.SortItems(cmp)

    def evt_item_selected(self, event):
        idx = event.GetData()
        if idx == self._PARENT_ENTRY:
            return
        self.selected.add(idx)
        self.evt_select(event)

    def evt_item_deselected(self, event):
        idx = event.GetData()
        if idx == self._PARENT_ENTRY:
            return
        self.selected.discard(idx)
        self.evt_select(event)

    def evt_item_activated(self, event):
        """Handle double-click: navigate into directories or go up with '..'."""
        idx = event.GetData()
        if idx == self._PARENT_ENTRY:
            # '..' entry
            self.navigate_up()
            return
        entry = self.dirtable[idx]
        if entry.dirent[0] & ps2mc.DF_DIR:
            dirname = entry.dirent[8].decode("ascii")
            self.current_path = self.current_path.rstrip("/") + "/" + dirname
            self.update(self._mc)
            if self._on_navigate:
                self._on_navigate()

    def navigate_up(self):
        if self.current_path == "/":
            return
        # Go up one level
        self.current_path = "/".join(self.current_path.rstrip("/").split("/")[:-1]) or "/"
        self.update(self._mc)
        if self._on_navigate:
            self._on_navigate()

    def update(self, mc):
        """Update the ListCtrl according to the contents of the
           memory card image."""

        self._mc = mc
        self._updating = True
        self.ClearAll()
        self.selected = set()

        columns = [
            (self.Column.DIRECTORY,     "Directory",    None),
            (self.Column.SIZE,          "Size",         wx.LIST_FORMAT_RIGHT),
            (self.Column.MODIFIED,      "Modified",     None),
            (self.Column.DESCRIPTION,   "Description",  None)
        ]

        for (id, title, align) in columns:
            index = id.value
            column = wx.ListItem()
            column.SetText(title)
            if align is not None:
                column.SetAlign(align)
            self.InsertColumn(index, column)

        # Default sort: directory name ascending
        self.sort_column = self.Column.DIRECTORY
        self.sort_reverse = False
        self.update_column_headers()

        self.update_dirtable(mc)

        empty = len(self.dirtable) == 0 and self.current_path == "/"
        self.Enable(not empty)

        item_offset = 0
        # Add '..' entry when not at root
        if self.current_path != "/":
            li = self.InsertItem(0, "..")
            self.SetItem(li, 1, "")
            self.SetItem(li, 2, "")
            self.SetItem(li, 3, "(Parent Directory)")
            self.SetItemData(li, self._PARENT_ENTRY)
            item_offset = 1

        if len(self.dirtable) == 0 and self.current_path == "/":
            self._updating = False
            return

        for (i, a) in enumerate(self.dirtable):
            li = self.InsertItem(i + item_offset, a.dirent[8])
            self.SetItem(li, 1, "%dK" % (a.size // 1024))
            m = a.dirent[6]
            m = ("%04d-%02d-%02d %02d:%02d"
                 % (m[5], m[4], m[3], m[2], m[1]))
            self.SetItem(li, 2, m)
            self.SetItem(li, 3, utils.single_title(a.title))
            self.SetItemData(li, i)

        du = get_dialog_units(self)
        for i in range(4):
            self.SetColumnWidth(i, wx.LIST_AUTOSIZE)
            self.SetColumnWidth(i, self.GetColumnWidth(i) + du)

        # Apply default sort (Directory, ascending)
        self.SortItems(self.cmp_dir_name)
        self._updating = False
