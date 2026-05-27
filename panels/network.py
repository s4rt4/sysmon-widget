import time
import tkinter as tk

try:
    import psutil
except ImportError:
    psutil = None

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

        accent = config["accent"]
        bg = self.widget.cget("bg")

        self.title = make_label(self.widget, config, text="NETWORK", size=10, color=accent["primary"], weight="bold")
        self.title.pack(fill="x")

        row = tk.Frame(self.widget, bg=bg)
        row.pack(fill="x", pady=(6, 0))

        self.down_col = self._make_col(row, "Download")
        self.up_col = self._make_col(row, "Upload")

        self.today = make_label(self.widget, config, text="Today: 0 B", size=10, color=accent["primary"])
        self.today.pack(fill="x", pady=(6, 0))

        self._tick()

    def _make_col(self, parent, label):
        bg = parent.cget("bg")
        col = tk.Frame(parent, bg=bg)
        col.pack(side="left", fill="both", expand=True)
        accent = self.config["accent"]
        make_label(col, self.config, text=label, size=10, color=accent["text_muted"]).pack(fill="x")
        value = make_label(col, self.config, text="-- KB/s", size=12, weight="bold")
        value.pack(fill="x", pady=(2, 0))
        return value

    def _tick(self):
        if psutil is None:
            self.down_col.configure(text="n/a")
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
            self.down_col.configure(text=f"{format_bytes(down_speed)}/s")
            self.up_col.configure(text=f"{format_bytes(up_speed)}/s")
            self.today.configure(text=f"Today: {format_bytes(self.total_down + self.total_up)}")
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
