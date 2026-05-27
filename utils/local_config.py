import importlib.util
import pprint
from pathlib import Path


LOCAL_CONFIG_PATH = Path.home() / ".config" / "sysmon-widget" / "config.py"


def load_local_config():
    if not LOCAL_CONFIG_PATH.exists():
        return {}
    try:
        spec = importlib.util.spec_from_file_location(
            "sysmon_widget_local_config_rw", LOCAL_CONFIG_PATH
        )
        if spec is None or spec.loader is None:
            return {}
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        value = getattr(module, "LOCAL_CONFIG", {})
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def save_local_config(local_config):
    LOCAL_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    formatted = pprint.pformat(local_config, indent=4, width=80, sort_dicts=False)
    LOCAL_CONFIG_PATH.write_text(f"LOCAL_CONFIG = {formatted}\n")


def update_local_config(updates):
    current = load_local_config()
    _deep_merge(current, updates)
    save_local_config(current)
    return current


def _deep_merge(base, override):
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
