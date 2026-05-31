import subprocess
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path

try:
    import psutil
except ImportError:
    psutil = None

from utils.ui import PanelFrame, make_label


ID_MONTHS_SHORT = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
VOLUME_REFRESH_TICKS = 3


class FooterPanel:
    def __init__(self, parent, config):
        self.config = config
        self.footer_config = config["footer"]
        self.widget = PanelFrame(parent, config)
        accent = config["accent"]
        bg = self.widget.cget("bg")

        self._brightness_path = self._detect_brightness()
        self._boot_time = psutil.boot_time() if psutil else None
        self._boot_text = self._format_boot()
        self._volume_text = "--"
        self._volume_counter = VOLUME_REFRESH_TICKS

        self.uptime_val = self._make_cell("UPTIME", "--", text_kind="label")
        self.boot_val = self._make_cell("BOOT", self._boot_text, text_kind="label")
        self.vol_val = self._make_cell("🔊", "--", text_kind="icon")
        self.brt_val = self._make_cell("☀", "--", text_kind="icon")

        self._tick()

    def _make_cell(self, header, value, text_kind="label"):
        accent = self.config["accent"]
        bg = self.widget.cget("bg")
        cell = tk.Frame(self.widget, bg=bg)
        cell.pack(side="left", fill="both", expand=True)
        color = accent["text_muted"] if text_kind == "label" else accent["primary"]
        size = 9 if text_kind == "label" else 13
        make_label(cell, self.config, text=header, size=size, color=color, weight="bold", anchor="center").pack(fill="x")
        val = make_label(cell, self.config, text=value, size=9, anchor="center")
        val.pack(fill="x", pady=(2, 0))
        return val

    def _tick(self):
        self.uptime_val.configure(text=self._uptime())
        self._volume_counter += 1
        if self._volume_counter >= VOLUME_REFRESH_TICKS:
            self._volume_text = self._volume()
            self._volume_counter = 0
        self.vol_val.configure(text=self._volume_text)
        self.brt_val.configure(text=self._brightness())
        self.widget.after(self.footer_config["refresh_ms"], self._tick)

    def _uptime(self):
        if self._boot_time is None:
            return "--"
        secs = int(time.time() - self._boot_time)
        h, m = divmod(secs // 60, 60)
        if h > 0:
            return f"{h}h {m}m"
        return f"{m}m"

    def _format_boot(self):
        if self._boot_time is None:
            return "--"
        bt = datetime.fromtimestamp(self._boot_time)
        return f"{bt.day} {ID_MONTHS_SHORT[bt.month - 1]} {bt.hour:02d}:{bt.minute:02d}"

    def _volume(self):
        try:
            out = subprocess.check_output(
                ["pactl", "get-sink-volume", "@DEFAULT_SINK@"],
                stderr=subprocess.DEVNULL,
                timeout=1,
            ).decode()
            for tok in out.split():
                if tok.endswith("%"):
                    return tok
        except (FileNotFoundError, subprocess.SubprocessError, subprocess.TimeoutExpired):
            pass
        try:
            out = subprocess.check_output(
                ["amixer", "get", "Master"],
                stderr=subprocess.DEVNULL,
                timeout=1,
            ).decode()
            import re
            m = re.search(r"\[(\d+)%\]", out)
            if m:
                return f"{m.group(1)}%"
        except (FileNotFoundError, subprocess.SubprocessError, subprocess.TimeoutExpired):
            pass
        return "--"

    def _brightness(self):
        path = self._brightness_path
        if not path:
            return "--"
        try:
            current = int((path / "brightness").read_text().strip())
            maxv = int((path / "max_brightness").read_text().strip())
            return f"{round(current / maxv * 100)}%"
        except (OSError, ValueError, ZeroDivisionError):
            return "--"

    def _detect_brightness(self):
        configured = self.footer_config.get("brightness_path")
        if configured and configured != "auto":
            p = Path(configured)
            return p if (p / "brightness").exists() else None
        root = Path("/sys/class/backlight")
        if not root.exists():
            return None
        for entry in sorted(root.iterdir()):
            if (entry / "brightness").exists():
                return entry
        return None
