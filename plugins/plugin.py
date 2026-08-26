##########################################################
#
# Script: plugin.py
# Author: Jani Hirvinen (jpkh)
# Contact: jphelirc@gmail.com
# Repository: https://github.com/jpkh/ki-tools
#
# Copyright (c) 2026 Jani Hirvinen
# License: GPL-3.0 - see the LICENSE file
#
# Description: Main dialog and ActionPlugin for KI-Tools.
#
##########################################################

import json
import os
import wx
import pcbnew

from . import fix_text, fix_via
from .config import DEFAULT_OPTIONS, settingsFileName, plugin_version
from .log_util import log_message


def _settings_file():
    """Settings live next to the plugin code (created at runtime, never shipped)."""
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), settingsFileName)


def load_options():
    """Merge stored values over the defaults so new keys keep working."""
    defaults = json.loads(json.dumps(DEFAULT_OPTIONS))
    try:
        with open(_settings_file(), 'r') as f:
            user = json.load(f)
    except Exception:
        user = {}
    for tool_key, tool_defaults in defaults.items():
        user_tool = user.get(tool_key)
        if isinstance(user_tool, dict):
            tool_defaults.update(user_tool)
    return defaults


def save_options(options):
    try:
        with open(_settings_file(), 'w') as f:
            json.dump(options, f, indent=4)
    except Exception as e:
        log_message(f"Error saving settings: {e}", log_type="ERROR")


class KiToolsPlugin(pcbnew.ActionPlugin):
    def __init__(self):
        super().__init__()
        self.name = "KI-Tools"
        self.category = "Utilities"
        self.description = "PCB cleanup tools: texts, vias, edges, fiducials"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'icon.png')

    def Run(self):
        frame = wx.GetActiveWindow()
        dlg = KiToolsDialog(frame)
        dlg.ShowModal()
        dlg.Destroy()


class KiToolsDialog(wx.Dialog):
    TEXT_LAYERS = ['F.SilkS', 'B.SilkS', 'F.Fab', 'B.Fab']

    PLANNED_TOOLS = [
        ("Edge Line Equalizer", "Planned: equalize board edge line widths"),
        ("Fiducial Grid Placer", "Planned: place fiducials on a grid"),
    ]

    def __init__(self, parent):
        title = "KI-Tools V{}".format(plugin_version)
        super().__init__(parent, title=title, size=(470, 560))
        self.options = load_options()

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        vbox.Add(self._build_text_section(panel),
                 flag=wx.EXPAND | wx.ALL, border=10)
        vbox.Add(self._build_via_section(panel),
                 flag=wx.EXPAND | wx.ALL, border=10)
        vbox.Add(self._build_planned_section(panel),
                 flag=wx.EXPAND | wx.ALL, border=10)

        # Status + version footer
        self.status_label = wx.StaticText(panel, label="Ready.")
        hbox_info = wx.BoxSizer(wx.HORIZONTAL)
        hbox_info.Add(self.status_label, flag=wx.ALIGN_CENTER_VERTICAL)
        hbox_info.AddStretchSpacer(1)
        hbox_info.Add(wx.StaticText(panel, label="KI-Tools V{}".format(plugin_version)),
                      flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=10)
        hbox_info.Add(wx.StaticText(panel, label="(c)2026 "),
                      flag=wx.ALIGN_CENTER_VERTICAL)
        hbox_info.Add(wx.adv.HyperlinkCtrl(panel, wx.ID_ANY, "jpkh/fi",
                                           "https://github.com/jpkh"),
                      flag=wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox_info, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                 border=10)

        self.fix_text_btn.Bind(wx.EVT_BUTTON, self.on_fix_text)
        self.fix_via_btn.Bind(wx.EVT_BUTTON, self.on_fix_via)
        self.count_via_btn.Bind(wx.EVT_BUTTON, self.on_count_vias)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self._restore_controls()
        panel.SetSizer(vbox)

    # --- Section builders ---

    def _build_text_section(self, panel):
        box = wx.StaticBox(panel, label="Text Size Fixer")
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        row = wx.BoxSizer(wx.HORIZONTAL)
        row.Add(wx.StaticText(panel, label="Text size (mm): "),
                flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=5)
        self.text_size_spin = wx.SpinCtrlDouble(
            panel, min=0.1, max=10.0, initial=0.8, inc=0.05)
        self.text_size_spin.SetDigits(2)
        row.Add(self.text_size_spin,
                flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=15)
        row.Add(wx.StaticText(panel, label="Thickness (mm): "),
                flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=5)
        self.text_thickness_spin = wx.SpinCtrlDouble(
            panel, min=0.01, max=5.0, initial=0.1, inc=0.01)
        self.text_thickness_spin.SetDigits(2)
        row.Add(self.text_thickness_spin, flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(row, flag=wx.EXPAND | wx.ALL, border=10)

        row2 = wx.BoxSizer(wx.HORIZONTAL)
        self.text_visible_check = wx.CheckBox(panel, label="Visible")
        row2.Add(self.text_visible_check, flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(row2, flag=wx.LEFT | wx.RIGHT, border=10)

        grid = wx.GridSizer(2, 2, 5, 5)
        self.text_layer_checks = {}
        for layer in self.TEXT_LAYERS:
            cb = wx.CheckBox(panel, label=layer)
            self.text_layer_checks[layer] = cb
            grid.Add(cb, flag=wx.EXPAND)
        layer_row = wx.BoxSizer(wx.HORIZONTAL)
        layer_row.Add(wx.StaticText(panel, label="Layers:"),
                      flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=5)
        layer_row.Add(grid, proportion=1, flag=wx.EXPAND)
        self.fix_text_btn = wx.Button(panel, label="Fix Text Sizes")
        self.fix_text_btn.SetToolTip(
            "Set footprint reference and value texts to the same size,\n"
            "thickness and visibility on the selected layers.")
        layer_row.Add(self.fix_text_btn, flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(layer_row, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)
        return sizer

    def _build_via_section(self, panel):
        box = wx.StaticBox(panel, label="Fix Vias")
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        self.via_spins = {}
        grid = wx.GridSizer(2, 2, 5, 5)
        for key, label, initial in (
            ('old_diameter', 'Old diameter', 0.6),
            ('new_diameter', 'New diameter', 0.45),
            ('old_drill', 'Old drill', 0.3),
            ('new_drill', 'New drill', 0.3),
        ):
            cell = wx.BoxSizer(wx.VERTICAL)
            cell.Add(wx.StaticText(panel, label=label + " (mm):"),
                     flag=wx.ALIGN_CENTER_HORIZONTAL)
            spin = wx.SpinCtrlDouble(
                panel, min=0.05, max=10.0, initial=initial, inc=0.05)
            spin.SetDigits(2)
            cell.Add(spin, flag=wx.EXPAND | wx.TOP, border=3)
            self.via_spins[key] = spin
            grid.Add(cell, flag=wx.EXPAND)
        sizer.Add(grid, flag=wx.EXPAND | wx.ALL, border=10)

        help_label = wx.StaticText(
            panel,
            label="Only vias matching both the old diameter and the old drill "
                  "are counted and changed.")
        help_font = help_label.GetFont()
        help_font.SetPointSize(max(6, help_font.GetPointSize() - 1))
        help_label.SetFont(help_font)
        help_label.SetForegroundColour(
            wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT))
        sizer.Add(help_label, flag=wx.LEFT | wx.RIGHT, border=10)

        btn_row = wx.BoxSizer(wx.HORIZONTAL)
        self.count_via_btn = wx.Button(panel, label="Count Vias")
        self.count_via_btn.SetToolTip(
            "Count vias matching the old diameter and drill.")
        self.via_count_label = wx.StaticText(panel, label="vias: -")
        btn_row.Add(self.count_via_btn,
                    flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=8)
        btn_row.Add(self.via_count_label, flag=wx.ALIGN_CENTER_VERTICAL)
        btn_row.AddStretchSpacer(1)
        self.fix_via_btn = wx.Button(panel, label="Fix Vias")
        self.fix_via_btn.SetToolTip(
            "Resize every via matching the old diameter and drill.")
        btn_row.Add(self.fix_via_btn, flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(btn_row, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                  border=10)
        return sizer

    def _build_planned_section(self, panel):
        box = wx.StaticBox(panel, label="Planned tools")
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        for label, tooltip in self.PLANNED_TOOLS:
            btn = wx.Button(panel, label=label)
            btn.Disable()
            btn.SetToolTip(tooltip)
            sizer.Add(btn, flag=wx.EXPAND | wx.ALL, border=5)
        return sizer

    # --- UI state ---

    def _restore_controls(self):
        text = self.options['textsizer']
        self.text_size_spin.SetValue(float(text.get('text_size', 0.8)))
        self.text_thickness_spin.SetValue(float(text.get('thickness', 0.1)))
        self.text_visible_check.SetValue(bool(text.get('visible', True)))
        layers = text.get('layers', {})
        for name, cb in self.text_layer_checks.items():
            cb.SetValue(bool(layers.get(name, name in ('F.SilkS', 'B.SilkS'))))

        via = self.options['fixvia']
        for key, spin in self.via_spins.items():
            spin.SetValue(float(via.get(key, spin.GetValue())))

    def _save(self):
        text = self.options['textsizer']
        text['text_size'] = float(self.text_size_spin.GetValue())
        text['thickness'] = float(self.text_thickness_spin.GetValue())
        text['visible'] = self.text_visible_check.GetValue()
        text['layers'] = {name: cb.GetValue()
                          for name, cb in self.text_layer_checks.items()}

        via = self.options['fixvia']
        for key, spin in self.via_spins.items():
            via[key] = float(spin.GetValue())

        save_options(self.options)

    # --- Events ---

    def on_fix_text(self, event):
        self._save()
        board = pcbnew.GetBoard()
        if board is None:
            self.status_label.SetLabel("No board open.")
            return
        layers = [name for name, cb in self.text_layer_checks.items()
                  if cb.GetValue()]
        if not layers:
            self.status_label.SetLabel("No layers selected.")
            return
        try:
            count = fix_text.fix_text_sizes(
                board,
                self.text_size_spin.GetValue(),
                self.text_thickness_spin.GetValue(),
                self.text_visible_check.GetValue(),
                layers,
            )
            log_message(f"Fixed text sizes: {count} text items")
            self.status_label.SetLabel(f"Updated {count} text items.")
        except Exception as e:
            log_message(f"Fix text sizes failed: {e}", log_type="ERROR")
            self.status_label.SetLabel("Fix text sizes failed: {}".format(e))

    def on_fix_via(self, event):
        self._save()
        board = pcbnew.GetBoard()
        if board is None:
            self.status_label.SetLabel("No board open.")
            return
        try:
            count = fix_via.fix_vias(
                board,
                self.via_spins['old_diameter'].GetValue(),
                self.via_spins['new_diameter'].GetValue(),
                self.via_spins['old_drill'].GetValue(),
                self.via_spins['new_drill'].GetValue(),
            )
            log_message(f"Fixed vias: {count} updated")
            self.status_label.SetLabel(f"Updated {count} vias.")
            # Refresh the manual count display (matching vias are gone now)
            remaining = fix_via.count_vias(
                board,
                self.via_spins['old_diameter'].GetValue(),
                self.via_spins['old_drill'].GetValue(),
            )
            self.via_count_label.SetLabel(f"vias: {remaining}")
        except Exception as e:
            log_message(f"Fix vias failed: {e}", log_type="ERROR")
            self.status_label.SetLabel("Fix vias failed: {}".format(e))

    def on_count_vias(self, event):
        self._save()
        board = pcbnew.GetBoard()
        if board is None:
            self.status_label.SetLabel("No board open.")
            return
        try:
            count = fix_via.count_vias(
                board,
                self.via_spins['old_diameter'].GetValue(),
                self.via_spins['old_drill'].GetValue(),
            )
            self.via_count_label.SetLabel(f"vias: {count}")
            self.status_label.SetLabel(f"Found {count} matching vias.")
        except Exception as e:
            log_message(f"Count vias failed: {e}", log_type="ERROR")
            self.status_label.SetLabel("Count vias failed: {}".format(e))

    def on_close(self, event):
        self._save()
        event.Skip()
