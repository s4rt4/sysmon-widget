import tkinter as tk


class RingGauge:
    def __init__(self, parent, size, ring_width, color, track_color, text_color, bg, font_size=11):
        self.size = size
        self.ring_width = ring_width
        self.color = color
        self.track_color = track_color
        self.text_color = text_color
        self.font_size = font_size
        self.value = 0.0
        self.label_text = "--"
        self.canvas = tk.Canvas(parent, width=size, height=size, bg=bg, highlightthickness=0)
        self._job = None
        self._draw()

    def set(self, pct, label_text=None):
        self.value = max(0, min(100, float(pct or 0)))
        if label_text is not None:
            self.label_text = label_text
        self._draw()

    def animate_to(self, pct, label_text=None, duration_ms=300):
        target = max(0, min(100, float(pct or 0)))
        start = self.value
        steps = max(1, duration_ms // 30)
        if self._job:
            self.canvas.after_cancel(self._job)

        def tick(step=1):
            t = step / steps
            self.value = start + (target - start) * t
            if label_text is not None:
                self.label_text = label_text
            self._draw()
            if step < steps:
                self._job = self.canvas.after(30, lambda: tick(step + 1))
            else:
                self._job = None

        tick()

    def _draw(self):
        self.canvas.delete("all")
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
        self.canvas.create_arc(
            bounds,
            start=90,
            extent=-(self.value / 100 * 360),
            style=tk.ARC,
            outline=self.color,
            width=self.ring_width,
        )
        self.canvas.create_text(
            self.size / 2,
            self.size / 2,
            text=self.label_text,
            fill=self.text_color,
            font=("monospace", self.font_size, "bold"),
        )
