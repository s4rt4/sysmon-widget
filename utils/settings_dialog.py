import tkinter as tk
from tkinter import ttk, messagebox

from config import CONFIG, THEMES
from utils.local_config import update_local_config


POSITIONS = ("left", "center", "right")


class SettingsDialog:
    def __init__(self, root, on_saved=None):
        self._root = root
        self._on_saved = on_saved
        self._top = None
        self._vars = {}

    def open(self):
        if self._top is not None and self._top.winfo_exists():
            self._top.lift()
            self._top.focus_force()
            return
        self._build()

    def _build(self):
        top = tk.Toplevel(self._root)
        self._top = top
        top.title("sysmon-widget settings")
        top.transient(self._root)
        top.resizable(False, False)
        top.configure(padx=12, pady=12)

        weather = CONFIG.get("weather", {})
        position = CONFIG.get("position", {})
        network = CONFIG.get("network", {})
        sysstat = CONFIG.get("sysstat", {})

        v = self._vars
        v["api_key"] = tk.StringVar(value=weather.get("api_key", ""))
        v["city"] = tk.StringVar(value=weather.get("city", ""))
        v["city_id"] = tk.StringVar(value=str(weather.get("city_id", "")))
        v["country_code"] = tk.StringVar(value=weather.get("country_code", "ID"))
        v["units"] = tk.StringVar(value=weather.get("units", "metric"))
        v["weather_refresh"] = tk.StringVar(value=str(weather.get("refresh_sec", 600)))
        v["anchor"] = tk.StringVar(value=position.get("anchor", "right"))
        v["pos_x"] = tk.StringVar(value=str(position.get("x", 16)))
        v["pos_y"] = tk.StringVar(value=str(position.get("y", 16)))
        v["theme"] = tk.StringVar(value=CONFIG.get("theme", "graphite"))
        v["net_interface"] = tk.StringVar(value=network.get("interface", "auto"))
        v["net_unit"] = tk.StringVar(value=network.get("unit", "KiB"))
        v["sysstat_refresh"] = tk.StringVar(value=str(sysstat.get("refresh_ms", 1500)))

        row = 0
        row = self._section(top, row, "Weather")
        row = self._field(top, row, "API key", v["api_key"], width=36, show="*")
        row = self._field(top, row, "City name", v["city"])
        row = self._field(top, row, "City ID", v["city_id"])
        row = self._field(top, row, "Country code", v["country_code"], width=8)
        row = self._combo(top, row, "Units", v["units"], ("metric", "imperial"))
        row = self._field(top, row, "Refresh (sec)", v["weather_refresh"], width=10)

        row = self._section(top, row, "Position & theme")
        row = self._combo(top, row, "Anchor", v["anchor"], POSITIONS)
        row = self._field(top, row, "Offset X", v["pos_x"], width=8)
        row = self._field(top, row, "Offset Y", v["pos_y"], width=8)
        row = self._combo(top, row, "Theme", v["theme"], tuple(sorted(THEMES)))

        row = self._section(top, row, "Network & sysstat")
        row = self._field(top, row, "Net interface", v["net_interface"])
        row = self._combo(top, row, "Net unit", v["net_unit"], ("KiB", "MiB", "Mbps"))
        row = self._field(top, row, "Sysstat refresh (ms)", v["sysstat_refresh"], width=10)

        btn_frame = ttk.Frame(top)
        btn_frame.grid(row=row, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(btn_frame, text="Cancel", command=self._close).pack(side="right", padx=(6, 0))
        ttk.Button(btn_frame, text="Save", command=self._save).pack(side="right")

        top.protocol("WM_DELETE_WINDOW", self._close)
        top.update_idletasks()
        self._center_over_root(top)
        top.focus_force()

    def _section(self, parent, row, text):
        lbl = ttk.Label(parent, text=text, font=("DejaVu Sans", 10, "bold"))
        lbl.grid(row=row, column=0, columnspan=2, sticky="w", pady=(8 if row else 0, 4))
        return row + 1

    def _field(self, parent, row, label, var, width=24, show=None):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=(0, 8), pady=2)
        entry = ttk.Entry(parent, textvariable=var, width=width, show=show or "")
        entry.grid(row=row, column=1, sticky="w", pady=2)
        return row + 1

    def _combo(self, parent, row, label, var, values):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=(0, 8), pady=2)
        combo = ttk.Combobox(parent, textvariable=var, values=values, state="readonly", width=18)
        combo.grid(row=row, column=1, sticky="w", pady=2)
        return row + 1

    def _center_over_root(self, top):
        self._root.update_idletasks()
        try:
            rx = self._root.winfo_rootx()
            ry = self._root.winfo_rooty()
            rw = self._root.winfo_width()
            rh = self._root.winfo_height()
        except Exception:
            rx, ry, rw, rh = 100, 100, 320, 480
        tw = top.winfo_reqwidth()
        th = top.winfo_reqheight()
        x = max(0, rx + (rw - tw) // 2)
        y = max(0, ry + (rh - th) // 2)
        top.geometry(f"+{x}+{y}")

    def _save(self):
        try:
            updates = self._collect()
        except ValueError as exc:
            messagebox.showerror("Invalid value", str(exc), parent=self._top)
            return
        update_local_config(updates)
        self._close()
        if self._on_saved is not None:
            self._on_saved()

    def _collect(self):
        v = self._vars
        try:
            city_id = int(v["city_id"].get().strip()) if v["city_id"].get().strip() else 0
        except ValueError:
            raise ValueError("City ID must be an integer")
        try:
            weather_refresh = int(v["weather_refresh"].get().strip() or "600")
        except ValueError:
            raise ValueError("Weather refresh must be an integer (seconds)")
        try:
            pos_x = int(v["pos_x"].get().strip() or "0")
            pos_y = int(v["pos_y"].get().strip() or "0")
        except ValueError:
            raise ValueError("Position X/Y must be integers")
        try:
            sysstat_refresh = int(v["sysstat_refresh"].get().strip() or "1500")
        except ValueError:
            raise ValueError("Sysstat refresh must be an integer (ms)")

        anchor = v["anchor"].get()
        if anchor not in POSITIONS:
            anchor = "right"
        theme = v["theme"].get()
        if theme not in THEMES:
            theme = "graphite"

        return {
            "theme": theme,
            "position": {"anchor": anchor, "x": pos_x, "y": pos_y},
            "weather": {
                "api_key": v["api_key"].get().strip(),
                "city": v["city"].get().strip(),
                "city_id": city_id,
                "country_code": v["country_code"].get().strip() or "ID",
                "units": v["units"].get() or "metric",
                "refresh_sec": weather_refresh,
            },
            "network": {
                "interface": v["net_interface"].get().strip() or "auto",
                "unit": v["net_unit"].get() or "KiB",
            },
            "sysstat": {"refresh_ms": sysstat_refresh},
        }

    def _close(self):
        if self._top is not None:
            try:
                self._top.destroy()
            except Exception:
                pass
            self._top = None
