import tkinter as tk

try:
    import psutil
except ImportError:  # pragma: no cover
    psutil = None

from utils.bar_meter import BarMeter
from utils.ui import PanelFrame, make_label


class StoragePanel:
    def __init__(self, parent, config):
        self.config = config
        self.storage_config = config["storage"]
        self.widget = PanelFrame(parent, config)
        self.rows = []
        make_label(self.widget, config, text="Storage", size=12, weight="bold").pack(fill="x")
        self._build_rows()
        self._tick()

    def _build_rows(self):
        for item in self.storage_config["paths"]:
            row = tk.Frame(self.widget, bg=self.widget.cget("bg"))
            row.pack(fill="x", pady=(8, 0))
            header = tk.Frame(row, bg=self.widget.cget("bg"))
            header.pack(fill="x")
            label = make_label(header, self.config, text=item["label"], size=10)
            value = make_label(header, self.config, text="--", size=10, color=self.config["accent"]["text_muted"], anchor="e")
            label.pack(side="left")
            value.pack(side="right")
            meter = BarMeter(
                row,
                self.config["width"] - self.config["panel_padding"] * 2,
                self.storage_config["bar_height"],
                self.config["accent"]["primary"],
                self.config["bg_color"],
                self.widget.cget("bg"),
            )
            meter.canvas.pack(fill="x", pady=(5, 0))
            self.rows.append({"path": item["path"], "value": value, "meter": meter})

    def _tick(self):
        for row in self.rows:
            if psutil is None:
                row["value"].configure(text="psutil missing")
                continue
            try:
                usage = psutil.disk_usage(row["path"])
            except OSError:
                row["value"].configure(text="unavailable")
                row["meter"].animate_to(0)
                continue
            total_gib = usage.total / (1024**3)
            row["value"].configure(text=f"{usage.percent:.0f}% ({total_gib:.1f} GiB)")
            row["meter"].animate_to(usage.percent)
        self.widget.after(self.storage_config["refresh_sec"] * 1000, self._tick)
