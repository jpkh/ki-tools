##########################################################
#
# Script: fix_via.py
# Author: Jani Hirvinen (jpkh)
# Contact: jphelirc@gmail.com
# Repository: https://github.com/jpkh/ki-tools
#
# Copyright (c) 2026 Jani Hirvinen
# License: GPL-3.0 - see the LICENSE file
#
# Description: Fix Vias — resize every via matching an old diameter and
#              drill to a new diameter and drill.
#              Ported from the original fixvia.py script.
#
##########################################################

import pcbnew


def count_vias(board, old_diameter, old_drill):
    """Count vias matching the exact old diameter and drill. mm values."""
    old_d_nm = int(round(old_diameter * 1e6))
    old_drill_nm = int(round(old_drill * 1e6))

    count = 0
    for via in board.GetVias():
        if via.GetWidth() == old_d_nm and via.GetDrill() == old_drill_nm:
            count += 1
    return count


def fix_vias(board, old_diameter, new_diameter, old_drill, new_drill):
    """Resize vias matching the old diameter and drill.

    All values in mm. Returns the number of updated vias.
    """
    old_d_nm = int(round(old_diameter * 1e6))
    new_d_nm = int(round(new_diameter * 1e6))
    old_drill_nm = int(round(old_drill * 1e6))
    new_drill_nm = int(round(new_drill * 1e6))

    count = 0
    for via in board.GetVias():
        if via.GetWidth() == old_d_nm and via.GetDrill() == old_drill_nm:
            via.SetWidth(new_d_nm)
            via.SetDrill(new_drill_nm)
            count += 1

    board.Refresh()
    return count
