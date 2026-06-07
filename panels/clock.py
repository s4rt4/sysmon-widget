from datetime import datetime
import tkinter as tk

from utils.ui import PanelFrame, make_label


ID_DAYS = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
ID_MONTHS = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]


class ClockPanel:
    def __init__(self, parent, config, controls=None):
        self.config = config
        self.controls = controls
        self.widget = PanelFrame(parent, config)
        clock_config = config["clock"]
        accent = config["accent"]
        self._autostart_var = tk.BooleanVar(value=False)

        bg = self.widget.cget("bg")

        self.time_label = make_label(
            self.widget,
            config,
            size=clock_config["time_font_size"],
            color=accent["text_main"],
            weight="bold",
            anchor="w",
        )
        self.time_label.pack(side="left", padx=(0, 12))

        sep = tk.Frame(self.widget, bg=config["separator_color"], width=1)
        sep.pack(side="left", fill="y", padx=(0, 12), pady=4)

        right = tk.Frame(self.widget, bg=bg)
        right.pack(side="left", fill="both", expand=True)

        self.day_label = make_label(
            right,
            config,
            size=clock_config["day_font_size"],
            color=accent["primary"],
            weight="bold",
            anchor="w",
        )
        self.day_label.pack(fill="x")
        self.date_label = make_label(
            right,
            config,
            size=clock_config["date_font_size"],
            color=accent["text_main"],
            anchor="w",
        )
        self.date_label.pack(fill="x", pady=(2, 0))
        self.seconds_label = make_label(
            right,
            config,
            size=11,
            color=accent["text_muted"],
            anchor="w",
        )
        self.seconds_label.pack(fill="x", pady=(2, 0))

        # Gear control lives in the top-right corner (primary control surface on
        # desktops without a tray, e.g. GNOME). Inset to clear the rounded corner.
        if controls:
            self._build_gear(bg)

        self._tick()

    def _build_gear(self, bg):
        accent = self.config["accent"]
        self.gear = tk.Label(
            self.widget,
            text="⚙",
            bg=bg,
            fg=accent["text_muted"],
            font=(self.config["clock"]["font"], 13),
            cursor="hand2",
        )
        self.gear.place(relx=1.0, y=4, x=-8, anchor="ne")
        self.gear.bind("<Button-1>", self._popup_menu)
        self.gear.bind("<Enter>", lambda e: self.gear.configure(fg=accent["primary"]))
        self.gear.bind("<Leave>", lambda e: self.gear.configure(fg=accent["text_muted"]))

    def _popup_menu(self, event):
        controls = self.controls or {}
        menu = tk.Menu(self.widget, tearoff=0)
        settings = controls.get("settings")
        if settings:
            menu.add_command(label="Settings…", command=settings)
        toggle_autostart = controls.get("toggle_autostart")
        if toggle_autostart:
            try:
                self._autostart_var.set(bool(controls.get("is_autostart_enabled", lambda: False)()))
            except Exception:
                self._autostart_var.set(False)
            menu.add_checkbutton(label="Autostart", variable=self._autostart_var, command=toggle_autostart)
        restart = controls.get("restart")
        exit_cb = controls.get("exit")
        if (settings or toggle_autostart) and (restart or exit_cb):
            menu.add_separator()
        if restart:
            menu.add_command(label="Restart widget", command=restart)
        if exit_cb:
            menu.add_command(label="Exit", command=exit_cb)
        # Dismiss when focus leaves (click on empty area / another window). The
        # usual try/finally grab_release() breaks click-away dismissal on
        # XWayland/mutter, so we rely on FocusOut instead.
        menu.bind("<FocusOut>", lambda e: menu.unpost())
        menu.tk_popup(event.x_root, event.y_root)

    def _tick(self):
        fmt = "%H:%M:%S" if self.config["clock"]["show_seconds"] else "%H:%M"
        now = datetime.now()
        self.time_label.configure(text=now.strftime(fmt))
        self.day_label.configure(text=ID_DAYS[now.weekday()])
        self.date_label.configure(text=f"{now.day} {ID_MONTHS[now.month - 1]} {now.year}")
        self.seconds_label.configure(text=f"{now.second:02d}")
        self.widget.after(1000, self._tick)
