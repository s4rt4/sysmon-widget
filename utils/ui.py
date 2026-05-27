import tkinter as tk


class PanelFrame(tk.Frame):
    def __init__(self, parent, config, card=True):
        self.card = card
        self.config_data = config
        self.content_bg = config.get("panel_bg", config["bg_color"])
        super().__init__(
            parent,
            bg=self.content_bg,
            padx=config["panel_padding"] if card else 0,
            pady=config["panel_padding"] if card else 0,
            highlightthickness=0,
        )
        self.bg_canvas = None

    def cget(self, key):
        if key in ("bg", "background"):
            return self.content_bg
        return super().cget(key)

def make_label(parent, config, text="", size=12, color=None, weight="normal", anchor="w"):
    accent = config["accent"]
    return tk.Label(
        parent,
        text=text,
        bg=parent.cget("bg"),
        fg=color or accent["text_main"],
        font=(config["clock"]["font"], size, weight),
        anchor=anchor,
        justify="left",
    )


def make_separator(parent, config):
    return tk.Frame(parent, bg=config["separator_color"], height=1, highlightthickness=0)


def format_bytes(value):
    value = float(max(0, value))
    for unit in ("B", "KiB", "MiB", "GiB"):
        if value < 1024 or unit == "GiB":
            if unit == "B":
                return f"{value:.0f}B"
            return f"{value:.2f}{unit}"
        value /= 1024


def compact_bytes(value):
    value = float(max(0, value))
    for unit, threshold in (("G", 1024**3), ("M", 1024**2), ("K", 1024)):
        if value >= threshold:
            return f"{value / threshold:.1f}{unit}"
    return f"{value:.0f}B"
