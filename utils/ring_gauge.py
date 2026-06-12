import tkinter as tk

try:
    from PIL import Image, ImageDraw, ImageTk
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False


_SCALE = 4


class RingGauge:
    def __init__(self, parent, size, ring_width, color, track_color, text_color, bg, font_size=11):
        self.size = size
        self.ring_width = ring_width
        self.color = color
        self.track_color = track_color
        self.text_color = text_color
        self.bg = bg
        self.font_size = font_size
        self.value = 0.0
        self.label_text = "--"
        self.canvas = tk.Canvas(parent, width=size, height=size, bg=bg, highlightthickness=0)
        self._photo = None
        self._job = None
        self._track_base = None
        if _PIL_AVAILABLE:
            self._build_track_base()
        self._draw()

    def _build_track_base(self):
        s = self.size * _SCALE
        w = self.ring_width * _SCALE
        pad = w // 2 + 2 * _SCALE
        img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.arc((pad, pad, s - pad, s - pad), start=0, end=360, fill=self.track_color, width=w)
        self._track_base = img
        self._bbox = (pad, pad, s - pad, s - pad)
        self._scaled_width = w

    def set(self, pct, label_text=None):
        self.value = max(0, min(100, float(pct or 0)))
        if label_text is not None:
            self.label_text = label_text
        self._draw()

    def animate_to(self, pct, label_text=None, duration_ms=300):
        target = max(0, min(100, float(pct or 0)))
        start = self.value
        if self._job:
            self.canvas.after_cancel(self._job)
            self._job = None
        if abs(target - start) < 1.5:
            self.set(target, label_text)
            return
        steps = max(1, duration_ms // 60)

        def tick(step=1):
            t = step / steps
            self.value = start + (target - start) * t
            if label_text is not None:
                self.label_text = label_text
            self._draw()
            if step < steps:
                self._job = self.canvas.after(60, lambda: tick(step + 1))
            else:
                self._job = None

        tick()

    def _draw(self):
        self.canvas.delete("all")
        if _PIL_AVAILABLE:
            self._draw_pil()
        else:
            self._draw_tk()
        self.canvas.create_text(
            self.size / 2,
            self.size / 2,
            text=self.label_text,
            fill=self.text_color,
            font=("monospace", self.font_size, "bold"),
        )

    def _draw_pil(self):
        img = self._track_base.copy()
        if self.value > 0:
            draw = ImageDraw.Draw(img)
            extent = self.value / 100 * 360
            draw.arc(self._bbox, start=-90, end=-90 + extent, fill=self.color, width=self._scaled_width)
        img = img.resize((self.size, self.size), Image.LANCZOS)
        self._photo = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, image=self._photo, anchor="nw")

    def _draw_tk(self):
        pad = self.ring_width + 2
        bounds = (pad, pad, self.size - pad, self.size - pad)
        self.canvas.create_arc(
            bounds,
            start=90,
            extent=-359.9,
            style=tk.ARC,
            outline=self.track_color,
            width=self.ring_width,
        )
        if self.value > 0:
            # Tk reduces an arc extent modulo 360, so a full 360 draws nothing
            # (leaving only the white track). Cap at 359.9 like the track above.
            extent = min(359.9, self.value / 100 * 360)
            self.canvas.create_arc(
                bounds,
                start=90,
                extent=-extent,
                style=tk.ARC,
                outline=self.color,
                width=self.ring_width,
            )
