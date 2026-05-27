import sys
from pathlib import Path


AUTOSTART_FILENAME = "sysmon-widget.desktop"
USER_AUTOSTART_PATH = Path.home() / ".config" / "autostart" / AUTOSTART_FILENAME
SYSTEM_AUTOSTART_PATH = Path("/etc/xdg/autostart") / AUTOSTART_FILENAME
SYSTEM_BIN = Path("/usr/bin/sysmon-widget")


def _read_hidden(path):
    try:
        for line in path.read_text().splitlines():
            stripped = line.strip()
            if stripped.lower().startswith("hidden="):
                return stripped.split("=", 1)[1].strip().lower() == "true"
    except Exception:
        pass
    return False


def is_autostart_enabled():
    if USER_AUTOSTART_PATH.exists():
        return not _read_hidden(USER_AUTOSTART_PATH)
    return SYSTEM_AUTOSTART_PATH.exists()


def _exec_line():
    if SYSTEM_BIN.exists():
        return str(SYSTEM_BIN)
    main_py = Path(__file__).resolve().parent.parent / "main.py"
    python = sys.executable or "python3"
    return f"{python} {main_py}"


def _user_desktop_content(hidden):
    if hidden:
        return (
            "[Desktop Entry]\n"
            "Type=Application\n"
            "Name=sysmon-widget\n"
            "Hidden=true\n"
        )
    return (
        "[Desktop Entry]\n"
        "Type=Application\n"
        "Name=sysmon-widget\n"
        "Comment=Conky-style desktop system monitor\n"
        f"Exec={_exec_line()}\n"
        "Icon=utilities-system-monitor\n"
        "Terminal=false\n"
        "StartupNotify=false\n"
        "X-GNOME-Autostart-enabled=true\n"
        "Categories=System;\n"
    )


def _write_user_file(hidden):
    USER_AUTOSTART_PATH.parent.mkdir(parents=True, exist_ok=True)
    USER_AUTOSTART_PATH.write_text(_user_desktop_content(hidden))


def enable_autostart():
    if SYSTEM_AUTOSTART_PATH.exists():
        if USER_AUTOSTART_PATH.exists():
            USER_AUTOSTART_PATH.unlink()
    else:
        _write_user_file(hidden=False)


def disable_autostart():
    if SYSTEM_AUTOSTART_PATH.exists():
        _write_user_file(hidden=True)
    elif USER_AUTOSTART_PATH.exists():
        USER_AUTOSTART_PATH.unlink()


def toggle_autostart():
    if is_autostart_enabled():
        disable_autostart()
    else:
        enable_autostart()
    return is_autostart_enabled()
