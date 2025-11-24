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

"""Graphical user-interface for mymc++."""

import copy
import os
import sys
import struct
import io

from pathlib import Path

# Windows-specific fixes
if os.name == "nt":
    # Work around a problem with mixing wx and py2exe
    if hasattr(sys, "setdefaultencoding"):
        sys.setdefaultencoding("mbcs")

    # Fix DPI awareness
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(True)
    except Exception:
        pass

import wx

from .. import ps2mc, ps2iconsys
from ..round import *
from ..save import ps2save
from .icon_window import IconWindow
from .dirlist_control import DirListControl
from . import utils


class GuiConfig(wx.Config):
    """A class for holding the persistant configuration state."""

    memcard_dir = "Memory Card Directory"
    savefile_dir = "Save File Directory"
    ascii = "ASCII Descriptions"
    force_import = "Force Import Overwrite"

    def __init__(self):
        wx.Config.__init__(self, "mymc++", style=wx.CONFIG_USE_LOCAL_FILE)

    def get_memcard_dir(self, default=None):
        return self.Read(GuiConfig.memcard_dir, default)

    def set_memcard_dir(self, value):
        return self.Write(GuiConfig.memcard_dir, value)

    def get_savefile_dir(self, default=None):
        return self.Read(GuiConfig.savefile_dir, default)

    def set_savefile_dir(self, value):
        return self.Write(GuiConfig.savefile_dir, value)

    def get_ascii(self, default=False):
        return bool(self.ReadInt(GuiConfig.ascii, int(bool(default))))

    def set_ascii(self, value):
        return self.WriteInt(GuiConfig.ascii, int(bool(value)))

    def get_force_import(self, default=False):
        return bool(self.ReadInt(GuiConfig.force_import, int(bool(default))))

    def set_force_import(self, value):
        return self.WriteInt(GuiConfig.force_import, int(bool(value)))


def add_tool(toolbar, id, label, standard_art, ico):
    bmp = wx.NullBitmap

    if standard_art is not None:
        bmp = wx.ArtProvider.GetBitmap(standard_art, wx.ART_TOOLBAR)

    if bmp == wx.NullBitmap:
        tbsize = toolbar.GetToolBitmapSize()
        bmp = utils.get_png_resource_bmp(ico, tbsize)

    return toolbar.AddTool(id, label, bmp, shortHelp=label)


class GuiFrame(wx.Frame):
    """The main top level window."""

    ID_CMD_EXIT = wx.ID_EXIT
    ID_CMD_OPEN = wx.ID_OPEN
    ID_CMD_EXPORT = 103
    ID_CMD_IMPORT = 104
    ID_CMD_DELETE = wx.ID_DELETE
    ID_CMD_SELECT_ALL = 111
    ID_CMD_ASCII = 106
    ID_CMD_SAVEAS = 107
    ID_CMD_NEW_MC = 109
    ID_CMD_ECC_TOOL = 110
    ID_CMD_FORCE_IMPORT = 108

    def message_box(self, message, caption="mymcplusplus", style=wx.OK,
                    x=-1, y=-1):
        return wx.MessageBox(message, caption, style, self, x, y)

    def error_box(self, msg):
        return self.message_box(msg, "Error", wx.OK | wx.ICON_ERROR)

    def mc_error(self, value, filename=None):
        """Display a message box for EnvironmentError exeception."""

        if filename is None:
            filename = getattr(value, "filename")
        if filename is None:
            filename = self.mcname
        if filename is None:
            filename = "???"

        strerror = getattr(value, "strerror", None)
        if strerror is None:
            strerror = "unknown error"

        return self.error_box(filename + ": " + strerror)

    def __init__(self, parent, title, mcname=None):
        self.f = None
        self.mc = None
        self.mcname = None
        self.icon_win = None

        wx.Frame.__init__(self, parent, wx.ID_ANY, title)
        self.SetClientSize(self.FromDIP((800, 400)))

        self.Bind(wx.EVT_CLOSE, self.evt_close)

        self.config = GuiConfig()
        self.title = title
        # OS-specific shortcut labels for Save As and ECC Save As
        is_mac = (wx.Platform == "__WXMAC__")
        if is_mac:
            self._saveas_shortcut = "⌘S"
            self._ecc_shortcut = "⌘⌥S"
        else:
            self._saveas_shortcut = "Ctrl+S"
            self._ecc_shortcut = "Ctrl+Shift+S"

        self.SetIcon(wx.Icon(utils.get_png_resource_bmp("icon.png")))

        self.Bind(wx.EVT_MENU, self.evt_cmd_exit, id=self.ID_CMD_EXIT)
        self.Bind(wx.EVT_MENU, self.evt_cmd_open, id=self.ID_CMD_OPEN)
        self.Bind(wx.EVT_MENU, self.evt_cmd_saveas, id=self.ID_CMD_SAVEAS)
        self.Bind(wx.EVT_MENU, self.evt_cmd_export, id=self.ID_CMD_EXPORT)
        self.Bind(wx.EVT_MENU, self.evt_cmd_import, id=self.ID_CMD_IMPORT)
        self.Bind(wx.EVT_MENU, self.evt_cmd_delete, id=self.ID_CMD_DELETE)
        self.Bind(wx.EVT_MENU, self.evt_cmd_select_all, id=self.ID_CMD_SELECT_ALL)
        self.Bind(wx.EVT_MENU, self.evt_cmd_ascii, id=self.ID_CMD_ASCII)
        self.Bind(wx.EVT_MENU, self.evt_cmd_force_import, id=self.ID_CMD_FORCE_IMPORT)
        self.Bind(wx.EVT_MENU, self.evt_cmd_new_mc, id=self.ID_CMD_NEW_MC)
        self.Bind(wx.EVT_MENU, self.evt_cmd_ecc_tool, id=self.ID_CMD_ECC_TOOL)

        filemenu = wx.Menu()
        filemenu.Append(
            self.ID_CMD_OPEN,
            "&Open...\tCtrl+O",
            "Opens an existing PS2 memory card image.",
        )
        self.new_mc_menu_item = filemenu.Append(
            self.ID_CMD_NEW_MC,
            "&New Memory Card...\tCtrl+N",
            "Create a new PS2 memory card image.",
        )
        self.ecc_tool_menu_item = filemenu.Append(
            self.ID_CMD_ECC_TOOL,
            f"Remove ECC and Save As...\t{self._ecc_shortcut}",
            "Add or remove ECC on the current memory card image.",
        )
        filemenu.AppendSeparator()
        self.saveas_menu_item = filemenu.Append(
            self.ID_CMD_SAVEAS,
            f"&Save As...\t{self._saveas_shortcut}",
        )
        self.select_all_menu_item = filemenu.Append(
            self.ID_CMD_SELECT_ALL,
            "Select &All\tCtrl+A",
        )
        filemenu.AppendSeparator()
        self.export_menu_item = filemenu.Append(
            self.ID_CMD_EXPORT,
            "&Export...\tCtrl+E",
            "Export a save file from this image.",
        )
        self.import_menu_item = filemenu.Append(
            self.ID_CMD_IMPORT,
            "&Import...\tCtrl+I",
            "Import a save file into this image.",
        )
        self.delete_menu_item = filemenu.Append(
            self.ID_CMD_DELETE,
            "&Delete\tDel",
        )
        filemenu.AppendSeparator()
        filemenu.Append(self.ID_CMD_EXIT, "E&xit\tCtrl+Q")

        optionmenu = wx.Menu()
        self.ascii_menu_item = optionmenu.AppendCheckItem(
            self.ID_CMD_ASCII,
            "&ASCII Descriptions\tCtrl+Shift+A",
            "Show descriptions in ASCII instead of Shift-JIS",
        )
        self.force_import_menu_item = optionmenu.AppendCheckItem(
            self.ID_CMD_FORCE_IMPORT,
            "&Force Import\tCtrl+Shift+F",
            "Force overwriting existing saves when importing",
        )

        self.Bind(wx.EVT_MENU_OPEN, self.evt_menu_open)

        self.CreateToolBar(wx.TB_HORIZONTAL)
        self.toolbar = toolbar = self.GetToolBar()
        toolbar.SetToolBitmapSize(self.FromDIP(wx.Size(50, 50)))
        add_tool(toolbar, self.ID_CMD_OPEN, "Open", wx.ART_FILE_OPEN, "open.png")
        toolbar.AddSeparator()
        add_tool(toolbar, self.ID_CMD_IMPORT, "Import", None, "import.png")
        add_tool(toolbar, self.ID_CMD_EXPORT, "Export", None, "export.png")
        add_tool(toolbar, self.ID_CMD_DELETE, "Delete", None, "delete.png")
        toolbar.Realize()

        self.statusbar = self.CreateStatusBar(2, style=wx.STB_SIZEGRIP)
        self.statusbar.SetStatusWidths([-2, -1])
        self._statusbar_default_colour = self.statusbar.GetForegroundColour()
        self._statusbar_default_colour = self.statusbar.GetForegroundColour()

        panel = wx.Panel(self, wx.ID_ANY, (0, 0))
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(panel, wx.EXPAND, wx.EXPAND)
        self.SetSizer(sizer)

        splitter_window = wx.SplitterWindow(panel, style=wx.SP_LIVE_UPDATE)
        splitter_window.SetSashGravity(0.5)

        self.dirlist = DirListControl(
            splitter_window,
            self.evt_dirlist_item_focused,
            self.evt_dirlist_select,
            self.config,
        )

        if mcname is not None:
            self.open_mc(mcname)
        else:
            self.refresh()

        # Ensure the force import status bar warning matches the current config
        self._update_force_import_status()

        panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        panel_sizer.Add(splitter_window, wx.EXPAND, wx.EXPAND)
        panel.SetSizer(panel_sizer)

        panel.Bind(wx.EVT_CHAR_HOOK, self.evt_key_pressed)

        info_win = wx.Window(splitter_window)
        icon_win = IconWindow(info_win, self)
        if icon_win.failed:
            info_win.Destroy()
            info_win = None
            icon_win = None
        self.info_win = info_win
        self.icon_win = icon_win

        if icon_win is None:
            self.info1 = None
            self.info2 = None
            splitter_window.Initialize(self.dirlist)
        else:
            self.icon_menu = icon_menu = wx.Menu()
            icon_win.append_menu_options(self, icon_menu)
            optionmenu.AppendSubMenu(icon_menu, "Icon Window")
            title_style = wx.ALIGN_RIGHT | wx.ST_NO_AUTORESIZE

            self.info1 = wx.StaticText(info_win, -1, "", style=title_style)
            self.info2 = wx.StaticText(info_win, -1, "", style=title_style)
            # self.info3 = wx.StaticText(panel, -1, "")

            info_sizer = wx.BoxSizer(wx.VERTICAL)
            info_sizer.Add(
                self.info1,
                0,
                wx.EXPAND | wx.LEFT | wx.RIGHT,
                border=4,
            )
            info_sizer.Add(
                self.info2,
                0,
                wx.EXPAND | wx.LEFT | wx.RIGHT,
                border=4,
            )
            # info_sizer.Add(self.info3, 0, wx.EXPAND)
            info_sizer.AddSpacer(5)
            info_sizer.Add(icon_win, 1, wx.EXPAND)
            info_win.SetSizer(info_sizer)

            splitter_window.SplitVertically(
                self.dirlist,
                info_win,
                int(self.Size.Width * 0.7),
            )

        menubar = wx.MenuBar()
        menubar.Append(filemenu, "&File")
        menubar.Append(optionmenu, "&Options")
        self.SetMenuBar(menubar)

        # Set up keyboard shortcuts (Cmd on macOS, Ctrl on others) for main actions.
        accel_entries = [
            (wx.ACCEL_CMD, ord("O"), self.ID_CMD_OPEN),           # Open
            (wx.ACCEL_CMD, ord("N"), self.ID_CMD_NEW_MC),         # New Memory Card
            (wx.ACCEL_CMD, ord("R"), self.ID_CMD_ECC_TOOL),       # Add/Remove ECC and Save As
            (wx.ACCEL_CMD | wx.ACCEL_SHIFT, ord("S"), self.ID_CMD_SAVEAS),  # Save As
            (wx.ACCEL_CMD, ord("E"), self.ID_CMD_EXPORT),         # Export
            (wx.ACCEL_CMD, ord("I"), self.ID_CMD_IMPORT),         # Import
            (wx.ACCEL_NORMAL, wx.WXK_DELETE, self.ID_CMD_DELETE), # Delete
            (wx.ACCEL_CMD, ord("Q"), self.ID_CMD_EXIT),           # Exit
            (wx.ACCEL_CMD | wx.ACCEL_SHIFT, ord("A"), self.ID_CMD_ASCII),       # ASCII Descriptions
            (wx.ACCEL_CMD | wx.ACCEL_SHIFT, ord("F"), self.ID_CMD_FORCE_IMPORT) # Force Import
        ]
        accel_table = wx.AcceleratorTable(
            [(flags, key, cmd_id) for (flags, key, cmd_id) in accel_entries]
        )
        self.SetAcceleratorTable(accel_table)

        self.Show(True)

        if self.mc is None:
            self.evt_cmd_open()

    def _close_mc(self):
        if self.mc is not None:
            try:
                self.mc.close()
            except EnvironmentError as value:
                self.mc_error(value)
            self.mc = None
        if self.f is not None:
            try:
                self.f.close()
            except EnvironmentError as value:
                self.mc_error(value)
            self.f = None
        self.mcname = None

    def refresh(self):
        try:
            self.dirlist.update(self.mc)
        except EnvironmentError as value:
            self.mc_error(value)
            self._close_mc()
            self.dirlist.update(None)

        mc = self.mc

        self.toolbar.EnableTool(self.ID_CMD_IMPORT, mc is not None)
        self.toolbar.EnableTool(self.ID_CMD_EXPORT, False)

        if mc is None:
            status = "No memory card image"
        else:
            free = mc.get_free_space() // 1024
            limit = mc.get_allocatable_space() // 1024
            status = "%dK of %dK free" % (free, limit)
        self.statusbar.SetStatusText(status, 1)

    def open_mc(self, filename):
        self._close_mc()
        self.statusbar.SetStatusText("", 1)
        if self.icon_win is not None:
            self.icon_win.load_icon(None, None)

        f = None
        try:
            f = open(filename, "r+b")
            mc = ps2mc.ps2mc(f)
        except EnvironmentError as value:
            if f is not None:
                f.close()
            self.mc_error(value, filename)
            self.SetTitle(self.title)
            self.refresh()
            return

        self.f = f
        self.mc = mc
        self.mcname = filename
        self.SetTitle(filename + " - " + self.title)
        self.refresh()

    def delete_selected(self):
        mc = self.mc
        if mc is None:
            return

        selected = self.dirlist.selected
        dirtable = self.dirlist.dirtable

        dirnames = [
            dirtable[i].dirent[8].decode("ascii")
            for i in selected
        ]
        if len(selected) == 1:
            title = dirtable[list(selected)[0]].title
            s = dirnames[0] + " (" + utils.single_title(title) + ")"
        else:
            s = ", ".join(dirnames)
            if len(s) > 200:
                s = s[:200] + "..."
        r = self.message_box(
            "Are you sure you want to delete " + s + "?",
            "Delete Save File Confirmation",
            wx.YES_NO,
        )
        if r != wx.YES:
            return

        for dn in dirnames:
            try:
                mc.rmdir("/" + dn)
            except EnvironmentError as value:
                self.mc_error(value, dn)

        mc.check()
        self.refresh()

    def evt_key_pressed(self, event):
        """Global key handler for shortcuts (Ctrl/Cmd + key)."""
        keycode = event.GetUnicodeKey()

        ctrl_or_cmd = event.ControlDown() or event.CmdDown()
        shift = event.ShiftDown()
        alt = event.AltDown()
        is_mac = (wx.Platform == "__WXMAC__")

        # Normalize letters to uppercase for comparison.
        if isinstance(keycode, int) and 97 <= keycode <= 122:
            key = chr(keycode - 32)
        elif isinstance(keycode, int) and 65 <= keycode <= 90:
            key = chr(keycode)
        else:
            key = None

        # Delete key (no modifiers).
        if keycode == wx.WXK_DELETE and not ctrl_or_cmd and not shift and not alt:
            self.delete_selected()
            return

        # Handle Save As / ECC Save As on S with modifiers:
        #   Windows/Linux: Ctrl+S (Save As), Ctrl+Shift+S (ECC Save As)
        #   macOS: Cmd+S (Save As), Cmd+Option+S (ECC Save As).
        if ctrl_or_cmd and key == "S":
            # Windows / Linux ECC: Ctrl+Shift+S (no Alt).
            if (not is_mac) and shift and not alt:
                self.evt_cmd_ecc_tool(event)
                return
            # macOS ECC: Cmd+Option+S (AltDown).
            if is_mac and alt:
                self.evt_cmd_ecc_tool(event)
                return
            # Plain Save As: primary modifier only, no Shift/Alt.
            if not shift and not alt:
                self.evt_cmd_saveas(event)
                return

        # Shortcuts that use primary modifier (Ctrl on Windows/Linux,
        # Cmd on macOS), no Shift/Alt.
        if ctrl_or_cmd and not shift and not alt and key is not None:
            if key == "O":
                self.evt_cmd_open(event)
                return
            if key == "N":
                self.evt_cmd_new_mc(event)
                return
            if key == "A":
                # Select All
                self.evt_cmd_select_all(event)
                return
            if key == "E":
                self.evt_cmd_export(event)
                return
            if key == "I":
                self.evt_cmd_import(event)
                return
            if key == "F":
                # Force Import toggle
                self.evt_cmd_force_import(event)
                return
            if key == "Q":
                self.evt_cmd_exit(event)
                return

        # Ctrl/Cmd+Shift+A -> ASCII Descriptions toggle (no Alt).
        if ctrl_or_cmd and shift and not alt and key == "A":
            self.evt_cmd_ascii(event)
            return

        # Let other keys propagate normally.
        event.Skip()

    def _update_force_import_status(self):
        """Sync the force import checkbox and status bar with current config."""
        fi = self.config.get_force_import()

        # Keep the menu checkmark in sync with the config
        if hasattr(self, "force_import_menu_item"):
            self.force_import_menu_item.Check(fi)

        if fi:
            # Show a red warning in the status bar when force import is active.
            self.statusbar.SetStatusText(
                "Force Import Mode Enabled - existing saves will be overwritten!",
                0,
            )
            self.statusbar.SetForegroundColour(wx.RED)
        else:
            # Clear warning and restore default color.
            self.statusbar.SetStatusText("", 0)
            self.statusbar.SetForegroundColour(self._statusbar_default_colour)

    def evt_menu_open(self, event):
        # Enable/disable basic actions based on current state
        self.import_menu_item.Enable(self.mc is not None)

        selected = self.mc is not None and len(self.dirlist.selected) > 0
        self.export_menu_item.Enable(selected)
        self.delete_menu_item.Enable(selected)

        self.select_all_menu_item.Enable(
            self.mc is not None and len(self.dirlist.dirtable) > 0
        )
        self.ascii_menu_item.Check(self.config.get_ascii())

        # Enable and update the ECC tool menu item based on current card
        has_mc = self.mc is not None
        self.ecc_tool_menu_item.Enable(has_mc)
        if has_mc:
            # Detect ECC based on spare_size: if there is spare area, ECC bytes exist.
            has_ecc = getattr(self.mc, "spare_size", 0) > 0

            if has_ecc:
                # Card currently has ECC → menu should show Remove ECC
                self.ecc_tool_menu_item.SetItemLabel(
                    f"&Remove ECC and Save As...\t{self._ecc_shortcut}"
                )
            else:
                # Card currently has NO ECC → menu should show Add ECC
                self.ecc_tool_menu_item.SetItemLabel(
                    f"&Add ECC and Save As...\t{self._ecc_shortcut}"
                )
        else:
            # No card open; default to "Add ECC" label
            self.ecc_tool_menu_item.SetItemLabel(
                f"&Add ECC and Save As...\t{self._ecc_shortcut}"
            )

        # Sync force import status (checkbox + warning text) with current config.
        self._update_force_import_status()

        if self.icon_win is not None:
            self.icon_win.update_menu(self.icon_menu)

    def evt_dirlist_item_focused(self, event):
        if self.icon_win is None:
            return

        i = event.GetData()
        entry = self.dirlist.dirtable[i]
        self.info1.SetLabel(entry.title[0])
        self.info2.SetLabel(entry.title[1])

        icon_sys = entry.icon_sys
        mc = self.mc

        if mc is None or icon_sys is None:
            self.icon_win.load_icon(None, None)
            return

        try:
            mc.chdir("/" + entry.dirent[8].decode("ascii"))
            f = mc.open(icon_sys.icon_file_normal, "rb")
            try:
                icon = f.read()
            finally:
                f.close()
        except EnvironmentError as value:
            print("icon failed to load", value)
            self.icon_win.load_icon(None, None)
            return

        self.icon_win.load_icon(icon_sys, icon)

    def evt_dirlist_select(self, event):
        self.toolbar.EnableTool(self.ID_CMD_IMPORT, self.mc is not None)
        self.toolbar.EnableTool(
            self.ID_CMD_EXPORT,
            len(self.dirlist.selected) > 0,
        )

    def evt_cmd_open(self, event=None):
        fn = wx.FileSelector(
            "Open Memory Card Image",
            self.config.get_memcard_dir(""),
            "Mcd001.ps2",
            "ps2",
            "Memory Card Image (*.ps2;*.mc2;*.mcd)|*.ps2;*.mc2;*.mcd",
            wx.FD_FILE_MUST_EXIST | wx.FD_OPEN,
            self,
        )
        if fn == "":
            return
        self.open_mc(fn)
        if self.mc is not None:
            dirname = os.path.dirname(fn)
            if os.path.isabs(dirname):
                self.config.set_memcard_dir(dirname)

    def evt_cmd_new_mc(self, event):
        """Create a new blank PS2 memory card image."""
        # Dialog to choose size and ECC settings
        dlg = wx.Dialog(self, title="Create New Memory Card")
        vbox = wx.BoxSizer(wx.VERTICAL)

        size_label = wx.StaticText(dlg, label="Card size:")
        size_choices = ["8 MB", "16 MB", "32 MB", "64 MB"]
        size_radio = wx.RadioBox(
            dlg,
            label="",
            choices=size_choices,
            majorDimension=1,
            style=wx.RA_SPECIFY_ROWS,
        )

        ecc_checkbox = wx.CheckBox(dlg, label="Disable ECC (-e)")
        ecc_checkbox.SetValue(False)

        vbox.Add(size_label, 0, wx.ALL, 5)
        vbox.Add(size_radio, 0, wx.ALL, 5)
        vbox.Add(ecc_checkbox, 0, wx.ALL, 5)

        btn_sizer = dlg.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        vbox.Add(btn_sizer, 0, wx.ALL | wx.ALIGN_RIGHT, 5)

        dlg.SetSizer(vbox)
        dlg.Fit()

        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return

        size_idx = size_radio.GetSelection()
        disable_ecc = ecc_checkbox.GetValue()
        dlg.Destroy()

        size_factors = [1, 2, 4, 8]  # 8MB, 16MB, 32MB, 64MB
        factor = size_factors[size_idx]
        with_ecc = not disable_ecc

        # Select filename for the new card
        fn = wx.FileSelector(
            "Create New Memory Card Image",
            self.config.get_memcard_dir(""),
            "Mcd001.ps2",
            "ps2",
            "PCSX2 Image|*.ps2"
            "|Multipurpose Memory Card Emulator - Virtual Memory Card|*.mc2;*.mcd",
            (wx.FD_OVERWRITE_PROMPT | wx.FD_SAVE),
            self,
        )
        if fn == "":
            return

        try:
            # Compute parameters for the new card.
            page_size = ps2mc.PS2MC_STANDARD_PAGE_SIZE
            pages_per_erase_block = ps2mc.PS2MC_STANDARD_PAGES_PER_ERASE_BLOCK
            base_pages_per_card = ps2mc.PS2MC_STANDARD_PAGES_PER_CARD
            pages_per_card = base_pages_per_card * factor

            params = (
                with_ecc,
                page_size,
                pages_per_erase_block,
                pages_per_card,
            )

            with open(fn, "w+b") as f:
                new_mc = ps2mc.ps2mc(f, True, params)
                new_mc.flush()
                new_mc.close()

            dirname = os.path.dirname(fn)
            if os.path.isabs(dirname):
                self.config.set_memcard_dir(dirname)

            # Open the newly created card
            self.open_mc(fn)

        except EnvironmentError as value:
            self.mc_error(value, fn)
            return

    def evt_cmd_ecc_tool(self, event):
        """Rebuild the current card as ECC or non-ECC and save as a new image."""
        mc = self.mc
        if mc is None:
            return

        # Determine current ECC state from the card object.
        # We consider the card to "have ECC" if it has a non-zero spare area.
        has_ecc = getattr(mc, "spare_size", 0) > 0
        target_with_ecc = not has_ecc

        from pathlib import Path as _Path
        base_name = _Path(self.mcname).name if getattr(self, "mcname", None) else "Mcd001.ps2"
        if has_ecc:
            # Card has ECC now: we are removing ECC.
            default_name = "NoECC_" + base_name
        else:
            # Card has no ECC now: we are adding ECC.
            default_name = "ECC_" + base_name

        fn = wx.FileSelector(
            "Remove ECC and Save As..." if has_ecc else "Add ECC and Save As...",
            self.config.get_memcard_dir(""),
            default_name,
            "ps2",
            "PCSX2 Image|*.ps2"
            "|Multipurpose Memory Card Emulator - Virtual Memory Card|*.mc2;*.mcd",
            (wx.FD_OVERWRITE_PROMPT | wx.FD_SAVE),
            self,
        )
        if fn == "":
            return

        try:
            # Use the current card geometry, but flip the ECC setting.
            page_size = mc.page_size
            pages_per_erase_block = mc.pages_per_erase_block
            pages_per_card = mc.clusters_per_card * mc.pages_per_cluster

            params = (
                target_with_ecc,
                page_size,
                pages_per_erase_block,
                pages_per_card,
            )

            with open(fn, "w+b") as f:
                new_mc = ps2mc.ps2mc(f, True, params)
                # Copy all saves from current card to new card.
                for dir_tab_entry in self.dirlist.dirtable:
                    dirname = dir_tab_entry.dirent[8].decode("ascii")
                    new_mc.import_save_file(
                        mc.export_save_file("/" + dirname),
                        False,
                    )

                new_mc.flush()
                new_mc.close()

            dirname = os.path.dirname(fn)
            if os.path.isabs(dirname):
                self.config.set_memcard_dir(dirname)

            # Open the rebuilt card.
            self.open_mc(fn)

        except EnvironmentError as value:
            self.mc_error(value, fn)
            return

    def evt_cmd_saveas(self, event):
        mc = self.mc
        if mc is None:
            return

        fn = wx.FileSelector(
            "Save As",
            self.config.get_memcard_dir(""),
            Path(self.mcname).stem + ".ps2",
            "ps2",
            "PCSX2 Image|*.ps2"
            "|Multipurpose Memory Card Emulator - Virtual Memory Card|*.mc2;*.mcd",
            (wx.FD_OVERWRITE_PROMPT | wx.FD_SAVE),
            self,
        )
        if fn == "":
            return
        try:
            filename = fn.lower()
            if filename.endswith(".mc2;*.mcd"):
                ecc = False
            else:
                ecc = True
            params = (
                ecc,
                mc.page_size,
                mc.pages_per_erase_block,
                mc.clusters_per_card * mc.pages_per_cluster,
            )

            with open(fn, "w+b") as f:
                new_mc = ps2mc.ps2mc(f, True, params)
                for dir_tab_entry in self.dirlist.dirtable:
                    dirname = dir_tab_entry.dirent[8].decode("ascii")
                    new_mc.import_save_file(
                        mc.export_save_file("/" + dirname),
                        False,
                    )

                new_mc.flush()
                new_mc.close()
        except EnvironmentError as value:
            self.mc_error(value, fn)
            return

    def evt_cmd_export(self, event):
        mc = self.mc
        if mc is None:
            return

        selected = self.dirlist.selected
        dirtable = self.dirlist.dirtable
        sfiles = []
        for i in selected:
            dirname = dirtable[i].dirent[8].decode("ascii")
            try:
                sf = mc.export_save_file("/" + dirname)
                longname = ps2save.make_longname(dirname, sf)
                sfiles.append((dirname, sf, longname))
            except EnvironmentError as value:
                self.mc_error(value. dirname)

        if len(sfiles) == 0:
            return

        dir = self.config.get_savefile_dir("")
        if len(selected) == 1:
            (dirname, sf, longname) = sfiles[0]
            fn = wx.FileSelector(
                "Export " + dirname,
                dir,
                longname,
                "psu",
                "EMS save file (.psu)|*.psu"
                "|MAXDrive save file (.max)"
                "|*.max",
                (wx.FD_OVERWRITE_PROMPT | wx.FD_SAVE),
                self,
            )
            if fn == "":
                return
            try:
                f = open(fn, "wb")
                try:
                    format = ps2save.format_for_filename(fn)
                    format.save(sf, f)
                finally:
                    f.close()
            except EnvironmentError as value:
                self.mc_error(value, fn)
                return

            dir = os.path.dirname(fn)
            if os.path.isabs(dir):
                self.config.set_savefile_dir(dir)

            self.message_box("Exported " + fn + " successfully.")
            return

        dir = wx.DirSelector("Export Save Files", dir, parent=self)
        if dir == "":
            return
        count = 0
        for (dirname, sf, longname) in sfiles:
            fn = os.path.join(dir, longname) + ".psu"
            try:
                f = open(fn, "wb")
                sf.save_ems(f)
                f.close()
                count += 1
            except EnvironmentError as value:
                self.mc_error(value, fn)
        if count > 0:
            if os.path.isabs(dir):
                self.config.set_savefile_dir(dir)
            self.message_box("Exported %d file(s) successfully." % count)

    def _do_import(self, fn):
        sf = ps2save.PS2SaveFile()
        f = open(fn, "rb")
        try:
            format = ps2save.poll_format(f)
            f.seek(0)
            if format is not None:
                format.load(sf, f)
            else:
                self.error_box(fn + ": Save file format not recognized.")
                return
        finally:
            f.close()

        force_import = self.config.get_force_import()
        mc = self.mc

        if force_import:
            # Use the directory name embedded in the save file itself, not
            # the filename, since a .psu/.max/etc can extract to any name.
            dir_ent = sf.get_directory()
            dir_name = dir_ent[8].decode("ascii")
            dirname = "/" + dir_name

            # Attempt to delete any existing save at that directory.
            try:
                mc.rmdir(dirname)
            except EnvironmentError as value:
                import errno
                err = getattr(value, "errno", None)
                # Ignore "no such file or directory"; surface other errors.
                if err not in (None, errno.ENOENT):
                    self.mc_error(value, dirname)
                    return

        # After optional deletion, import as usual. If a save with the same
        # directory name still exists, this will fail in the normal way.
        if not mc.import_save_file(sf, True):
            self.error_box(fn + ": Save file already present.")

    def evt_cmd_import(self, event):
        if self.mc is None:
            return

        dir = self.config.get_savefile_dir("")
        fd = wx.FileDialog(
            self,
            "Import Save File",
            dir,
            wildcard=(
                "PS2 save files"
                " (.cbs;.psu;.psv;.max;.sps;.xps)"
                "|*.cbs;*.psu;.psv;*.max;*.sps;*.xps"
                "|All files|*.*"
            ),
            style=(
                wx.FD_OPEN
                | wx.FD_MULTIPLE
                | wx.FD_FILE_MUST_EXIST
            ),
        )
        if fd is None:
            return
        r = fd.ShowModal()
        if r == wx.ID_CANCEL:
            return

        success = None
        for fn in fd.GetPaths():
            try:
                self._do_import(fn)
                success = fn
            except EnvironmentError as value:
                self.mc_error(value, fn)

        if success is not None:
            dir = os.path.dirname(success)
            if os.path.isabs(dir):
                self.config.set_savefile_dir(dir)
        self.refresh()

    def evt_cmd_delete(self, event):
        self.delete_selected()

    def evt_cmd_select_all(self, event):
        """Select all save entries in the list."""
        if self.mc is None:
            return
        count = self.dirlist.GetItemCount()
        for i in range(count):
            self.dirlist.Select(i, on=1)

    def evt_cmd_ascii(self, event):
        self.config.set_ascii(not self.config.get_ascii())
        self.refresh()

    def evt_cmd_force_import(self, event):
        new_value = not self.config.get_force_import()
        self.config.set_force_import(new_value)

        # Update the status bar and menu checkmark to reflect the new value.
        self._update_force_import_status()

    def evt_cmd_exit(self, event):
        self.Close(True)

    def evt_close(self, event):
        self._close_mc()
        self.Destroy()


def run(filename=None):
    """Display a GUI for working with memory card images."""

    wx_app = wx.App()
    frame = GuiFrame(None, "mymc++", filename)
    return wx_app.MainLoop()


if __name__ == "__main__":
    import gc
    gc.set_debug(gc.DEBUG_LEAK)

    run("test.ps2")

    gc.collect()
    for o in gc.garbage:
        print()
        print(o)
        if type(o) == ps2mc.ps2mc_file:
            for m in dir(o):
                print(m, getattr(o, m))
