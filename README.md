# Desktop Widget

Conky-style floating desktop widget built with Python and Tkinter.

## Setup

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

The widget degrades gracefully when optional desktop services are unavailable:

- Weather shows a placeholder until `CONFIG["weather"]["api_key"]` is set.
- Music shows stopped/unavailable if no MPRIS2 player or D-Bus binding is available.
- Battery and temperature gauges show `--` when sensors are unavailable.

## Build Debian Package

```bash
packaging/build-deb.sh 1.0.0
sudo apt install ./dist/sysmon-widget_1.0.0_all.deb
```
