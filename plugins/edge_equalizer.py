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


# Shape constants handled by the equalizer (PCB_SHAPE shapes)
_SHAPES = {
    'lines': 'S_SEGMENT',
    'arcs': 'S_ARC',
    'rects': 'S_RECT',
    'circles': 'S_CIRCLE',
    'polygons': 'S_POLYGON',
}


def equalize_edges(board, line_width):
    """Set the outline width of every drawing shape on Edge.Cuts.

    Lines, arcs, rectangles, circles and polygons are changed; other
    Edge.Cuts items (text) are left alone.

    line_width: mm float. Returns a dict of changed counts per shape type.
    """
    width_nm = int(round(line_width * 1e6))
    counts = {key: 0 for key in _SHAPES}

    shape_consts = {}
    for key, const_name in _SHAPES.items():
        const = getattr(pcbnew, const_name, None)
        if const is not None:
            shape_consts[const] = key

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
            key = shape_consts.get(shape_fn())
            if key is None:
                continue
            item.SetWidth(width_nm)
            counts[key] += 1
        except Exception:
            continue

    pcbnew.Refresh()
    return counts
