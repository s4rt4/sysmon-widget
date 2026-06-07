import tkinter as tk

from panels.clock import ClockPanel
from panels.footer import FooterPanel
from panels.music import MusicPanel
from panels.network import NetworkPanel
from panels.processes import ProcessesPanel
from panels.storage import StoragePanel
from panels.sysstat import SysStatPanel
from panels.weather import WeatherPanel


PANEL_CLASSES = {
    "clock": ClockPanel,
    "weather": WeatherPanel,
    "network": NetworkPanel,
    "sysstat": SysStatPanel,
    "music": MusicPanel,
    "storage": StoragePanel,
    "processes": ProcessesPanel,
    "footer": FooterPanel,
}


# (panel_key, row, col, colspan)
GRID = [
    ("clock", 0, 0, 2),
    ("weather", 1, 0, 1),
    ("network", 1, 1, 1),
    ("sysstat", 2, 0, 2),
    ("music", 3, 0, 2),
    ("storage", 4, 0, 1),
    ("processes", 4, 1, 1),
    ("footer", 5, 0, 2),
]


class WidgetLayout:
    def __init__(self, root, config, controls=None):
        self.root = root
        self.config = config
        self.controls = controls
        self.panels = []

    def build(self):
        outer = self.config.get("outer_pad", 4)
        gap = self.config.get("card_gap", 6)

        container = tk.Frame(self.root, bg=self.config["bg_color"], padx=outer, pady=outer)
        container.pack(fill="both", expand=True)
        container.grid_columnconfigure(0, weight=1, uniform="col")
        container.grid_columnconfigure(1, weight=1, uniform="col")

        enabled = self.config["panels"]
        for key, row, col, colspan in GRID:
            if not enabled.get(key, False):
                continue
            panel_class = PANEL_CLASSES[key]
            if key == "clock":
                panel = panel_class(container, self.config, controls=self.controls)
            else:
                panel = panel_class(container, self.config)
            panel.widget.grid(
                row=row,
                column=col,
                columnspan=colspan,
                sticky="nsew",
                padx=gap // 2,
                pady=gap // 2,
            )
            self.panels.append(panel)
