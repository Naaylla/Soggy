"""Soggy - a tiny pixel-art desktop cat.

Soggy lives on your desktop: a sad little cat with tears in its eyes. It
sits, wanders left and right, and naps (still crying a little). Left-click it
for a hype quote, right-click to quit.

Standard library only (tkinter), no extra installs needed.
Repo: https://github.com/Naaylla/Soggy
"""

import random
import tkinter as tk

# ---------------------------------------------------------------------------
# Look & feel
# ---------------------------------------------------------------------------

SCALE = 3                     # screen pixels per sprite cell (smaller = cuter)
WINDOW_W, WINDOW_H = 160, 150
TASKBAR_HEIGHT = 48           # so Soggy stands right on top of the taskbar
TRANSPARENT_KEY = "#ff00ff"   # this exact color is made invisible (Windows)
QUOTE_MS = 3000               # how long a quote stays on screen
MOVE_MS = 50                  # how often Soggy takes a step
WALK_FRAME_MS = 160           # how fast the walking legs animate
CRY_FRAME_MS = 350            # how fast the tears drip

# ---------------------------------------------------------------------------
# Sprites - one letter = one color, "." means transparent.
# Each grid is 16 x 16. Edit freely, just keep every row the same length.
# ---------------------------------------------------------------------------

SPRITE_SIT = [
    "................",
    "..#..........#..",
    "..##........##..",
    "..#F#......#F#..",
    "..#FF#....#FF#..",
    "..#FFF####FFF#..",
    "..#FFFFFFFFFF#..",
    "..#FFEFFFFEFF#..",
    "..#TFFFPPFFFT#..",
    "..#FFFFFFFFFF#..",
    "...#FFFFFFFF#...",
    "..#FFWWWWWWFF#..",
    "..#FFWWWWWWFF#..",
    "..#FFWWWWWWFF#..",
    "..#FFFFFFFFFF#..",
    "..############..",
]

SPRITE_WALK_A = [
    "................",
    "..#..........#..",
    "..##........##..",
    "..#F#......#F#..",
    "..#FF#....#FF#..",
    "..#FFF####FFF#..",
    "..#FFFFFFFFFF#..",
    "..#FFEFFFFEFF#..",
    "..#TFFFPPFFFT#..",
    "..#FFFFFFFFFF#..",
    "...#FFFFFFFF#...",
    "..#FFWWWWWWFF#..",
    "..#FFWWWWWWFF#..",
    "..#FFWWWWWWFF#..",
    "..#FFFFFFFFFF#..",
    "..##FF####FF##..",
]

SPRITE_WALK_B = [
    "................",
    "..#..........#..",
    "..##........##..",
    "..#F#......#F#..",
    "..#FF#....#FF#..",
    "..#FFF####FFF#..",
    "..#FFFFFFFFFF#..",
    "..#FFEFFFFEFF#..",
    "..#TFFFPPFFFT#..",
    "..#FFFFFFFFFF#..",
    "...#FFFFFFFF#...",
    "..#FFWWWWWWFF#..",
    "..#FFWWWWWWFF#..",
    "..#FFWWWWWWFF#..",
    "...#FFFFFFFF#...",
    "...#FF####FF#...",
]

SPRITE_SLEEP = [
    "................",
    "..#..........#..",
    "..##........##..",
    "..#F#......#F#..",
    "..#FF#....#FF#..",
    "..#FFF####FFF#..",
    "..#FFFFFFFFFF#..",
    "..#FcccFFcccF#..",
    "..#TFFFPPFFFT#..",
    "..#FFFFFFFFFF#..",
    "...#FFFFFFFF#...",
    "..#FFWWWWWWFF#..",
    "..#FFWWWWWWFF#..",
    "..#FFWWWWWWFF#..",
    "..#FFFFFFFFFF#..",
    "..############..",
]

SPRITE_CRY_A = [
    "................",
    "..#..........#..",
    "..##........##..",
    "..#F#......#F#..",
    "..#FF#....#FF#..",
    "..#FFF####FFF#..",
    "..#FFFFFFFFFF#..",
    "..#FFEFFFFEFF#..",
    "..#TFFFPPFFFT#..",
    "..#FFFFFFFFFF#..",
    "...#FFFFFFFF#...",
    "..#FFWWWWWWFF#..",
    "..#FFWWWWWWFF#..",
    "..#FFWWWWWWFF#..",
    "..#FFFFFFFFFF#..",
    "..############..",
]

SPRITE_CRY_B = [
    "................",
    "..#..........#..",
    "..##........##..",
    "..#F#......#F#..",
    "..#FF#....#FF#..",
    "..#FFF####FFF#..",
    "..#FFFFFFFFFF#..",
    "..#FFEFFFFEFF#..",
    "..#TFFFPPFFFT#..",
    "..#TFFFFFFFFT#..",
    "...#FFFFFFFF#...",
    "..#FFWWWWWWFF#..",
    "..#FFWWWWWWFF#..",
    "..#FFWWWWWWFF#..",
    "..#FFFFFFFFFF#..",
    "..############..",
]

# Every letter used above must have a color here.
PALETTE = {
    "#": "#2b1d14",  # outline
    "F": "#f2a03d",  # fur
    "W": "#ffe9d6",  # chest / belly
    "P": "#ff8fa3",  # nose
    "E": "#241a14",  # eyes
    "c": "#2b1d14",  # closed eyes (sleeping)
    "T": "#7fd4ff",  # tears
}

# Add, remove or edit quotes here. Keep them short so they fit the bubble.
QUOTES = [
    "You got this!",
    "Soggy believes in you.",
    "One small step, then snacks.",
    "Be the main character today.",
    "Nap now, conquer later.",
    "That idea? Kind of genius.",
    "Drink some water, legend.",
    "You're doing better than you think.",
    "Today's vibe: unstoppable.",
    "Soggy is proud of you.",
]


class SoggyPet:
    """The whole app: one small, borderless, transparent desktop window."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Soggy")
        self.root.overrideredirect(True)        # no title bar, no borders
        self.root.attributes("-topmost", True)  # visible on top of everything
        self.root.configure(bg=TRANSPARENT_KEY)

        try:
            # Anything painted in TRANSPARENT_KEY becomes see-through.
            self.root.attributes("-transparentcolor", TRANSPARENT_KEY)
        except tk.TclError:
            pass  # not supported here (e.g. macOS/Linux): window stays solid

        # Soggy always floats on top, standing just above the taskbar.
        self.x = self.root.winfo_screenwidth() - WINDOW_W - 40
        self.y = self.root.winfo_screenheight() - WINDOW_H - TASKBAR_HEIGHT
        self.root.geometry(f"{WINDOW_W}x{WINDOW_H}+{self.x}+{self.y}")

        self.canvas = tk.Canvas(
            self.root,
            width=WINDOW_W,
            height=WINDOW_H,
            bg=TRANSPARENT_KEY,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack()

        self._jobs = []          # pending animation / behavior timers
        self._hide_job = None    # timer that hides the quote
        self.state = "sit"
        self.direction = 1
        self.walk_frame = 0
        self.cry_frame = 0
        self.zzz_step = 0

        self._create_overlays()
        self._enter_state("sit")

        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<Button-3>", self.on_right_click)

    # -- drawing -----------------------------------------------------------
    def _render_sprite(self, grid):
        """Turn a text grid into colored rectangles on the canvas."""
        self.canvas.delete("sprite")
        rows = len(grid)
        cols = len(grid[0])
        x0 = (WINDOW_W - cols * SCALE) // 2
        y0 = WINDOW_H - rows * SCALE - 16

        for row, line in enumerate(grid):
            for col, letter in enumerate(line):
                color = PALETTE.get(letter)
                if color is None:
                    continue  # "." or unknown letter = transparent pixel
                left = x0 + col * SCALE
                top = y0 + row * SCALE
                self.canvas.create_rectangle(
                    left, top, left + SCALE, top + SCALE,
                    fill=color, outline="", tags="sprite",
                )

    def _create_overlays(self):
        """Create the hidden speech bubble, quote text and sleeping Zzz."""
        self.bubble = self.canvas.create_rectangle(
            0, 0, 0, 0,
            fill="#fffdf7", outline=PALETTE["#"], width=2,
            state="hidden",
        )
        self.text = self.canvas.create_text(
            WINDOW_W // 2, 36,
            text="", width=WINDOW_W - 30,
            font=("Segoe UI", 8, "bold"),
            fill=PALETTE["#"], justify="center",
            state="hidden",
        )
        self.zzz = self.canvas.create_text(
            122, 74,
            text="z", font=("Segoe UI", 9, "bold"),
            fill="#5a4636", state="hidden",
        )

    # -- timers ------------------------------------------------------------
    def _later(self, ms, func):
        """Schedule a callback and remember it so it can be cancelled."""
        self._jobs.append(self.root.after(ms, func))

    def _cancel_jobs(self):
        for job in self._jobs:
            try:
                self.root.after_cancel(job)
            except tk.TclError:
                pass
        self._jobs.clear()

    # -- behavior state machine -------------------------------------------
    def _enter_state(self, state):
        """Switch to sit / walk / sleep / cry, then return to sitting later."""
        self._cancel_jobs()
        self.canvas.itemconfigure(self.zzz, state="hidden")
        self.state = state

        if state == "sit":
            self._render_sprite(SPRITE_SIT)
            self._later(random.randint(3000, 7000), self._pick_behavior)

        elif state == "walk":
            self.direction = random.choice((-1, 1))
            self.walk_frame = 0
            self._render_sprite(SPRITE_WALK_A)
            self._later(MOVE_MS, self._move)
            self._later(WALK_FRAME_MS, self._walk_tick)
            self._later(random.randint(2000, 5000),
                        lambda: self._enter_state("sit"))

        elif state == "sleep":
            self._render_sprite(SPRITE_SLEEP)
            self.zzz_step = 0
            self._later(200, self._zzz_tick)
            self._later(random.randint(6000, 10000),
                        lambda: self._enter_state("sit"))

        elif state == "cry":
            self.cry_frame = 0
            self._render_sprite(SPRITE_CRY_A)
            self._later(CRY_FRAME_MS, self._cry_tick)
            self._later(random.randint(2500, 4500),
                        lambda: self._enter_state("sit"))

    def _pick_behavior(self):
        """After a little sitting around, do something cute."""
        self._enter_state(
            random.choices(["walk", "sleep", "cry"], weights=[5, 3, 2])[0]
        )

    # -- animations --------------------------------------------------------
    def _move(self):
        if self.state != "walk":
            return
        self.x += self.direction * 2
        max_x = self.root.winfo_screenwidth() - WINDOW_W
        if self.x <= 0:
            self.x, self.direction = 0, 1
        elif self.x >= max_x:
            self.x, self.direction = max_x, -1
        self.root.geometry(f"+{self.x}+{self.y}")
        self._later(MOVE_MS, self._move)

    def _walk_tick(self):
        if self.state != "walk":
            return
        self.walk_frame = 1 - self.walk_frame
        self._render_sprite(
            SPRITE_WALK_A if self.walk_frame == 0 else SPRITE_WALK_B
        )
        self._later(WALK_FRAME_MS, self._walk_tick)

    def _cry_tick(self):
        if self.state != "cry":
            return
        self.cry_frame = 1 - self.cry_frame
        self._render_sprite(
            SPRITE_CRY_A if self.cry_frame == 0 else SPRITE_CRY_B
        )
        self._later(CRY_FRAME_MS, self._cry_tick)

    def _zzz_tick(self):
        if self.state != "sleep":
            return
        self.zzz_step = (self.zzz_step + 1) % 3
        self.canvas.itemconfigure(
            self.zzz,
            text=("z", "z z", "z z z")[self.zzz_step],
            state="normal",
        )
        self.canvas.coords(self.zzz, 122, 74 - self.zzz_step * 4)
        self._later(700, self._zzz_tick)

    # -- interaction -------------------------------------------------------
    def on_left_click(self, event):
        """Show a random hype quote for QUOTE_MS milliseconds."""
        if self._hide_job is not None:
            self.root.after_cancel(self._hide_job)

        self.canvas.itemconfigure(
            self.text, text=random.choice(QUOTES), state="normal"
        )

        # Size the bubble around whatever the wrapped text became.
        left, top, right, bottom = self.canvas.bbox(self.text)
        pad = 8
        self.canvas.coords(
            self.bubble,
            left - pad, top - pad, right + pad, bottom + pad,
        )
        self.canvas.itemconfigure(self.bubble, state="normal")
        self.canvas.tag_raise(self.text)  # words stay above the bubble

        self._hide_job = self.root.after(QUOTE_MS, self.hide_quote)

    def hide_quote(self):
        """Hide the quote again."""
        self.canvas.itemconfigure(self.text, state="hidden")
        self.canvas.itemconfigure(self.bubble, state="hidden")
        self._hide_job = None

    def on_right_click(self, event):
        """Right-click quits the app."""
        self.root.destroy()

    # -- main loop ---------------------------------------------------------
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    SoggyPet().run()
