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


class FooterPanel:
    def __init__(self, parent, config):
        self.config = config
        self.footer_config = config["footer"]
        self.widget = PanelFrame(parent, config)
        accent = config["accent"]
        bg = self.widget.cget("bg")

        self._brightness_path = self._detect_brightness()

        self.uptime_val = self._make_cell("UPTIME", "--", text_kind="label")
        self.boot_val = self._make_cell("BOOT", "--", text_kind="label")
        self.vol_val = self._make_cell("🔊", "--", text_kind="icon")
        self.brt_val = self._make_cell("☀", "--", text_kind="icon")

        self._tick()

    def _make_cell(self, header, value, text_kind="label"):
        accent = self.config["accent"]
        bg = self.widget.cget("bg")
        cell = tk.Frame(self.widget, bg=bg)
        cell.pack(side="left", fill="both", expand=True)
        color = accent["text_muted"] if text_kind == "label" else accent["primary"]
        size = 10 if text_kind == "label" else 14
        make_label(cell, self.config, text=header, size=size, color=color, weight="bold", anchor="center").pack(fill="x")
        val = make_label(cell, self.config, text=value, size=11, anchor="center")
        val.pack(fill="x", pady=(2, 0))
        return val

    def _tick(self):
        self.uptime_val.configure(text=self._uptime())
        self.boot_val.configure(text=self._boot())
        self.vol_val.configure(text=self._volume())
        self.brt_val.configure(text=self._brightness())
        self.widget.after(self.footer_config["refresh_ms"], self._tick)

    def _uptime(self):
        if psutil is None:
            return "--"
        secs = int(time.time() - psutil.boot_time())
        h, m = divmod(secs // 60, 60)
        if h > 0:
            return f"{h}h {m}m"
        return f"{m}m"

    def _boot(self):
        if psutil is None:
            return "--"
        bt = datetime.fromtimestamp(psutil.boot_time())
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
