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
    """Set every line and arc on Edge.Cuts to the given width.

    Other Edge.Cuts items (circles, text) are left alone.

    line_width: mm float. Returns (lines_changed, arcs_changed).
    """
    width_nm = int(round(line_width * 1e6))
    lines = 0
    arcs = 0
    for item in _board_drawings(board):
        try:
            if item.GetLayer() != pcbnew.Edge_Cuts:
                continue
        except Exception:
            continue
        try:
            shape_fn = getattr(item, 'GetShape', None)
            if shape_fn is None:
                continue
            shape = shape_fn()
            if shape == pcbnew.S_SEGMENT:
                item.SetWidth(width_nm)
                lines += 1
            elif shape == pcbnew.S_ARC:
                item.SetWidth(width_nm)
                arcs += 1
        except Exception:
            continue

    pcbnew.Refresh()
    return lines, arcs
