import tkinter as tk

try:
    import psutil
except ImportError:
    psutil = None

from utils.ui import PanelFrame, format_bytes, make_label


class ProcessesPanel:
    def __init__(self, parent, config):
        self.config = config
        self.proc_config = config["processes"]
        self.widget = PanelFrame(parent, config)
        accent = config["accent"]
        bg = self.widget.cget("bg")

        make_label(
            self.widget,
            config,
            text="TOP PROCESSES",
            size=10,
            color=accent["primary"],
            weight="bold",
        ).pack(fill="x")

        self.rows_container = tk.Frame(self.widget, bg=bg)
        self.rows_container.pack(fill="both", expand=True, pady=(6, 0))
        self.rows = []
        for _ in range(self.proc_config["top_n"]):
            self.rows.append(self._build_row(self.rows_container))

        self._init_cpu_baseline()
        self._tick()

    def _init_cpu_baseline(self):
        if psutil is None:
            return
        for proc in psutil.process_iter():
            try:
                proc.cpu_percent(interval=None)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    def _build_row(self, parent):
        accent = self.config["accent"]
        bg = parent.cget("bg")
        wrapper = tk.Frame(parent, bg=bg)
        wrapper.pack(fill="x", pady=(0, 6))
        name = make_label(wrapper, self.config, text="--", size=11, weight="bold")
        name.pack(fill="x")
        stats_row = tk.Frame(wrapper, bg=bg)
        stats_row.pack(fill="x", pady=(2, 0))
        cpu_icon = make_label(stats_row, self.config, text="⏿", size=9, color=accent["primary"])
        cpu_val = make_label(stats_row, self.config, text="--", size=10)
        mem_icon = make_label(stats_row, self.config, text="▥", size=9, color=accent["secondary"])
        mem_val = make_label(stats_row, self.config, text="--", size=10)
        cpu_icon.pack(side="left", padx=(0, 4))
        cpu_val.pack(side="left", padx=(0, 12))
        mem_icon.pack(side="left", padx=(0, 4))
        mem_val.pack(side="left")
        return {"name": name, "cpu": cpu_val, "mem": mem_val}

    def _tick(self):
        procs = self._top_processes()
        for idx, row in enumerate(self.rows):
            if idx < len(procs):
                p = procs[idx]
                row["name"].configure(text=self._truncate(p["name"], 22))
                row["cpu"].configure(text=f"{p['cpu']:.0f}%")
                row["mem"].configure(text=format_bytes(p["mem"]))
            else:
                row["name"].configure(text="--")
                row["cpu"].configure(text="--")
                row["mem"].configure(text="--")
        self.widget.after(self.proc_config["refresh_ms"], self._tick)

    def _truncate(self, text, max_chars):
        if len(text) > max_chars:
            return text[: max_chars - 1] + "…"
        return text

    def _top_processes(self):
        if psutil is None:
            return []
        result = []
        for proc in psutil.process_iter(["name"]):
            try:
                cpu = proc.cpu_percent(interval=None)
                mem = proc.memory_info().rss
                name = proc.info.get("name") or "?"
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            result.append({"name": name, "cpu": cpu, "mem": mem})
        result.sort(key=lambda p: (p["cpu"], p["mem"]), reverse=True)
        return result[: self.proc_config["top_n"]]
