from datetime import datetime
import tkinter as tk

from utils.ui import PanelFrame, make_label


ID_DAYS = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
ID_MONTHS = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]


class ClockPanel:
    def __init__(self, parent, config):
        self.config = config
        self.widget = PanelFrame(parent, config)
        clock_config = config["clock"]
        accent = config["accent"]

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

        self._tick()

    def _tick(self):
        fmt = "%H:%M:%S" if self.config["clock"]["show_seconds"] else "%H:%M"
        now = datetime.now()
        self.time_label.configure(text=now.strftime(fmt))
        self.day_label.configure(text=ID_DAYS[now.weekday()])
        self.date_label.configure(text=f"{now.day} {ID_MONTHS[now.month - 1]} {now.year}")
        self.seconds_label.configure(text=f"{now.second:02d}")
        self.widget.after(1000, self._tick)
