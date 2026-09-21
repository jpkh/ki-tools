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


def _board_vias(board):
    """Yield the board's vias, KiCad 7-10 compatible.

    Older bindings expose BOARD.GetVias(); newer ones only return vias
    through BOARD.GetTracks().
    """
    get_vias = getattr(board, 'GetVias', None)
    if get_vias is not None:
        for via in get_vias():
            yield via
        return
    for track in board.GetTracks():
        if hasattr(track, 'GetDrillValue') or hasattr(track, 'GetDrill'):
            yield track


def _via_drill(via):
    """Drill size in nm, compatible with KiCad 7-10 SWIG bindings."""
    for name in ('GetDrillValue', 'GetDrill'):
        fn = getattr(via, name, None)
        if fn is not None:
            return fn()
    raise AttributeError("no drill getter on via object")


def _set_via_drill(via, value_nm):
    for name in ('SetDrillValue', 'SetDrill'):
        fn = getattr(via, name, None)
        if fn is not None:
            fn(value_nm)
            return
    raise AttributeError("no drill setter on via object")


def count_vias(board, old_diameter, old_drill):
    """Count vias matching the exact old diameter and drill. mm values."""
    old_d_nm = int(round(old_diameter * 1e6))
    old_drill_nm = int(round(old_drill * 1e6))

    count = 0
    for via in _board_vias(board):
        if via.GetWidth() == old_d_nm and _via_drill(via) == old_drill_nm:
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
    for via in _board_vias(board):
        if via.GetWidth() == old_d_nm and _via_drill(via) == old_drill_nm:
            via.SetWidth(new_d_nm)
            _set_via_drill(via, new_drill_nm)
            count += 1

    pcbnew.Refresh()
    return count
