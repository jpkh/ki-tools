##########################################################
#
# Script: fix_text.py
# Author: Jani Hirvinen (jpkh)
# Contact: jphelirc@gmail.com
# Repository: https://github.com/jpkh/ki-tools
#
# Copyright (c) 2026 Jani Hirvinen
# License: GPL-3.0 - see the LICENSE file
#
# Description: Text Size Fixer — set footprint reference/value text size,
#              thickness and visibility on the selected layers.
#              Ported from the original fixcompnamesize.py script.
#
##########################################################

import re
import pcbnew

# Layer names accepted from the dialog -> pcbnew layer constants
LAYERS = {
    'F.SilkS': pcbnew.F_SilkS,
    'B.SilkS': pcbnew.B_SilkS,
    'F.Fab': pcbnew.F_Fab,
    'B.Fab': pcbnew.B_Fab,
}

# Auto-hide patterns (faithful to the original script)
HIDE_FP_KEYWORDS = ['mountinghole', 'mounting hole', 'tooling', 'fiducial']
HIDE_REF_REGEX = r'^(G\d{3,}|FIDORIG1)$'
HIDE_VAL_REGEX = r'^LOGO$'


def should_hide(module):
    try:
        fp_name = str(module.GetFPID().GetLibItemName()).lower()
    except Exception:
        fp_name = ''
    ref = module.Reference().GetText().upper()
    val = module.Value().GetText().upper()

    for keyword in HIDE_FP_KEYWORDS:
        if keyword in fp_name:
            return True
    if re.match(HIDE_REF_REGEX, ref):
        return True
    if re.match(HIDE_VAL_REGEX, val):
        return True
    return False


def fix_text_sizes(board, text_size, thickness, visible, layer_names):
    """Set footprint reference and value texts to the same size, thickness
    and visibility on the given layers.

    text_size / thickness: mm floats.
    layer_names: list of strings from LAYERS.keys().
    Returns the number of modified text items.
    """
    target_layers = [LAYERS[name] for name in layer_names if name in LAYERS]
    if not target_layers:
        return 0

    width_nm = int(round(text_size * 1e6))
    thickness_nm = int(round(thickness * 1e6))

    count = 0
    for module in board.GetFootprints():
        auto_hide = should_hide(module)
        final_visible = bool(visible) and not auto_hide

        for text in (module.Reference(), module.Value()):
            if text.GetLayer() in target_layers:
                text.SetTextSize(pcbnew.VECTOR2I(width_nm, width_nm))
                text.SetTextThickness(thickness_nm)
                text.SetVisible(final_visible)
                count += 1

    pcbnew.Refresh()
    return count
