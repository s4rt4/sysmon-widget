import os
import sys
from pathlib import Path


AUTOSTART_PATH = Path.home() / ".config" / "autostart" / "sysmon-widget.desktop"


def is_autostart_enabled():
    return AUTOSTART_PATH.exists()


def enable_autostart():
    AUTOSTART_PATH.parent.mkdir(parents=True, exist_ok=True)
    exec_line = _exec_line()
    content = (
        "[Desktop Entry]\n"
        "Type=Application\n"
        "Name=sysmon-widget\n"
        "Comment=Conky-style desktop system monitor\n"
        f"Exec={exec_line}\n"
        "Icon=utilities-system-monitor\n"
        "Terminal=false\n"
        "X-GNOME-Autostart-enabled=true\n"
        "Categories=System;\n"
    )
    AUTOSTART_PATH.write_text(content)


def disable_autostart():
    if AUTOSTART_PATH.exists():
        AUTOSTART_PATH.unlink()


def toggle_autostart():
    if is_autostart_enabled():
        disable_autostart()
    else:
        enable_autostart()
    return is_autostart_enabled()


def _exec_line():
    main_py = Path(__file__).resolve().parent.parent / "main.py"
    python = sys.executable or "python3"
    return f"{python} {main_py}"
