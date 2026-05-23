import importlib.util
import os
from pathlib import Path


CONFIG = {
    "position": {"anchor": "right", "x": 30, "y": 30},
    "width": 300,
    "bg_color": "#2A1A3E",
    "transparent_color": "#2A1A3E",
    "bg_alpha": 1.0,
    "panel_bg": "#2A1A3E",
    "separator_color": "#3A2A50",
    "corner_radius": 0,
    "panel_gap": 0,
    "panel_padding": 14,
    "accent": {
        "primary": "#cc44ff",
        "secondary": "#ff44aa",
        "text_main": "#ffffff",
        "text_muted": "#888899",
        "track_bg": "#1A0F29",
    },
    "panels": {
        "clock": True,
        "weather": True,
        "network": True,
        "sysstat": True,
        "storage": True,
        "music": True,
    },
    "clock": {
        "time_font_size": 52,
        "date_font_size": 14,
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
        "ring_size": 58,
        "ring_width": 6,
        "cpu_color": None,
        "ram_color": None,
        "battery_color": "#cc44ff",
        "temp_color": "#ff44aa",
    },
    "storage": {
        "paths": [
            {"label": "System", "path": "/"},
            {"label": "Home", "path": "/home"},
        ],
        "bar_height": 5,
        "refresh_sec": 30,
    },
    "music": {
        "preferred_player": "dopamine",
        "refresh_ms": 2000,
        "marquee_speed": 30,
        "show_visualizer": True,
        "vis_bars": 16,
        "vis_height": 32,
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
