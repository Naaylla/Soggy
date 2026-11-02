import random
import tkinter as tk

from .config import (
    CYCLE, DRAG_THRESHOLD, FRICTION, GRAVITY, PHYSICS_MS, QUOTE_MS,
    SCALE, STEP_MS, STEP_PX, TASKBAR_HEIGHT, TEAR_MS, TRANSPARENT_KEY,
    WINDOW_H, WINDOW_W,
)
from .quotes import QUOTES, Z_SHAPE, bubble_rects
from .sprites import (
    FRAME_SIT, FRAME_SLEEP, FRAME_WALK, PALETTE, SIDE, tear_phase,
)


class SoggyPet:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Soggy")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=TRANSPARENT_KEY)

        try:
            self.root.attributes("-transparentcolor", TRANSPARENT_KEY)
        except tk.TclError:
            pass

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        margin = (WINDOW_W - len(SIDE[0]) * SCALE) // 2

        self.min_x = -margin
        self.max_x = screen_w - WINDOW_W + margin
        self.ground = screen_h - WINDOW_H - TASKBAR_HEIGHT

        self.x = float(screen_w - WINDOW_W - 40)
        self.y = float(self.ground)
        self.vx = self.vy = 0.0
        self._last_geom = None
        self.root.geometry(f"{WINDOW_W}x{WINDOW_H}+{int(self.x)}+{int(self.y)}")

        self.canvas = tk.Canvas(
            self.root,
            width=WINDOW_W,
            height=WINDOW_H,
            bg=TRANSPARENT_KEY,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack()

        self._jobs = []
        self._hide_job = None
        self.state = "sit"
        self.direction = 1
        self.walk_frame = 0
        self.zzz_step = 0
        self.cycle_i = 0
        self.tear_t = 0
        self.frame = FRAME_SIT
        self.flip = False
        self.sx = self.sy = 0
        self.cell_w = self.cell_h = SCALE

        self.dragging = False
        self.vanishing = False
        self.press_xy = (0, 0)
        self.grab = (0, 0)
        self.prev_xy = (self.x, self.y)

        self._enter_state("sit")

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.on_right_click)

        self.root.after(PHYSICS_MS, self._physics)
        self.root.after(TEAR_MS, self._tear_tick)


    def _render(self, frame, flip=False, squash=1.0):
        self.frame, self.flip = frame, flip
        grid = frame["grid"]
        width = len(grid[0])

        self.cell_w = SCALE / squash
        self.cell_h = SCALE * squash
        self.sx = (WINDOW_W - width * self.cell_w) / 2
        self.sy = WINDOW_H - len(grid) * self.cell_h

        self.canvas.delete("sprite")
        for row_index, line in enumerate(grid):
            col = 0
            while col < width:
                letter = line[col]
                color = PALETTE.get(letter)
                if color is None:
                    col += 1
                    continue

                end = col
                while end + 1 < width and line[end + 1] == letter:
                    end += 1

                left, right = (
                    (width - 1 - end, width - 1 - col)
                    if flip else (col, end)
                )
                self.canvas.create_rectangle(
                    self.sx + left * self.cell_w,
                    self.sy + row_index * self.cell_h,
                    self.sx + (right + 1) * self.cell_w,
                    self.sy + (row_index + 1) * self.cell_h,
                    fill=color,
                    outline="",
                    tags="sprite",
                )
                col = end + 1
        self._draw_tears()

    def _cell(self, col, row, tag):
        width = len(self.frame["grid"][0])
        if self.flip:
            col = width - 1 - col
        x = self.sx + col * self.cell_w
        y = self.sy + row * self.cell_h
        self.canvas.create_rectangle(
            x, y, x + self.cell_w, y + self.cell_h,
            fill=PALETTE["T"], outline="", tags=tag
        )

    def _draw_tears(self):
        self.canvas.delete("tear")
        for (col, row), offset in zip(
            self.frame["tears"], self.frame["offsets"]
        ):
            in_eye, drop = tear_phase((self.tear_t + offset) % 8)
            if in_eye:
                self._cell(col, row, "tear")
            if drop:
                self._cell(col, row + drop, "tear")
        self._raise()

    def _raise(self):
        for tag in ("tear", "zzz", "bubble"):
            self.canvas.tag_raise(tag)

    def _draw_zzz(self, count):
        self.canvas.delete("zzz")
        col, row = self.frame["head_top"]
        bx = self.sx + col * self.cell_w
        by = self.sy + row * self.cell_h - 3

        for i in range(count):
            cell = 2 if i < 2 else 3
            zx = bx + i * 7
            zy = by - 4 - i * 8 - cell * 3
            for color, offset in (("#1a1209", 1), ("#ffffff", 0)):
                for r, line in enumerate(Z_SHAPE):
                    for c, char in enumerate(line):
                        if char == "#":
                            x = zx + c * cell + offset
                            y = zy + r * cell + offset
                            self.canvas.create_rectangle(
                                x, y, x + cell, y + cell,
                                fill=color, outline="", tags="zzz"
                            )
        self._raise()


    def _later(self, ms, func):
        self._jobs.append(self.root.after(ms, func))

    def _cancel_jobs(self):
        for job in self._jobs:
            try:
                self.root.after_cancel(job)
            except tk.TclError:
                pass
        self._jobs.clear()

    def _enter_state(self, state, direction=1):
        self._cancel_jobs()
        self.canvas.delete("zzz")
        self.state = state

        if state in ("sit", "held", "air"):
            self._render(FRAME_SIT, squash=0.78 if state == "held" else 1.0)
            if state == "sit":
                self._later(random.randint(2500, 4500), self._next_in_cycle)

        elif state == "bump":

            self._render(FRAME_SIT, squash=1.28)
            self._later(90, lambda: self._render(FRAME_SIT, squash=0.91))
            self._later(170, lambda: self._render(FRAME_SIT, squash=1.0))
            self._later(210, lambda: self._enter_state("sit"))

        elif state == "walk":
            self.direction = direction
            self.walk_frame = 0
            self._render(FRAME_WALK[0], direction > 0)
            self._later(STEP_MS, self._walk_step)
            self._later(
                random.randint(3000, 5000),
                lambda: self._enter_state("sit")
            )

        elif state == "sleep":
            self._render(FRAME_SLEEP)
            self.zzz_step = 0
            self._later(200, self._zzz_tick)
            self._later(
                random.randint(6000, 9000),
                lambda: self._enter_state("sit")
            )

    def _next_in_cycle(self):
        action = CYCLE[self.cycle_i % len(CYCLE)]
        self.cycle_i += 1
        if action == "sleep":
            self._enter_state("sleep")
        else:
            self._enter_state("walk", 1 if action == "right" else -1)

    def _walk_step(self):
        if self.state != "walk":
            return

        self.x += self.direction * STEP_PX
        if self.x <= self.min_x:
            self.x, self.direction = self.min_x, 1
        elif self.x >= self.max_x:
            self.x, self.direction = self.max_x, -1

        self.walk_frame = (self.walk_frame + 1) % len(FRAME_WALK)
        self._render(FRAME_WALK[self.walk_frame], self.direction > 0)
        self._later(STEP_MS, self._walk_step)

    def _tear_tick(self):
        if self.vanishing:
            return
        self.tear_t = (self.tear_t + 1) % 8
        self._draw_tears()
        self.root.after(TEAR_MS, self._tear_tick)

    def _zzz_tick(self):
        if self.state != "sleep":
            return
        self.zzz_step = (self.zzz_step + 1) % 3
        self._draw_zzz(self.zzz_step + 1)
        self._later(700, self._zzz_tick)


    def _physics(self):
        if self.vanishing:
            return
        if self.dragging:
            self.vx = 0.5 * self.vx + 0.5 * (self.x - self.prev_xy[0])
            self.vy = 0.5 * self.vy + 0.5 * (self.y - self.prev_xy[1])
            self.prev_xy = (self.x, self.y)
        else:
            on_ground = self.y >= self.ground - 0.5
            if not on_ground:
                self.vy += GRAVITY

            self.x += self.vx
            self.y += self.vy

            if on_ground:
                self.vx *= FRICTION
                if abs(self.vx) < 0.3:
                    self.vx = 0.0
            else:
                self.vx *= 0.995

            if self.x < self.min_x:
                self.x, self.vx = self.min_x, abs(self.vx) * 0.5
            elif self.x > self.max_x:
                self.x, self.vx = self.max_x, -abs(self.vx) * 0.5

            if self.y < 0:
                self.y, self.vy = 0.0, abs(self.vy) * 0.5

            if self.y >= self.ground:
                just_landed = self.state == "air" and self.vy > 0
                self.y, self.vy = float(self.ground), 0.0
                if just_landed:
                    self.vx *= 0.7
                    self._enter_state("bump")
            elif self.state not in ("held", "air"):
                self._enter_state("air")

        geometry = (int(self.x), int(self.y))
        if geometry != self._last_geom:
            self._last_geom = geometry
            self.root.geometry(f"+{geometry[0]}+{geometry[1]}")

        self.root.after(PHYSICS_MS, self._physics)


    def on_press(self, event):
        self.press_xy = (event.x_root, event.y_root)
        self.grab = (event.x_root - self.x, event.y_root - self.y)
        self.dragging = False

    def on_drag(self, event):
        if not self.dragging:
            moved = (
                abs(event.x_root - self.press_xy[0])
                + abs(event.y_root - self.press_xy[1])
            )
            if moved < DRAG_THRESHOLD:
                return
            self.dragging = True
            self.vx = self.vy = 0.0
            self.prev_xy = (self.x, self.y)
            self._enter_state("held")

        self.x = max(
            self.min_x, min(self.max_x, event.x_root - self.grab[0])
        )
        self.y = max(0, min(self.ground, event.y_root - self.grab[1]))

    def on_release(self, event):
        if not self.dragging:
            self.show_quote()
            return

        self.dragging = False
        self.vx = max(-40.0, min(40.0, self.vx))
        self.vy = max(-40.0, min(40.0, self.vy))

        if self.y < self.ground - 0.5:
            self._enter_state("air")
        else:
            self._enter_state("bump")

    def show_quote(self):
        if self._hide_job is not None:
            try:
                self.root.after_cancel(self._hide_job)
            except tk.TclError:
                pass
        self.canvas.delete("bubble")
        for x0, y0, x1, y1, color in bubble_rects(random.choice(QUOTES)):
            self.canvas.create_rectangle(
                x0, y0, x1, y1, fill=color, outline="", tags="bubble"
            )
        self._raise()
        self._hide_job = self.root.after(QUOTE_MS, self.hide_quote)

    def hide_quote(self):
        self.canvas.delete("bubble")
        self._hide_job = None

    def on_right_click(self, event):
        if self.vanishing:
            return
        self.vanishing = True
        self._cancel_jobs()
        self.canvas.delete("sprite", "tear", "zzz", "bubble")
        self._vanish_particles = []
        grid = self.frame["grid"]
        width = len(grid[0])
        center_x = self.sx + width * self.cell_w / 2
        center_y = self.sy + len(grid) * self.cell_h / 2

        for row, line in enumerate(grid):
            for col, letter in enumerate(line):
                if letter not in PALETTE or random.random() > 0.12:
                    continue
                draw_col = width - 1 - col if self.flip else col
                x0 = self.sx + draw_col * self.cell_w
                y0 = self.sy + row * self.cell_h
                item = self.canvas.create_rectangle(
                    x0, y0, x0 + self.cell_w, y0 + self.cell_h,
                    fill="#ffffff", outline="", tags="vanish"
                )
                dx = x0 + self.cell_w / 2 - center_x
                dy = y0 + self.cell_h / 2 - center_y - 1
                length = max(1, (dx * dx + dy * dy) ** 0.5)
                speed = random.uniform(1.5, 4.5)
                vx = dx / length * speed + random.uniform(-0.7, 0.7)
                vy = dy / length * speed + random.uniform(-1.5, 0.2)
                self._vanish_particles.append((item, vx, vy))

        self.canvas.tag_raise("vanish")
        self._vanish_step(8)

    def _vanish_step(self, step):
        if step == 0:
            self.root.destroy()
            return
        for item, vx, vy in self._vanish_particles:
            self.canvas.move(item, vx, vy)
            coords = self.canvas.coords(item)
            if coords:
                x0, y0, x1, y1 = coords
                cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
                half_w, half_h = (x1 - x0) * 0.38, (y1 - y0) * 0.38
                self.canvas.coords(
                    item, cx - half_w, cy - half_h, cx + half_w, cy + half_h
                )
        self.root.after(35, lambda: self._vanish_step(step - 1))

    def run(self):
        self.root.mainloop()
