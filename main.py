import argparse
import tkinter as tk

try:
    import psutil
except ImportError:  # pragma: no cover - startup continues with panel fallbacks
    psutil = None

from config import CONFIG, THEMES, apply_theme
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
        radius = CONFIG.get("card_radius", 14)
        root.after(120, lambda: _apply_post_map(root, args, radius))
    root.mainloop()


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
    y = position.get("y", 30)
    if position.get("anchor") == "right":
        x = root.winfo_screenwidth() - width - position.get("x", 30)
    else:
        x = position.get("x", 30)
    return max(0, x), max(0, y)


if __name__ == "__main__":
    main()
