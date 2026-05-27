from io import BytesIO
import tkinter as tk

try:
    import requests
except ImportError:
    requests = None

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

from utils.ui import PanelFrame, make_label


LAST_WEATHER = None


class WeatherPanel:
    def __init__(self, parent, config):
        self.config = config
        self.weather_config = config["weather"]
        self.widget = PanelFrame(parent, config)
        self.icon_photo = None
        bg = self.widget.cget("bg")
        accent = config["accent"]

        self.title = make_label(self.widget, config, text="WEATHER", size=10, color=accent["secondary"], weight="bold")
        self.title.pack(fill="x")

        body = tk.Frame(self.widget, bg=bg)
        body.pack(fill="both", expand=True, pady=(6, 0))

        self.icon_label = make_label(body, config, text="☁", size=32, color=accent["primary"], anchor="center")
        self.icon_label.pack(side="left", padx=(0, 8))

        right = tk.Frame(body, bg=bg)
        right.pack(side="left", fill="both", expand=True)

        self.temp_label = make_label(right, config, text="--°C", size=22, weight="bold")
        self.temp_label.pack(fill="x")
        self.city_label = make_label(right, config, text=self.weather_config["city"], size=10, color=accent["text_muted"])
        self.city_label.pack(fill="x")
        self.desc_label = make_label(right, config, text="--", size=9, color=accent["text_muted"])
        self.desc_label.pack(fill="x")
        self.detail_label = make_label(right, config, text="", size=9, color=accent["text_muted"])
        self.detail_label.pack(fill="x")
        self._refresh()

    def _refresh(self):
        data = self._fetch()
        if data:
            self._render(data, offline=False)
        elif LAST_WEATHER:
            self._render(LAST_WEATHER, offline=True)
        else:
            self.desc_label.configure(text="Unavailable")
        self.widget.after(self.weather_config["refresh_sec"] * 1000, self._refresh)

    def _fetch(self):
        global LAST_WEATHER
        key = self.weather_config["api_key"]
        if requests is None or not key or key == "YOUR_OPENWEATHERMAP_API_KEY":
            return None
        params = {"appid": key, "units": self.weather_config["units"]}
        if self.weather_config.get("city_id"):
            params["id"] = self.weather_config["city_id"]
        else:
            params["q"] = f"{self.weather_config['city']},{self.weather_config['country_code']}"
        try:
            response = requests.get("https://api.openweathermap.org/data/2.5/weather", params=params, timeout=8)
            response.raise_for_status()
            LAST_WEATHER = response.json()
            return LAST_WEATHER
        except requests.RequestException:
            return None

    def _render(self, data, offline=False):
        weather = data.get("weather", [{}])[0]
        main = data.get("main", {})
        wind = data.get("wind", {})
        temp = main.get("temp")
        city = data.get("name", self.weather_config["city"])
        desc = weather.get("description", "unknown").title()
        suffix = " (offline)" if offline else ""

        self.temp_label.configure(text=f"{round(temp) if temp is not None else '--'}°C")
        self.city_label.configure(text=city)
        self.desc_label.configure(text=f"{desc}{suffix}")
        details = []
        if self.weather_config["show_humidity"]:
            details.append(f"H {main.get('humidity', '--')}%")
        if self.weather_config["show_wind"]:
            details.append(f"W {wind.get('speed', '--')}")
        self.detail_label.configure(text=" ".join(details))

        icon = weather.get("icon")
        if icon and requests is not None and Image is not None and ImageTk is not None:
            try:
                response = requests.get(f"https://openweathermap.org/img/wn/{icon}@2x.png", timeout=8)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content)).resize((48, 48))
                self.icon_photo = ImageTk.PhotoImage(image)
                self.icon_label.configure(image=self.icon_photo, text="")
            except Exception:
                self.icon_label.configure(image="", text="☁")
        else:
            self.icon_label.configure(text="☁")
