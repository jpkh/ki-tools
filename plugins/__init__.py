##########################################################
#
# Script: __init__.py
# Author: Jani Hirvinen (jpkh)
# Contact: jphelirc@gmail.com
# Repository: https://github.com/jpkh/ki-tools
#
# Copyright (c) 2026 Jani Hirvinen
# License: GPL-3.0 - see the LICENSE file
#
# Description: Plugin registration for KI-Tools.
#
##########################################################

from .log_util import log_message

try:
    from .plugin import KiToolsPlugin
    plugin = KiToolsPlugin()
    plugin.register()
    log_message("Plugin initialized successfully.")
except Exception as e:
    log_message(f"Error initializing plugin: {repr(e)}", log_type="ERROR")
