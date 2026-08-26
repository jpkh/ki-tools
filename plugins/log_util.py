##########################################################
#
# Script: log_util.py
# Author: Jani Hirvinen (jpkh)
# Contact: jphelirc@gmail.com
# Repository: https://github.com/jpkh/ki-tools
#
# Copyright (c) 2026 Jani Hirvinen
# License: GPL-3.0 - see the LICENSE file
#
# Description: Logging helper.
#
##########################################################

import pcbnew

def log_message(message, log_type="INFO"):
    """Logs a message in the KiCad scripting console. Never raises."""
    full_message = f"[KI-Tools] [{log_type}] {message}"
    print(full_message)  # Prints to KiCad's scripting console
    try:
        pcbnew.GetKernel().GetLogManager().Log(full_message)
    except Exception:
        pass  # Logging must never break a tool
