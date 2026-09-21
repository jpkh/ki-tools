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


def _board_drawings(board):
    """Yield the board's drawing items, KiCad 7-10 compatible.

    Newer bindings may drop BOARD.GetDrawings(); fall back to iterating
    all board items via GetItems().
    """
    get_drawings = getattr(board, 'GetDrawings', None)
    if get_drawings is not None:
        for item in get_drawings():
            yield item
        return
    get_items = getattr(board, 'GetItems', None)
    if get_items is not None:
        for item in get_items():
            yield item


def equalize_edges(board, line_width):
    """Set every line segment on Edge.Cuts to the given width.

    Only straight line segments are touched; other Edge.Cuts items
    (arcs, circles, text) are left alone.

    line_width: mm float. Returns the number of modified lines.
    """
    width_nm = int(round(line_width * 1e6))
    count = 0
    for item in _board_drawings(board):
        try:
            if item.GetLayer() != pcbnew.Edge_Cuts:
                continue
        except Exception:
            continue
        try:
            shape_fn = getattr(item, 'GetShape', None)
            if shape_fn is None or shape_fn() != pcbnew.S_SEGMENT:
                continue
            item.SetWidth(width_nm)
            count += 1
        except Exception:
            continue

    board.Refresh()
    return count
