import tkinter as tk

from utils.ui import make_separator
from panels.clock import ClockPanel
from panels.music import MusicPanel
from panels.network import NetworkPanel
from panels.storage import StoragePanel
from panels.sysstat import SysStatPanel
from panels.weather import WeatherPanel


PANEL_CLASSES = {
    "clock": ClockPanel,
    "weather": WeatherPanel,
    "network": NetworkPanel,
    "sysstat": SysStatPanel,
    "storage": StoragePanel,
    "music": MusicPanel,
}


class WidgetLayout:
    def __init__(self, root, config):
        self.root = root
        self.config = config
        self.panels = []

    def build(self):
        frame = tk.Frame(self.root, bg=self.config["bg_color"], width=self.config["width"])
        frame.pack(fill="both", expand=True)

        enabled = self.config["panels"]
        first = True
        for name, panel_class in PANEL_CLASSES.items():
            if not enabled.get(name, False):
                continue
            if not first:
                make_separator(frame, self.config).pack(fill="x", padx=14)
            panel = panel_class(frame, self.config)
            panel.widget.pack(fill="x")
            self.panels.append(panel)
            first = False
