import json
import time
import tkinter as tk
from datetime import date
from pathlib import Path

try:
    import psutil
except ImportError:
    psutil = None

from utils.ui import PanelFrame, compact_bytes, format_bytes, make_label


STATE_FILE = Path.home() / ".cache" / "sysmon-widget" / "network.json"
SAVE_EVERY_TICKS = 30


class NetworkPanel:
    def __init__(self, parent, config):
        self.config = config
        self.net_config = config["network"]
        self.widget = PanelFrame(parent, config)
        self.interface = None
        self.last = None
        self.last_time = None
        self.today_date = date.today().isoformat()
        self.total_down = 0
        self.total_up = 0
        self._save_counter = 0
        self._load_state()

        accent = config["accent"]
        bg = self.widget.cget("bg")

        self.title = make_label(self.widget, config, text="NETWORK", size=9, color=accent["primary"], weight="bold")
        self.title.pack(fill="x")

        row = tk.Frame(self.widget, bg=bg)
        row.pack(fill="x", pady=(4, 0))

        self.down_col = self._make_col(row, "↓ Down")
        self.up_col = self._make_col(row, "↑ Up")

        self.today = make_label(self.widget, config, text="Today: 0B", size=8, color=accent["primary"])
        self.today.pack(fill="x", pady=(4, 0))
        self._refresh_today_label()

        self._tick()

    def _make_col(self, parent, label):
        bg = parent.cget("bg")
        col = tk.Frame(parent, bg=bg)
        col.pack(side="left", fill="both", expand=True)
        accent = self.config["accent"]
        make_label(col, self.config, text=label, size=8, color=accent["text_muted"]).pack(fill="x")
        value = make_label(col, self.config, text="--", size=10, weight="bold")
        value.pack(fill="x", pady=(2, 0))
        return value

    def _tick(self):
        if psutil is None:
            self.down_col.configure(text="n/a")
            self.widget.after(self.net_config["refresh_ms"], self._tick)
            return

        current_date = date.today().isoformat()
        if current_date != self.today_date:
            self.today_date = current_date
            self.total_down = 0
            self.total_up = 0
            self._save_state()

        counter = self._counter()
        now = time.time()
        if counter and self.last:
            elapsed = max(0.001, now - self.last_time)
            down_speed = max(0, counter.bytes_recv - self.last.bytes_recv) / elapsed
            up_speed = max(0, counter.bytes_sent - self.last.bytes_sent) / elapsed
            self.total_down += down_speed * elapsed
            self.total_up += up_speed * elapsed
            self.down_col.configure(text=f"{compact_bytes(down_speed)}/s")
            self.up_col.configure(text=f"{compact_bytes(up_speed)}/s")
            self._refresh_today_label()

            self._save_counter += 1
            if self._save_counter >= SAVE_EVERY_TICKS:
                self._save_state()
                self._save_counter = 0

        self.last = counter
        self.last_time = now
        self.widget.after(self.net_config["refresh_ms"], self._tick)

    def _refresh_today_label(self):
        self.today.configure(text=f"Today: {format_bytes(self.total_down + self.total_up)}")

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

    def _load_state(self):
        try:
            data = json.loads(STATE_FILE.read_text())
        except (OSError, ValueError):
            return
        if data.get("date") == self.today_date:
            self.total_down = float(data.get("total_down", 0) or 0)
            self.total_up = float(data.get("total_up", 0) or 0)

    def _save_state(self):
        try:
            STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            STATE_FILE.write_text(json.dumps({
                "date": self.today_date,
                "total_down": self.total_down,
                "total_up": self.total_up,
            }))
        except OSError:
            pass
