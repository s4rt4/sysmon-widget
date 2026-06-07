import threading

try:
    import pystray
    from pystray import Menu, MenuItem
    from PIL import Image, ImageDraw
except Exception:
    pystray = None


def _make_icon_image(size=64, fg="#4DD0E1", bg="#161a20"):
    image = Image.new("RGBA", (size, size), bg)
    draw = ImageDraw.Draw(image)
    pad = size // 8
    draw.rounded_rectangle(
        (pad, pad, size - pad, size - pad),
        radius=size // 6,
        outline=fg,
        width=max(2, size // 16),
    )
    bar_w = (size - 2 * pad - 4 * 3) // 4
    base_y = size - pad - max(2, size // 12)
    heights = [size // 5, size // 3, size // 4, size // 2]
    x = pad + 3
    for h in heights:
        draw.rectangle((x, base_y - h, x + bar_w, base_y), fill=fg)
        x += bar_w + 3
    return image


class TrayController:
    def __init__(self, root, callbacks, accent_color="#4DD0E1", bg_color="#161a20"):
        self._root = root
        self._callbacks = callbacks
        self._icon = None
        self._thread = None
        self._visible = True
        self._autostart_state = bool(callbacks.get("is_autostart_enabled", lambda: False)())
        self._accent = accent_color
        self._bg = bg_color

    def is_available(self):
        return pystray is not None

    def start(self):
        if not self.is_available():
            return False
        image = _make_icon_image(fg=self._accent, bg=self._bg)
        self._icon = pystray.Icon(
            "sysmon-widget",
            image,
            "sysmon-widget",
            menu=self._build_menu(),
        )
        self._thread = threading.Thread(target=self._run_icon, daemon=True)
        self._thread.start()
        return True

    def _run_icon(self):
        # The GTK/AppIndicator backend installs a SIGINT handler, which only
        # works on the main thread; that thread belongs to Tk's mainloop here,
        # so a background-thread tray cannot run. On GNOME there is no tray host
        # anyway -- the in-widget gear menu is the control surface. Fail quietly
        # instead of dumping a traceback from the worker thread.
        try:
            self._icon.run()
        except Exception as exc:
            print(f"Tray unavailable, using the gear menu instead: {exc}", flush=True)
            self._icon = None

    def stop(self):
        if self._icon is not None:
            try:
                self._icon.stop()
            except Exception:
                pass
            self._icon = None

    def set_visible(self, visible):
        self._visible = bool(visible)
        self._refresh_menu()

    def set_autostart(self, enabled):
        self._autostart_state = bool(enabled)
        self._refresh_menu()

    def _refresh_menu(self):
        if self._icon is None:
            return
        try:
            self._icon.menu = self._build_menu()
            self._icon.update_menu()
        except Exception:
            pass

    def _build_menu(self):
        return Menu(
            MenuItem(
                "Hide" if self._visible else "Show",
                self._on_toggle_visible,
                default=True,
            ),
            MenuItem("Settings...", self._on_settings),
            Menu.SEPARATOR,
            MenuItem(
                "Autostart",
                self._on_toggle_autostart,
                checked=lambda item: self._autostart_state,
            ),
            MenuItem("Restart widget", self._on_restart),
            Menu.SEPARATOR,
            MenuItem("Exit", self._on_exit),
        )

    def _marshal(self, name):
        cb = self._callbacks.get(name)
        if cb is None:
            return
        try:
            self._root.after(0, cb)
        except Exception:
            pass

    def _on_toggle_visible(self, icon, item):
        self._marshal("toggle_visible")

    def _on_settings(self, icon, item):
        self._marshal("settings")

    def _on_toggle_autostart(self, icon, item):
        self._marshal("toggle_autostart")

    def _on_restart(self, icon, item):
        self._marshal("restart")

    def _on_exit(self, icon, item):
        self._marshal("exit")
