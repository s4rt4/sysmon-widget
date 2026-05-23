import argparse
import tkinter as tk

try:
    import psutil
except ImportError:  # pragma: no cover - startup continues with panel fallbacks
    psutil = None

from config import CONFIG
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
    return parser.parse_args()


def main():
    args = parse_args()
    if psutil is not None:
        psutil.cpu_percent(interval=None)

    root = tk.Tk()
    root.title(WINDOW_TITLE)
    root.overrideredirect(False)
    root.configure(bg=CONFIG["bg_color"])
    root.wm_attributes("-alpha", CONFIG["bg_alpha"])
    root.resizable(False, False)
    try:
        if args.desktop_type:
            root.wm_attributes("-type", "desktop")
        elif not args.managed:
            root.wm_attributes("-type", "splash")
    except tk.TclError:
        pass

    layout = WidgetLayout(root, CONFIG)
    layout.build()
    root.update_idletasks()

    height = max(1, root.winfo_reqheight())
    x, y = calculate_position(root, CONFIG["width"], height)
    root.geometry(f"{CONFIG['width']}x{height}+{x}+{y}")

    root.after(350, lambda: apply_desktop_hints(root.winfo_id(), desktop_type=args.desktop_type, splash_type=not args.managed))
    root.mainloop()


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
