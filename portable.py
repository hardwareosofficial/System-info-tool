"""
portable.py — makes the app work both "installed" (settings in the
user's normal config dir) and "portable" (settings + exports sit next
to the executable, e.g. run from a USB stick, nothing written to the
host machine's profile).

Portable mode is auto-detected: if a file named `portable.flag` exists
next to the running executable/script, everything is kept local to
that folder. This is the same convention used by most well-known
portable Windows utilities (7-Zip portable, Notepad++ portable, etc.).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

APP_NAME = "SystemInfoTool"
SETTINGS_FILENAME = "settings.json"


def _executable_dir() -> Path:
    if getattr(sys, "frozen", False):
        # Running as a PyInstaller-built executable
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def is_portable_mode() -> bool:
    return (_executable_dir() / "portable.flag").exists()


def get_app_data_dir() -> str:
    """
    Where settings + default export location live.

    Portable mode -> a `data` folder next to the executable.
    Installed mode -> the OS's normal per-user config directory.
    """
    if is_portable_mode():
        d = _executable_dir() / "data"
    elif sys.platform.startswith("win"):
        base = os.environ.get("APPDATA") or str(Path.home())
        d = Path(base) / APP_NAME
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
        d = Path(base) / APP_NAME

    d.mkdir(parents=True, exist_ok=True)
    return str(d)


def _settings_path() -> Path:
    return Path(get_app_data_dir()) / SETTINGS_FILENAME


DEFAULT_SETTINGS = {
    "default_share_email": "",
    "smtp": {"host": "", "port": 587, "username": "", "password": "", "use_tls": True},
}


def load_settings() -> dict:
    path = _settings_path()
    if not path.exists():
        return dict(DEFAULT_SETTINGS)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        merged = dict(DEFAULT_SETTINGS)
        merged.update(data)
        return merged
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_SETTINGS)


def save_settings(settings: dict) -> None:
    path = _settings_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
