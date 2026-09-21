##########################################################
#
# Script: edge_equalizer.py
# Author: Jani Hirvinen (jpkh)
# Contact: jphelirc@gmail.com
# Repository: https://github.com/jpkh/ki-tools
#
# Copyright (c) 2026 Jani Hirvinen
# License: GPL-3.0 - see the LICENSE file
#
# Description: Edge Line Equalizer — set every line segment on the
#              Edge.Cuts layer to the same width.
#
##########################################################

import pcbnew


def equalize_edges(board, line_width):
    """Set every line segment on Edge.Cuts to the given width.

    Only straight line segments are touched; other Edge.Cuts items
    (arcs, circles, text) are left alone.

    line_width: mm float. Returns the number of modified lines.
    """
    width_nm = int(round(line_width * 1e6))
    count = 0
    for item in board.GetDrawings():
        try:
            if item.GetLayer() != pcbnew.Edge_Cuts:
                continue
        except Exception:
            continue
        try:
            if item.GetShape() == pcbnew.S_SEGMENT:
                item.SetWidth(width_nm)
                count += 1
        except Exception:
            continue

    board.Refresh()
    return count
