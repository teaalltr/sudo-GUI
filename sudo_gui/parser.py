from __future__ import annotations
import re
import subprocess
from pathlib import Path
from typing import List, Tuple
from .constants import DEFAULT_RE, ALIAS_RE

def parse_sudoers(text: str):
    defaults: List[str] = []
    aliases: List[Tuple[str, str, str]] = []
    rules: List[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or not stripped:
            rules.append(line)
            continue
        if m := DEFAULT_RE.match(stripped):
            defaults.append(m.group(1))
        elif m := ALIAS_RE.match(stripped):
            aliases.append((m.group(1), m.group(2), m.group(3)))
        else:
            rules.append(line)
    return defaults, aliases, rules

def get_plugins():
    try:
        out = subprocess.check_output(["sudo", "-V"], text=True, stderr=subprocess.STDOUT)
    except Exception as e:
        return [("Error", str(e))]
    plugs, grab = [], False
    for ln in out.splitlines():
        if ln.strip().startswith("Plugin options"):
            break
        if grab and ln.strip():
            m = re.match(r"\s*(\S+)\s*:\s*(.*)", ln)
            if m:
                plugs.append((m.group(1), m.group(2)))
        if ln.strip().startswith("Plugins:"):
            grab = True
    return plugs or [("None detected", "")]