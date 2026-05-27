import tkinter as tk

try:
    import psutil
except ImportError:
    psutil = None

from utils.ring_gauge import RingGauge
from utils.ui import PanelFrame, make_label


class SysStatPanel:
    def __init__(self, parent, config):
        self.config = config
        self.sys_config = config["sysstat"]
        self.widget = PanelFrame(parent, config)
        self.gauges = {}
        self._build()
        self._tick()

    def _build(self):
        bg = self.widget.cget("bg")
        accent = self.config["accent"]
        row = tk.Frame(self.widget, bg=bg)
        row.pack(fill="x")
        for key, label, color in self._gauge_defs():
            cell = tk.Frame(row, bg=bg)
            cell.pack(side="left", expand=True, fill="both")
            gauge = RingGauge(
                cell,
                self.sys_config["ring_size"],
                self.sys_config["ring_width"],
                color or accent["primary"],
                accent["track_bg"],
                accent["text_main"],
                bg,
                font_size=8,
            )
            gauge.canvas.pack()
            make_label(
                cell,
                self.config,
                text=label,
                size=9,
                color=accent["text_muted"],
                anchor="center",
                weight="bold",
            ).pack(pady=(4, 0))
            self.gauges[key] = gauge

    def _gauge_defs(self):
        accent = self.config["accent"]
        return [
            ("cpu", "CPU", self.sys_config.get("cpu_color") or accent["primary"]),
            ("ram", "RAM", self.sys_config.get("ram_color") or accent["secondary"]),
            ("battery", "BAT", self.sys_config.get("battery_color") or "#34D399"),
            ("temp", "TEMP", self.sys_config.get("temp_color") or "#F97316"),
        ]

    def _tick(self):
        values = self._values()
        for key, gauge in self.gauges.items():
            pct, label = values.get(key, (0, "--"))
            gauge.animate_to(pct, label)
        self.widget.after(self.sys_config["refresh_ms"], self._tick)

    def _values(self):
        if psutil is None:
            return {key: (0, "--") for key in self.gauges}
        battery = psutil.sensors_battery() if self.sys_config["show_battery"] else None
        temp = self._temperature() if self.sys_config["show_temp"] else None
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        return {
            "cpu": (cpu, f"{cpu:.0f}%"),
            "ram": (ram, f"{ram:.0f}%"),
            "battery": (battery.percent if battery else 0, f"{battery.percent:.0f}%" if battery else "--"),
            "temp": (min(100, temp) if temp is not None else 0, f"{temp:.0f}C" if temp is not None else "--"),
        }

    def _temperature(self):
        try:
            temps = psutil.sensors_temperatures()
        except Exception:
            return None
        for entries in temps.values():
            for entry in entries:
                if entry.current is not None:
                    return float(entry.current)
        return None
