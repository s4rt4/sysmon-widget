import argparse
import tkinter as tk

try:
    import psutil
except ImportError:  # pragma: no cover - startup continues with panel fallbacks
    psutil = None

from config import CONFIG, THEMES, apply_theme
from utils.autostart import is_autostart_enabled, toggle_autostart
from utils.restart import restart_widget
from utils.settings_dialog import SettingsDialog
from utils.tray import TrayController
from utils.window_shape import apply_panel_shape
from utils.xlib_hints import apply_desktop_hints
from widget import WidgetLayout


WINDOW_TITLE = "sysmon-widget"


def parse_args():
    parser = argparse.ArgumentParser(description="Conky-style desktop system monitor widget.")
    parser.add_argument(
        "--managed",
        action="store_true",
        help="Run as a normal window-manager-managed app window for debugging.",
    )
    parser.add_argument(
        "--desktop-type",
        action="store_true",
        help="Use _NET_WM_WINDOW_TYPE_DESKTOP. On XFCE this may hide behind xfdesktop.",
    )
    parser.add_argument(
        "--theme",
        choices=sorted(THEMES),
        help="Color theme to use.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if args.theme:
        apply_theme(args.theme)
    if psutil is not None:
        psutil.cpu_percent(interval=None)

    root = tk.Tk()
    root.title(WINDOW_TITLE)
    root.overrideredirect(False)
    root.configure(bg=CONFIG["bg_color"])
    root.wm_attributes("-alpha", CONFIG["bg_alpha"])
    root.resizable(False, False)

    if not args.managed:
        root.withdraw()

    layout = WidgetLayout(root, CONFIG)
    layout.build()
    root.update_idletasks()

    height = max(1, root.winfo_reqheight())
    x, y = calculate_position(root, CONFIG["width"], height)
    root.geometry(f"{CONFIG['width']}x{height}+{x}+{y}")

    radius = CONFIG.get("card_radius", 14)
    if not args.managed:
        wid = _get_toplevel_wid(root)
        apply_desktop_hints(
            wid,
            desktop_type=args.desktop_type,
            splash_type=False,
            below=not args.desktop_type,
            undecorated=True,
        )
        root.deiconify()
        root.after(120, lambda: _apply_post_map(root, args, radius))

    tray = _start_tray(root, args, radius)
    try:
        root.mainloop()
    finally:
        if tray is not None:
            tray.stop()


def _apply_post_map(root, args, radius):
    wid = _get_toplevel_wid(root)
    apply_desktop_hints(
        wid,
        desktop_type=args.desktop_type,
        splash_type=False,
        below=not args.desktop_type,
        undecorated=True,
    )
    apply_panel_shape(root, wid=wid, radius=radius)


def _start_tray(root, args, radius):
    state = {"visible": True}
    dialog = SettingsDialog(root, on_saved=lambda: _on_settings_saved(root))
    tray = TrayController(
        root,
        callbacks={
            "toggle_visible": lambda: _toggle_visible(root, args, radius, state, tray_ref),
            "settings": dialog.open,
            "toggle_autostart": lambda: _toggle_autostart(tray_ref),
            "restart": lambda: _do_restart(tray_ref),
            "exit": lambda: _do_exit(root, tray_ref),
            "is_autostart_enabled": is_autostart_enabled,
        },
        accent_color=CONFIG.get("accent", {}).get("primary", "#4DD0E1"),
        bg_color=CONFIG.get("card_bg", "#161a20"),
    )
    tray_ref = {"tray": tray, "state": state}
    if not tray.is_available():
        return None
    tray.start()
    return tray


def _toggle_visible(root, args, radius, state, tray_ref):
    if state["visible"]:
        root.withdraw()
        state["visible"] = False
    else:
        root.deiconify()
        if not args.managed:
            root.after(120, lambda: _apply_post_map(root, args, radius))
        state["visible"] = True
    tray = tray_ref.get("tray") if isinstance(tray_ref, dict) else None
    if tray is not None:
        tray.set_visible(state["visible"])


def _toggle_autostart(tray_ref):
    enabled = toggle_autostart()
    tray = tray_ref.get("tray") if isinstance(tray_ref, dict) else None
    if tray is not None:
        tray.set_autostart(enabled)


def _do_restart(tray_ref):
    tray = tray_ref.get("tray") if isinstance(tray_ref, dict) else None
    if tray is not None:
        tray.stop()
    restart_widget()


def _do_exit(root, tray_ref):
    tray = tray_ref.get("tray") if isinstance(tray_ref, dict) else None
    if tray is not None:
        tray.stop()
    try:
        root.destroy()
    except Exception:
        pass


def _on_settings_saved(root):
    from tkinter import messagebox
    if messagebox.askyesno(
        "Restart widget",
        "Settings saved. Restart widget now to apply changes?",
        parent=root,
    ):
        restart_widget()


def _get_toplevel_wid(root):
    # Tk on X11 creates an inner widget wrapped by an outer toplevel "client"
    # window; winfo_id() returns the inner one but the WM reads properties
    # (Motif hints, _NET_WM_STATE) on the client. The client is the parent
    # of winfo_id() in the X11 tree.
    inner = root.winfo_id()
    try:
        from Xlib import display
        d = display.Display()
        try:
            win = d.create_resource_object("window", inner)
            parent = win.query_tree().parent
            return parent.id
        finally:
            d.close()
    except Exception:
        return inner


def calculate_position(root, width, height):
    position = CONFIG["position"]
    anchor = position.get("anchor", "right")
    y = position.get("y", 30)
    screen_w = root.winfo_screenwidth()
    if anchor == "right":
        x = screen_w - width - position.get("x", 30)
    elif anchor == "center":
        x = (screen_w - width) // 2 + position.get("x", 0)
    else:
        x = position.get("x", 30)
    return max(0, x), max(0, y)


if __name__ == "__main__":
    main()
