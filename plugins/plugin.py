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

from . import tools
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
        self.description = "PCB cleanup tools: fonts, edges, fiducials, vias"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'icon.png')

    def Run(self):
        frame = wx.GetActiveWindow()
        dlg = KiToolsDialog(frame)
        dlg.ShowModal()
        dlg.Destroy()


class KiToolsDialog(wx.Dialog):
    # Fixed layer order for the font fixer checkboxes
    FIX_LAYERS = ['F.SilkS', 'B.SilkS', 'F.Fab', 'B.Fab']

    # (label, tooltip, stub name) for the planned tools
    PLANNED_TOOLS = [
        ("Edge Line Equalizer", "Planned: equalize board edge line widths"),
        ("Fiducial Grid Placer", "Planned: place fiducials on a grid"),
        ("Fix Vias", "Planned: via cleanup"),
    ]

    def __init__(self, parent):
        title = "KI-Tools V{}".format(plugin_version)
        super().__init__(parent, title=title, size=(430, 430))
        self.options = load_options()

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # --- Font Fixer section ---
        fix_box = wx.StaticBox(panel, label="Font Fixer")
        fix_sizer = wx.StaticBoxSizer(fix_box, wx.VERTICAL)

        size_row = wx.BoxSizer(wx.HORIZONTAL)
        size_row.Add(wx.StaticText(panel, label="Font size (mm): "),
                     flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=5)
        self.font_size_spin = wx.SpinCtrlDouble(
            panel, min=0.1, max=10.0, initial=1.0, inc=0.1)
        self.font_size_spin.SetDigits(2)
        size_row.Add(self.font_size_spin,
                     flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=15)
        size_row.Add(wx.StaticText(panel, label="Line thickness (mm): "),
                     flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=5)
        self.thickness_spin = wx.SpinCtrlDouble(
            panel, min=0.01, max=5.0, initial=0.15, inc=0.05)
        self.thickness_spin.SetDigits(3)
        size_row.Add(self.thickness_spin, flag=wx.ALIGN_CENTER_VERTICAL)
        fix_sizer.Add(size_row, flag=wx.EXPAND | wx.ALL, border=10)

        self.visible_check = wx.CheckBox(panel, label="Visible")
        fix_sizer.Add(self.visible_check, flag=wx.LEFT | wx.RIGHT, border=10)

        layer_row = wx.BoxSizer(wx.HORIZONTAL)
        layer_row.Add(wx.StaticText(panel, label="Layers: "),
                      flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=5)
        self.layer_checks = {}
        for layer in self.FIX_LAYERS:
            cb = wx.CheckBox(panel, label=layer)
            layer_row.Add(cb,
                          flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=5)
            self.layer_checks[layer] = cb
        fix_sizer.Add(layer_row, flag=wx.LEFT | wx.RIGHT, border=10)

        self.fix_btn = wx.Button(panel, label="Fix Fonts")
        fix_sizer.Add(self.fix_btn,
                      flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, border=10)

        vbox.Add(fix_sizer, flag=wx.EXPAND | wx.ALL, border=10)

        # --- Planned tools (disabled placeholders) ---
        plan_box = wx.StaticBox(panel, label="Planned tools")
        plan_sizer = wx.StaticBoxSizer(plan_box, wx.VERTICAL)
        for label, tooltip in self.PLANNED_TOOLS:
            btn = wx.Button(panel, label=label)
            btn.Disable()
            btn.SetToolTip(tooltip)
            plan_sizer.Add(btn, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(plan_sizer, flag=wx.EXPAND | wx.ALL, border=10)

        # --- Status + version footer ---
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

        self.fix_btn.Bind(wx.EVT_BUTTON, self.on_fix_fonts)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self._restore_controls()
        panel.SetSizer(vbox)

    # --- UI state ---

    def _restore_controls(self):
        opts = self.options['fixfonts']
        self.font_size_spin.SetValue(float(opts.get('font_size', 1.0)))
        self.thickness_spin.SetValue(float(opts.get('line_thickness', 0.15)))
        self.visible_check.SetValue(bool(opts.get('visible', True)))
        layers = opts.get('layers', {})
        for layer, cb in self.layer_checks.items():
            cb.SetValue(bool(layers.get(layer, layer in ('F.SilkS', 'B.SilkS'))))

    def _collect_options(self):
        opts = self.options['fixfonts']
        opts['font_size'] = float(self.font_size_spin.GetValue())
        opts['line_thickness'] = float(self.thickness_spin.GetValue())
        opts['visible'] = self.visible_check.GetValue()
        opts['layers'] = {layer: cb.GetValue()
                          for layer, cb in self.layer_checks.items()}
        return opts

    # --- Events ---

    def on_fix_fonts(self, event):
        opts = self._collect_options()
        save_options(self.options)
        board = pcbnew.GetBoard()
        if board is None:
            self.status_label.SetLabel("No board open.")
            return
        active_layers = [layer for layer, enabled in opts['layers'].items()
                         if enabled]
        if not active_layers:
            self.status_label.SetLabel("No layers selected.")
            return
        try:
            count = tools.fix_fonts(
                board,
                opts['font_size'],
                opts['line_thickness'],
                opts['visible'],
                active_layers,
            )
            log_message(f"Fixed fonts: {count} text items")
            self.status_label.SetLabel(f"Fixed {count} text items.")
        except NotImplementedError as e:
            self.status_label.SetLabel(str(e))
        except Exception as e:
            log_message(f"Fix fonts failed: {e}", log_type="ERROR")
            self.status_label.SetLabel("Fix fonts failed: {}".format(e))

    def on_close(self, event):
        self._collect_options()
        save_options(self.options)
        event.Skip()
