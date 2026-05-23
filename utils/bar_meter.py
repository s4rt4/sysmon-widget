import tkinter as tk


class BarMeter:
    def __init__(self, parent, width, height, fill_color, track_color, bg):
        self.width = width
        self.height = height
        self.fill_color = fill_color
        self.track_color = track_color
        self.value = 0.0
        self.canvas = tk.Canvas(parent, width=width, height=height, bg=bg, highlightthickness=0)
        self._job = None
        self._draw()

    def set(self, pct):
        self.value = max(0, min(100, float(pct or 0)))
        self._draw()

    def animate_to(self, pct, duration_ms=200):
        target = max(0, min(100, float(pct or 0)))
        start = self.value
        steps = max(1, duration_ms // 25)
        if self._job:
            self.canvas.after_cancel(self._job)

        def tick(step=1):
            self.value = start + (target - start) * (step / steps)
            self._draw()
            if step < steps:
                self._job = self.canvas.after(25, lambda: tick(step + 1))
            else:
                self._job = None

        tick()

    def _draw(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, self.width, self.height, fill=self.track_color, width=0)
        self.canvas.create_rectangle(
            0,
            0,
            self.width * (self.value / 100),
            self.height,
            fill=self.fill_color,
            width=0,
        )
