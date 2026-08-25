##########################################################
#
# Script: tools.py
# Author: Jani Hirvinen (jpkh)
# Contact: jphelirc@gmail.com
# Repository: https://github.com/jpkh/ki-tools
#
# Copyright (c) 2026 Jani Hirvinen
# License: GPL-3.0 - see the LICENSE file
#
# Description: PCB editing tool implementations. One function per tool.
#              The dialog stays thin; all board manipulation lives here.
#
##########################################################


def fix_fonts(board, font_size, line_thickness, visible, layers):
    """Set every text item on the given layers to the same font size,
    line thickness and visibility.

    fixfonts(x, y, z): x = font size, y = line thickness, z = visible 0/1.

    Returns the number of modified text items.

    TODO: port from the original fixfonts script (tmp/).
    """
    raise NotImplementedError("fix_fonts: original script not ported yet")


def edge_line_equalizer(board):
    """Equalize the width of the board edge lines.

    TODO: check whether KiCad edge lines can be modified this way.
    """
    raise NotImplementedError("edge_line_equalizer: not implemented yet")


def fiducial_grid(board):
    """Place fiducials on a grid.

    TODO: design the parameters first.
    """
    raise NotImplementedError("fiducial_grid: not implemented yet")


def fix_vias(board):
    """Fix via properties.

    TODO: check what the original fixvia script did.
    """
    raise NotImplementedError("fix_vias: not implemented yet")
