# Desktop Widget

Conky-style floating desktop widget built with Python and Tkinter. This branch
(`fedora-gnome`) is tuned for **Fedora + GNOME (Wayland/XWayland)**: since GNOME
has no system tray, the widget exposes an in-widget **gear menu** (top-right of
the clock card) for Settings, Autostart, Restart and Exit.

## Install on Fedora (RPM)

Grab the `.rpm` from the [latest release](https://github.com/s4rt4/sysmon-widget/releases):

```bash
sudo dnf install ./sysmon-widget-1.0.0-1.fc43.noarch.rpm
```

Core Python dependencies are pulled automatically; `playerctl` and
`python3-pystray` are optional (D-Bus and the gear menu cover their roles on
GNOME). Then launch from the app grid ("Sysmon Widget") or run `sysmon-widget`.
The package installs a system autostart entry, so the widget starts on login;
toggle it from the gear menu.

## Setup (run from source)

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

On Debian/Ubuntu systems that block global `pip` installs with `externally-managed-environment`, either use the virtual environment above or install packaged dependencies:

```bash
sudo apt install python3-tk python3-psutil python3-requests python3-dbus python3-pil python3-xlib playerctl
python3 main.py
```

On Fedora:

```bash
sudo dnf install python3-tkinter python3-psutil python3-requests python3-dbus python3-pillow python3-xlib playerctl python3-pystray
python3 main.py
```

Edit `config.py` to change colors, position, enabled panels, and the OpenWeatherMap API key.

For weather, prefer keeping the API key out of source control:

```bash
mkdir -p ~/.config/sysmon-widget
cat > ~/.config/sysmon-widget/config.py <<'EOF'
LOCAL_CONFIG = {
    "weather": {
        "api_key": "YOUR_OPENWEATHERMAP_API_KEY",
    },
}
EOF
```

The default mode is borderless and hidden from the taskbar. For a normal debug window, run:

```bash
python main.py --managed
```

Choose a color theme:

```bash
python main.py --theme graphite
```

Available themes: `purple`, `graphite`, `midnight`, `forest`, `rose`, `amber`.

You can also set the theme from local config:

```python
LOCAL_CONFIG = {
    "theme": "midnight",
}
```

The widget degrades gracefully when optional desktop services are unavailable:

- Weather shows a placeholder until `CONFIG["weather"]["api_key"]` is set.
- Music shows stopped/unavailable if no MPRIS2 player or D-Bus binding is available.
- Battery and temperature gauges show `--` when sensors are unavailable.

## Performance

Idle CPU on a 2-core machine, measured with `top -d 3` over ~60 s:

| Version | Mean | Median |
|---------|-----:|-------:|
| 0.1.0   | ~38% | ~38%   |
| 0.2.2   | ~6%  | ~6%    |

CPU percentages shown in the Top Processes panel are normalized by core count to match Plasma System Monitor.

## Build packages

Debian/Ubuntu:

```bash
packaging/build-deb.sh 0.2.2
sudo apt install ./dist/sysmon-widget_0.2.2_all.deb
```

Fedora (RPM):

```bash
packaging/build-rpm.sh 1.0.0
sudo dnf install ./dist/sysmon-widget-1.0.0-1.fc43.noarch.rpm
```

Both install to `/opt/sysmon-widget` with a `sysmon-widget` launcher, an
applications-menu entry, and a system autostart entry.

## License

MIT — see [LICENSE](LICENSE).
