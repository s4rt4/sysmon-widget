import random
import subprocess
import tkinter as tk

try:
    import dbus
except ImportError:
    dbus = None

from utils.bar_meter import BarMeter
from utils.ui import PanelFrame, make_label


class MusicPanel:
    def __init__(self, parent, config):
        self.config = config
        self.music_config = config["music"]
        self.widget = PanelFrame(parent, config)
        self.status = "Stopped"
        self.position = 0
        self.duration = 0
        self.title_text = ""
        self.vis_values = [4] * self.music_config["vis_bars"]
        accent = config["accent"]
        bg = self.widget.cget("bg")

        row = tk.Frame(self.widget, bg=bg)
        row.pack(fill="both", expand=True)

        self.vis_canvas = tk.Canvas(
            row,
            width=110,
            height=self.music_config["vis_height"] + 8,
            bg=bg,
            highlightthickness=0,
        )
        if self.music_config["show_visualizer"]:
            self.vis_canvas.pack(side="right", padx=(8, 0))

        left = tk.Frame(row, bg=bg)
        left.pack(side="left", fill="both", expand=True)

        self.status_label = make_label(left, config, text="▶ Stopped", size=10, color=accent["primary"], weight="bold")
        self.status_label.pack(fill="x")
        self.title_canvas = tk.Canvas(left, height=18, bg=bg, highlightthickness=0)
        self.title_canvas.pack(fill="x", pady=(2, 0))
        self.title_offset = 0
        self.meta_label = make_label(left, config, text="--", size=9, color=accent["text_muted"])
        self.meta_label.pack(fill="x")
        self.time_label = make_label(left, config, text="0:00 / 0:00", size=9, color=accent["text_muted"])
        self.time_label.pack(fill="x", pady=(4, 0))
        self.progress = BarMeter(left, 10, 3, accent["primary"], accent["track_bg"], bg)
        self.progress.canvas.pack(fill="x", pady=(2, 0))

        self._refresh()
        self._animate()
        self._local_second()

    def _refresh(self):
        info = self._mpris_info()
        self.status = info["status"]
        self.position = info.get("position", 0)
        self.duration = info.get("duration", 0)
        title = info.get("title") or "No track"
        artist = info.get("artist") or "Unknown artist"
        if title != self.title_text:
            self.title_text = title
            self.title_offset = 0
        self.status_label.configure(text=f"▶ {self.status}" if self.status == "Playing" else f"❚❚ {self.status}")
        self.meta_label.configure(text=self._truncate(artist, 32))
        self._draw_title()
        self._draw_time()
        self.widget.after(self.music_config["refresh_ms"], self._refresh)

    def _truncate(self, text, max_chars):
        if len(text) > max_chars:
            return text[: max_chars - 1] + "…"
        return text

    def _mpris_info(self):
        playerctl_info = self._playerctl_info()
        if playerctl_info:
            return playerctl_info
        if dbus is None:
            return {"status": "Stopped", "title": "dbus-python missing"}
        try:
            bus = dbus.SessionBus()
            services = [name for name in bus.list_names() if name.startswith("org.mpris.MediaPlayer2.")]
            if not services:
                return {"status": "Stopped"}
            preferred = self.music_config.get("preferred_player", "dopamine").lower()
            services.sort(key=lambda name: 0 if preferred in name.lower() else 1)
            for service in services:
                info = self._read_mpris_service(bus, service)
                if info.get("title") or preferred in service.lower():
                    return info
            return {"status": "Stopped"}
        except Exception:
            return {"status": "Stopped", "title": "MPRIS unavailable"}

    def _read_mpris_service(self, bus, service):
        player_obj = bus.get_object(service, "/org/mpris/MediaPlayer2")
        props = dbus.Interface(player_obj, "org.freedesktop.DBus.Properties")
        metadata = props.Get("org.mpris.MediaPlayer2.Player", "Metadata")
        status = props.Get("org.mpris.MediaPlayer2.Player", "PlaybackStatus")
        position = props.Get("org.mpris.MediaPlayer2.Player", "Position")
        artists = metadata.get("xesam:artist", [""])
        duration = int(metadata.get("mpris:length", 0))
        return {
            "status": str(status),
            "title": str(metadata.get("xesam:title", "")),
            "artist": str(artists[0]) if artists else "",
            "album": str(metadata.get("xesam:album", "")),
            "position": int(position),
            "duration": duration,
        }

    def _playerctl_info(self):
        player = self.music_config.get("preferred_player", "dopamine")
        try:
            status = self._playerctl(["status"], player)
            title = self._playerctl(["metadata", "title"], player)
            artist = self._playerctl(["metadata", "artist"], player)
            album = self._playerctl(["metadata", "album"], player)
            position_text = self._playerctl(["position"], player)
            duration_text = self._playerctl(["metadata", "mpris:length"], player)
        except (OSError, subprocess.SubprocessError):
            return None
        if not title:
            return None
        try:
            position = int(float(position_text) * 1_000_000)
        except ValueError:
            position = 0
        try:
            duration = int(duration_text)
        except ValueError:
            duration = 0
        return {
            "status": status or "Stopped",
            "title": title,
            "artist": artist,
            "album": album,
            "position": position,
            "duration": duration,
        }

    def _playerctl(self, args, player):
        result = subprocess.run(
            ["playerctl", "-p", player, *args],
            check=True,
            capture_output=True,
            text=True,
            timeout=1,
        )
        return result.stdout.strip()

    def _animate(self):
        if self.status == "Playing":
            self.vis_values = [
                max(4, min(self.music_config["vis_height"], v + random.randint(-6, 8)))
                for v in self.vis_values
            ]
        else:
            self.vis_values = [max(4, v - 3) for v in self.vis_values]
        self._draw_visualizer()
        self._draw_title()
        self.widget.after(80, self._animate)

    def _draw_title(self):
        self.title_canvas.delete("all")
        width = max(1, self.title_canvas.winfo_width())
        font = (self.config["clock"]["font"], 11, "bold")
        color = self.config["accent"]["text_main"]
        text = self.title_text or "No track"
        # measure full text width
        measure_id = self.title_canvas.create_text(0, -100, text=text, font=font, anchor="w")
        bbox = self.title_canvas.bbox(measure_id)
        text_width = (bbox[2] - bbox[0]) if bbox else 0
        self.title_canvas.delete(measure_id)
        if text_width <= width:
            self.title_canvas.create_text(0, 9, text=text, font=font, fill=color, anchor="w")
            self.title_offset = 0
            return
        # marquee: draw twice (gap then repeat) so it wraps seamlessly
        gap = 40
        cycle = text_width + gap
        x = -self.title_offset
        self.title_canvas.create_text(x, 9, text=text, font=font, fill=color, anchor="w")
        self.title_canvas.create_text(x + cycle, 9, text=text, font=font, fill=color, anchor="w")
        speed = max(0.2, self.music_config.get("marquee_speed", 30) / 80)
        self.title_offset = (self.title_offset + speed) % cycle

    def _draw_visualizer(self):
        self.vis_canvas.delete("all")
        width = max(1, self.vis_canvas.winfo_width())
        height = self.music_config["vis_height"]
        gap = 2
        n = len(self.vis_values)
        bar_width = max(2, (width - gap * (n - 1)) / n)
        for idx, value in enumerate(self.vis_values):
            x0 = idx * (bar_width + gap)
            self.vis_canvas.create_rectangle(
                x0,
                height - value + 4,
                x0 + bar_width,
                height + 4,
                fill=self.config["accent"]["primary"],
                width=0,
            )

    def _draw_time(self):
        pos_sec = max(0, self.position // 1_000_000)
        dur_sec = max(0, self.duration // 1_000_000)
        self.time_label.configure(
            text=f"{pos_sec // 60}:{pos_sec % 60:02d} / {dur_sec // 60}:{dur_sec % 60:02d}"
        )
        if dur_sec > 0:
            self.progress.set(min(100, pos_sec / dur_sec * 100))
        else:
            self.progress.set(0)

    def _local_second(self):
        if self.status == "Playing":
            self.position += 1_000_000
            self._draw_time()
        self.widget.after(1000, self._local_second)
