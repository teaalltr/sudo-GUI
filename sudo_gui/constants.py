from __future__ import annotations
import re
from PyQt6.QtGui import QColor, QPalette

SUDOERS_PATH = "/etc/sudoers"

DEFAULT_RE = re.compile(r"^Defaults\s+(.*)")
ALIAS_RE   = re.compile(r"^(User|Runas|Host|Cmnd)_Alias\s+(\w+)\s*=\s*(.*)")

BoolDefault = {
    "env_reset", "authenticate", "lecture", "tty_tickets", "set_home",
    "requiretty", "visiblepw", "rootpw", "runaspw", "targetpw",
    "log_input", "log_output", "use_pty"
}

DEFAULTS_META: dict[str, dict] = {
    "env_reset": {
        "desc": "Reset most environment variables to a safe default set "
                "before running the command.",
        "type": "bool",
    },
    "mail_badpass": {
        "desc": "Send mail to the mailto user if an incorrect password is "
                "entered.",
        "type": "bool",
    },
    "secure_path": {
        "desc": "Overrides the user's PATH when a command is run via sudo. "
                "Separate directories with ':' (colon).",
        "type": "path",
    },
    "use_pty": {
        "desc": "Run the command in a new pseudo-terminal (recommended for "
                "logging/forensics).",
        "type": "bool",
    },
    "lecture": {
        "desc": "Whether sudo should lecture the user about its dangers.",
        "type": "enum",
        "choices": ["always", "once", "never"],
    },
    "timestamp_timeout": {
        "desc": "Minutes before sudo asks for the password again. -1 means "
                "‘never time-out’.",
        "type": "int",
        "min": -1,
        "max": 999,
    },
}
