import time
import tkinter as tk

try:
    import psutil
except ImportError:  # pragma: no cover
    psutil = None

from utils.sparkline import Sparkline
from utils.ui import PanelFrame, format_bytes, make_label


class NetworkPanel:
    def __init__(self, parent, config):
        self.config = config
        self.net_config = config["network"]
        self.widget = PanelFrame(parent, config)
        self.interface = None
        self.last = None
        self.last_time = None
        self.total_down = 0
        self.total_up = 0

        self.down = self._make_row("↓")
        self.up = self._make_row("↑")
        self._tick()

    def _make_row(self, label):
        row = tk.Frame(self.widget, bg=self.widget.cget("bg"))
        row.pack(fill="x", pady=2)
        icon = make_label(row, self.config, text=label, size=13, color=self.config["accent"]["primary"])
        value = make_label(row, self.config, text="--", size=11)
        total = make_label(row, self.config, text="0B", size=10, color=self.config["accent"]["text_muted"], anchor="e")
        spark = Sparkline(row, 92, 24, self.net_config["history_len"], self.config["accent"]["primary"], self.widget.cget("bg"))
        icon.pack(side="left")
        value.pack(side="left", padx=(8, 6))
        spark.canvas.pack(side="left", fill="x", expand=True)
        total.pack(side="right")
        return {"value": value, "total": total, "spark": spark}

    def _tick(self):
        if psutil is None:
            self.down["value"].configure(text="psutil missing")
            self.widget.after(self.net_config["refresh_ms"], self._tick)
            return

        counter = self._counter()
        now = time.time()
        if counter and self.last:
            elapsed = max(0.001, now - self.last_time)
            down_speed = max(0, counter.bytes_recv - self.last.bytes_recv) / elapsed
            up_speed = max(0, counter.bytes_sent - self.last.bytes_sent) / elapsed
            self.total_down += down_speed * elapsed
            self.total_up += up_speed * elapsed
            self.down["value"].configure(text=format_bytes(down_speed) + "/s")
            self.up["value"].configure(text=format_bytes(up_speed) + "/s")
            self.down["total"].configure(text=format_bytes(self.total_down))
            self.up["total"].configure(text=format_bytes(self.total_up))
            self.down["spark"].push(down_speed)
            self.up["spark"].push(up_speed)
        self.last = counter
        self.last_time = now
        self.widget.after(self.net_config["refresh_ms"], self._tick)

    def _counter(self):
        if self.net_config["interface"] == "auto":
            self.interface = self._active_interface()
        else:
            self.interface = self.net_config["interface"]
        if self.interface is None:
            return None
        counters = psutil.net_io_counters(pernic=True)
        return counters.get(self.interface)

    def _active_interface(self):
        counters = psutil.net_io_counters(pernic=True)
        candidates = [(name, c.bytes_recv + c.bytes_sent) for name, c in counters.items() if name != "lo"]
        if not candidates:
            return None
        return max(candidates, key=lambda item: item[1])[0]
