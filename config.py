import importlib.util
import os
from pathlib import Path


THEMES = {
    "purple": {
        "bg_color": "#0a0a12",
        "card_bg": "#1c1830",
        "panel_bg": "#1c1830",
        "separator_color": "#3A2A50",
        "primary": "#CC44FF",
        "secondary": "#FF44AA",
        "track_bg": "#0d0a18",
        "text_main": "#FFFFFF",
        "text_muted": "#A99BB8",
    },
    "graphite": {
        "bg_color": "#000000",
        "card_bg": "#161a20",
        "panel_bg": "#161a20",
        "separator_color": "#2a2f38",
        "primary": "#4DD0E1",
        "secondary": "#80CBC4",
        "track_bg": "#0a0d12",
        "text_main": "#F5F7FA",
        "text_muted": "#A8ADB5",
    },
    "midnight": {
        "bg_color": "#05080f",
        "card_bg": "#101a2e",
        "panel_bg": "#101a2e",
        "separator_color": "#22304A",
        "primary": "#5BA7FF",
        "secondary": "#8B7CFF",
        "track_bg": "#08101F",
        "text_main": "#F3F7FF",
        "text_muted": "#94A3B8",
    },
    "forest": {
        "bg_color": "#04100a",
        "card_bg": "#14251D",
        "panel_bg": "#14251D",
        "separator_color": "#284236",
        "primary": "#6EE7A8",
        "secondary": "#A3E635",
        "track_bg": "#08150F",
        "text_main": "#F2FFF8",
        "text_muted": "#9BB8A8",
    },
    "rose": {
        "bg_color": "#10070c",
        "card_bg": "#2B1624",
        "panel_bg": "#2B1624",
        "separator_color": "#472A3B",
        "primary": "#FB7185",
        "secondary": "#F472B6",
        "track_bg": "#1A0B14",
        "text_main": "#FFF5F7",
        "text_muted": "#C7A3B0",
    },
    "amber": {
        "bg_color": "#0e0904",
        "card_bg": "#241B12",
        "panel_bg": "#241B12",
        "separator_color": "#3F3121",
        "primary": "#FBBF24",
        "secondary": "#F97316",
        "track_bg": "#140E08",
        "text_main": "#FFF8EA",
        "text_muted": "#C7B99E",
    },
}


CONFIG = {
    "theme": os.environ.get("SYSMON_WIDGET_THEME", "graphite"),
    "position": {"anchor": "right", "x": 16, "y": 16},
    "width": 320,
    "bg_color": "#000000",
    "card_bg": "#161a20",
    "transparent_color": "#000000",
    "bg_alpha": 1.0,
    "panel_bg": "#161a20",
    "separator_color": "#2a2f38",
    "card_radius": 14,
    "card_gap": 6,
    "outer_pad": 4,
    "panel_padding": 9,
    "accent": {
        "primary": "#4DD0E1",
        "secondary": "#80CBC4",
        "text_main": "#F5F7FA",
        "text_muted": "#A8ADB5",
        "track_bg": "#0a0d12",
    },
    "panels": {
        "clock": True,
        "weather": True,
        "network": True,
        "sysstat": True,
        "music": True,
        "storage": True,
        "processes": True,
        "footer": True,
    },
    "clock": {
        "time_font_size": 34,
        "date_font_size": 11,
        "day_font_size": 15,
        "font": "DejaVu Sans",
        "show_seconds": False,
    },
    "weather": {
        "api_key": os.environ.get("OPENWEATHER_API_KEY", ""),
        "city_id": 1648473,
        "city": "Palangkaraya",
        "country_code": "ID",
        "units": "metric",
        "refresh_sec": 600,
        "show_humidity": True,
        "show_wind": True,
    },
    "network": {
        "interface": "auto",
        "history_len": 40,
        "refresh_ms": 1000,
        "unit": "KiB",
    },
    "sysstat": {
        "refresh_ms": 1500,
        "show_battery": True,
        "show_temp": True,
        "ring_size": 44,
        "ring_width": 5,
        "cpu_color": None,
        "ram_color": None,
        "battery_color": None,
        "temp_color": None,
    },
    "storage": {
        "paths": [
            {"label": "C:", "path": "/"},
        ],
        "bar_height": 6,
        "refresh_sec": 30,
    },
    "music": {
        "preferred_player": "dopamine",
        "refresh_ms": 2000,
        "marquee_speed": 30,
        "show_visualizer": True,
        "vis_bars": 14,
        "vis_height": 22,
    },
    "processes": {
        "refresh_ms": 2500,
        "top_n": 2,
    },
    "footer": {
        "refresh_ms": 2000,
        "brightness_path": "auto",
    },
}


def _merge_dict(base, override):
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _merge_dict(base[key], value)
        else:
            base[key] = value


def _load_local_config():
    path = Path.home() / ".config" / "sysmon-widget" / "config.py"
    if not path.exists():
        return
    spec = importlib.util.spec_from_file_location("sysmon_widget_local_config", path)
    if spec is None or spec.loader is None:
        return
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    local_config = getattr(module, "LOCAL_CONFIG", None)
    if isinstance(local_config, dict):
        _merge_dict(CONFIG, local_config)


_load_local_config()


def apply_theme(name=None):
    theme_name = name or CONFIG.get("theme", "graphite")
    theme = THEMES.get(theme_name, THEMES["graphite"])
    CONFIG["theme"] = theme_name if theme_name in THEMES else "graphite"
    CONFIG["bg_color"] = theme["bg_color"]
    CONFIG["transparent_color"] = theme["bg_color"]
    CONFIG["card_bg"] = theme["card_bg"]
    CONFIG["panel_bg"] = theme["card_bg"]
    CONFIG["separator_color"] = theme["separator_color"]
    CONFIG["accent"]["primary"] = theme["primary"]
    CONFIG["accent"]["secondary"] = theme["secondary"]
    CONFIG["accent"]["track_bg"] = theme["track_bg"]
    CONFIG["accent"]["text_main"] = theme["text_main"]
    CONFIG["accent"]["text_muted"] = theme["text_muted"]


apply_theme()
