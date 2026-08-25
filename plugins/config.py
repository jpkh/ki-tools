##########################################################
#
# Script: config.py
# Author: Jani Hirvinen (jpkh)
# Contact: jphelirc@gmail.com
# Repository: https://github.com/jpkh/ki-tools
#
# Copyright (c) 2026 Jani Hirvinen
# License: GPL-3.0 - see the LICENSE file
#
# Description: Defaults: tool options, settings filename, plugin version.
#
##########################################################

settingsFileName = 'ki-tools-options.json'

# Shown in the dialog title; bump together with metadata.json
plugin_version = '0.1.0'
plugin_date = '2026-08-25'

# Defaults for every tool. The dialog restores these on first run and
# saves the last used values back to the settings file.
DEFAULT_OPTIONS = {
    # Text Size Fixer (ported from fixcompnamesize.py)
    'textsizer': {
        'text_size': 0.8,        # mm, footprint reference/value text height
        'thickness': 0.1,        # mm, text stroke width
        'visible': True,         # False = hide the text items
        'layers': {              # layer name -> enabled
            'F.SilkS': True,
            'B.SilkS': True,
            'F.Fab': False,
            'B.Fab': False,
        },
    },
    # Fix Vias (ported from fixvia.py)
    'fixvia': {
        'old_diameter': 0.6,     # mm
        'new_diameter': 0.45,    # mm
        'old_drill': 0.3,        # mm
        'new_drill': 0.3,        # mm
    },
}
