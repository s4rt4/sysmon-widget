import random
import subprocess
import tkinter as tk

try:
    import dbus
except ImportError:  # pragma: no cover
    dbus = None

from utils.ui import PanelFrame, make_label


class MusicPanel:
    def __init__(self, parent, config):
        self.config = config
        self.music_config = config["music"]
        self.widget = PanelFrame(parent, config)
        self.status = "Stopped"
        self.position = 0
        self.title_offset = 0
        self.title_text = ""
        self.vis_values = [4] * self.music_config["vis_bars"]

        self.status_label = make_label(self.widget, config, text="♪ Stopped", size=11, color=config["accent"]["primary"])
        self.status_label.pack(fill="x")
        self.title_canvas = tk.Canvas(self.widget, height=22, bg=self.widget.cget("bg"), highlightthickness=0)
        self.title_canvas.pack(fill="x", pady=(4, 0))
        self.meta_label = make_label(self.widget, config, text="No active MPRIS player", size=10, color=config["accent"]["text_muted"])
        self.meta_label.pack(fill="x")
        self.time_label = make_label(self.widget, config, text="0:00", size=10, color=config["accent"]["text_muted"])
        self.time_label.pack(fill="x", pady=(4, 0))
        self.vis_canvas = tk.Canvas(
            self.widget,
            height=self.music_config["vis_height"],
            bg=self.widget.cget("bg"),
            highlightthickness=0,
        )
        if self.music_config["show_visualizer"]:
            self.vis_canvas.pack(fill="x", pady=(6, 0))

        self._refresh()
        self._animate()
        self._local_second()

    def _refresh(self):
        info = self._mpris_info()
        self.status = info["status"]
        self.position = info.get("position", 0)
        title = info.get("title") or "No track"
        artist = info.get("artist") or "Unknown artist"
        album = info.get("album") or ""
        self.title_text = title
        self.status_label.configure(text=f"♪ {self.status}")
        self.meta_label.configure(text=" - ".join(part for part in (artist, album) if part))
        self._draw_title()
        self._draw_time()
        self.widget.after(self.music_config["refresh_ms"], self._refresh)

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
        return {
            "status": str(status),
            "title": str(metadata.get("xesam:title", "")),
            "artist": str(artists[0]) if artists else "",
            "album": str(metadata.get("xesam:album", "")),
            "position": int(position),
        }

    def _playerctl_info(self):
        player = self.music_config.get("preferred_player", "dopamine")
        try:
            status = self._playerctl(["status"], player)
            title = self._playerctl(["metadata", "title"], player)
            artist = self._playerctl(["metadata", "artist"], player)
            album = self._playerctl(["metadata", "album"], player)
            position_text = self._playerctl(["position"], player)
        except (OSError, subprocess.SubprocessError):
            return None
        if not title:
            return None
        try:
            position = int(float(position_text) * 1_000_000)
        except ValueError:
            position = 0
        return {
            "status": status or "Stopped",
            "title": title,
            "artist": artist,
            "album": album,
            "position": position,
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
            self.vis_values = [max(4, min(self.music_config["vis_height"], value + random.randint(-6, 8))) for value in self.vis_values]
        else:
            self.vis_values = [max(4, value - 3) for value in self.vis_values]
        self._draw_visualizer()
        self._draw_title()
        self.widget.after(80, self._animate)

    def _draw_visualizer(self):
        self.vis_canvas.delete("all")
        width = max(1, self.vis_canvas.winfo_width())
        height = self.music_config["vis_height"]
        gap = 3
        bar_width = max(2, (width - gap * (len(self.vis_values) - 1)) / len(self.vis_values))
        for idx, value in enumerate(self.vis_values):
            x0 = idx * (bar_width + gap)
            self.vis_canvas.create_rectangle(
                x0,
                height - value,
                x0 + bar_width,
                height,
                fill=self.config["accent"]["primary"],
                width=0,
            )

    def _draw_title(self):
        self.title_canvas.delete("all")
        width = max(1, self.title_canvas.winfo_width())
        text_id = self.title_canvas.create_text(
            -self.title_offset,
            11,
            anchor="w",
            text=self.title_text,
            fill=self.config["accent"]["text_main"],
            font=(self.config["clock"]["font"], 12, "bold"),
        )
        bbox = self.title_canvas.bbox(text_id)
        text_width = (bbox[2] - bbox[0]) if bbox else 0
        if text_width > width:
            self.title_offset = (self.title_offset + self.music_config["marquee_speed"] / 12.5) % (text_width + 30)
        else:
            self.title_offset = 0

    def _draw_time(self):
        seconds = max(0, self.position // 1_000_000)
        self.time_label.configure(text=f"{seconds // 60}:{seconds % 60:02d}")

    def _local_second(self):
        if self.status == "Playing":
            self.position += 1_000_000
            self._draw_time()
        self.widget.after(1000, self._local_second)
