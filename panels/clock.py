from datetime import datetime

from utils.ui import PanelFrame, make_label


class ClockPanel:
    def __init__(self, parent, config):
        self.config = config
        self.widget = PanelFrame(parent, config)
        clock_config = config["clock"]
        accent = config["accent"]

        self.time_label = make_label(
            self.widget,
            config,
            size=clock_config["time_font_size"],
            color=accent["text_main"],
            weight="bold",
            anchor="center",
        )
        self.date_label = make_label(
            self.widget,
            config,
            size=clock_config["date_font_size"],
            color=accent["text_muted"],
            anchor="center",
        )
        self.time_label.pack(fill="x")
        self.date_label.pack(fill="x")
        self._tick()

    def _tick(self):
        fmt = "%H:%M:%S" if self.config["clock"]["show_seconds"] else "%H:%M"
        now = datetime.now()
        self.time_label.configure(text=now.strftime(fmt))
        self.date_label.configure(text=now.strftime("%A %d %B"))
        self.widget.after(1000, self._tick)
