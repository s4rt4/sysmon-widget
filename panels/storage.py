import tkinter as tk

try:
    import psutil
except ImportError:
    psutil = None

from utils.bar_meter import BarMeter
from utils.ui import PanelFrame, format_bytes, make_label


class StoragePanel:
    def __init__(self, parent, config):
        self.config = config
        self.storage_config = config["storage"]
        self.widget = PanelFrame(parent, config)
        self.rows = []
        accent = config["accent"]
        bg = self.widget.cget("bg")

        make_label(self.widget, config, text="STORAGE", size=10, color=accent["secondary"], weight="bold").pack(fill="x")

        body = tk.Frame(self.widget, bg=bg)
        body.pack(fill="x", pady=(6, 0))
        self._build_rows(body)
        self._tick()

    def _build_rows(self, parent):
        accent = self.config["accent"]
        bg = parent.cget("bg")
        for item in self.storage_config["paths"]:
            container = tk.Frame(parent, bg=bg)
            container.pack(fill="x", pady=(0, 4))

            header = tk.Frame(container, bg=bg)
            header.pack(fill="x")
            label = make_label(header, self.config, text=item["label"], size=12, weight="bold")
            pct = make_label(header, self.config, text="--%", size=11, color=accent["text_muted"], anchor="e")
            label.pack(side="left")
            pct.pack(side="right")

            meter = BarMeter(
                container,
                10,
                self.storage_config["bar_height"],
                accent["primary"],
                accent["track_bg"],
                bg,
            )
            meter.canvas.pack(fill="x", pady=(4, 0))

            info = make_label(container, self.config, text="-- / --", size=9, color=accent["text_muted"])
            info.pack(fill="x", pady=(3, 0))

            self.rows.append({"path": item["path"], "pct": pct, "info": info, "meter": meter})

    def _tick(self):
        for row in self.rows:
            if psutil is None:
                row["pct"].configure(text="n/a")
                continue
            try:
                usage = psutil.disk_usage(row["path"])
            except OSError:
                row["pct"].configure(text="n/a")
                row["meter"].animate_to(0)
                continue
            free_gb = usage.free / (1024**3)
            total_gb = usage.total / (1024**3)
            row["pct"].configure(text=f"{usage.percent:.0f}%")
            row["info"].configure(text=f"{free_gb:.0f} GB free / {total_gb:.0f} GB")
            row["meter"].animate_to(usage.percent)
        self.widget.after(self.storage_config["refresh_sec"] * 1000, self._tick)
