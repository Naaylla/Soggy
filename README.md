# Soggy

Soggy is a tiny, sad pixel-art cat with tears in its eyes. It lives on top of
your taskbar, always visible above other windows, and wanders left and right,
takes naps, and cries. Left-click it and it cheers you on with a hype quote.

Repo: [github.com/Naaylla/Soggy](https://github.com/Naaylla/Soggy)

## How to run it

```bash
python pet.py
```

You only need Python 3 (tkinter is included with the standard Windows/macOS
Python installers). No `pip install` required.

## How to use it

- **Left-click Soggy** - shows a random hype quote for 3 seconds.
- **Right-click Soggy** - quits the app.
- Otherwise just leave it alone: it walks, sleeps and cries on its own.
- It always stays on top, standing right above your taskbar.

## Make it your own

All the fun stuff lives at the top of `pet.py`.

**Add quotes:** edit the `QUOTES` list. Each line is one quote:

```python
QUOTES = [
    "You got this!",
    "Soggy believes in you.",
    "Your new quote goes here.",
]
```

**Change the sprite:** edit the `SPRITE_*` grids (`SPRITE_SIT`, `SPRITE_WALK_A`,
`SPRITE_WALK_B`, `SPRITE_SLEEP`, `SPRITE_CRY_A`, `SPRITE_CRY_B`). They are just
text - one letter per pixel, and `.` means transparent. Soggy is a sad cat, so
the tears (`T`) are already in every frame. Pick a color for each letter in
`PALETTE`:

```python
PALETTE = {
    "#": "#2b1d14",  # outline
    "F": "#f2a03d",  # fur
    "W": "#ffe9d6",  # chest
    "P": "#ff8fa3",  # nose
    "E": "#241a14",  # eyes
    "c": "#2b1d14",  # closed eyes
    "T": "#7fd4ff",  # tears
}
```

Want a bigger cat? Increase `SCALE` (pixels per cell). Make sure every row of
every sprite has the same number of letters.

## Build a .exe (optional)

Install PyInstaller, then package the script:

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole pet.py
```

Your app appears in the `dist` folder as `pet.exe`.

## Troubleshooting

- **The transparent background is solid/black.** Transparency only works on
  Windows (via `-transparentcolor`). On macOS and Linux the cat still works,
  but it sits on a colored square.
- **Soggy floats above your apps.** That is on purpose - it is always on top.
  Right-click it to quit.
- **Soggy is not resting on the taskbar.** Change `TASKBAR_HEIGHT` near the top
  of `pet.py` (try 40 or 60) to match your taskbar.
- **Windows Defender or antivirus flags the .exe.** This is a common false
  alarm for PyInstaller apps. Add an exception, or just run `python pet.py`.
- **Soggy is off-screen.** Edit the `self.x` / `self.y` lines in `__init__` to
  change its starting position.
