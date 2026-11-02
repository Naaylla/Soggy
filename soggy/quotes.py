"""Pixel-font quotes and speech-bubble layout."""

from .config import SCALE, WINDOW_H, WINDOW_W
from .sprites import FRONT_ROWS, PALETTE


FONT = {
    "A": (".#.", "#.#", "###", "#.#", "#.#"),
    "B": ("##.", "#.#", "##.", "#.#", "##."),
    "C": (".##", "#..", "#..", "#..", ".##"),
    "D": ("##.", "#.#", "#.#", "#.#", "##."),
    "E": ("###", "#..", "##.", "#..", "###"),
    "F": ("###", "#..", "##.", "#..", "#.."),
    "G": (".##", "#..", "#.#", "#.#", ".##"),
    "H": ("#.#", "#.#", "###", "#.#", "#.#"),
    "I": ("###", ".#.", ".#.", ".#.", "###"),
    "J": ("..#", "..#", "..#", "#.#", ".#."),
    "K": ("#.#", "#.#", "##.", "#.#", "#.#"),
    "L": ("#..", "#..", "#..", "#..", "###"),
    "M": ("#.#", "###", "###", "#.#", "#.#"),
    "N": ("##.", "#.#", "#.#", "#.#", "#.#"),
    "O": (".#.", "#.#", "#.#", "#.#", ".#."),
    "P": ("##.", "#.#", "##.", "#..", "#.."),
    "Q": (".#.", "#.#", "#.#", "##.", ".##"),
    "R": ("##.", "#.#", "##.", "#.#", "#.#"),
    "S": (".##", "#..", ".#.", "..#", "##."),
    "T": ("###", ".#.", ".#.", ".#.", ".#."),
    "U": ("#.#", "#.#", "#.#", "#.#", "###"),
    "V": ("#.#", "#.#", "#.#", "#.#", ".#."),
    "W": ("#.#", "#.#", "###", "###", "#.#"),
    "X": ("#.#", "#.#", ".#.", "#.#", "#.#"),
    "Y": ("#.#", "#.#", ".#.", ".#.", ".#."),
    "Z": ("###", "..#", ".#.", "#..", "###"),
    "'": (".#.", ".#.", "...", "...", "..."),
    ".": ("...", "...", "...", "...", ".#."),
    ",": ("...", "...", "...", ".#.", "#.."),
    ":": ("...", ".#.", "...", ".#.", "..."),
    "!": (".#.", ".#.", ".#.", "...", ".#."),
    "?": ("##.", "..#", ".#.", "...", ".#."),
    "-": ("...", "...", "###", "...", "..."),
    " ": ("...", "...", "...", "...", "..."),
}

FP = 2
CHAR_W = 4 * FP
LINE_H = 6 * FP
BUBBLE_CHARS = 20
BUBBLE_BG = "#fff8e8"
BUBBLE_FG = PALETTE["#"]

QUOTES = [
    "Nothing lasts forever, not even this feeling.",
    "Crying is just feelings leaving the body.",
    "Small steps still count, even the crying ones.",
    "Soggy is sad too. We can be sad together.",
    "It's okay to be a little lost.",
    "Tomorrow can be softer.",
]

Z_SHAPE = ("###", ".#.", "###")


def wrap_text(text):
    lines, current = [], ""
    for word in text.upper().split():
        if current and len(current) + 1 + len(word) > BUBBLE_CHARS:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}" if current else word
    if current:
        lines.append(current)
    return lines


def bubble_rects(text):
    lines = wrap_text(text)
    text_w = max(len(line) for line in lines) * CHAR_W - FP
    text_h = len(lines) * LINE_H - FP
    pad = 3 * FP
    bw = text_w + 2 * (pad + FP)
    bh = text_h + 2 * (pad + FP)
    cx = WINDOW_W // 2
    x0 = max(2, min(WINDOW_W - bw - 2, cx - bw // 2))
    x1 = x0 + bw
    y1 = WINDOW_H - FRONT_ROWS * SCALE - 8
    y0 = max(2, y1 - bh)
    b = FP

    rects = [
        (x0 + b, y0, x1 - b, y1, BUBBLE_FG),
        (x0, y0 + b, x1, y1 - b, BUBBLE_FG),
        (x0 + b, y0 + b, x1 - b, y1 - b, BUBBLE_BG),
        (cx - 4, y1 - b, cx + 4, y1, BUBBLE_BG),
        (cx - 6, y1, cx + 6, y1 + 2, BUBBLE_FG),
        (cx - 4, y1, cx + 4, y1 + 2, BUBBLE_BG),
        (cx - 4, y1 + 2, cx + 4, y1 + 4, BUBBLE_FG),
        (cx - 2, y1 + 2, cx + 2, y1 + 4, BUBBLE_BG),
        (cx - 2, y1 + 4, cx + 2, y1 + 6, BUBBLE_FG),
    ]

    for line_index, line in enumerate(lines):
        lx = x0 + (bw - (len(line) * CHAR_W - FP)) // 2
        ly = y0 + b + pad + line_index * LINE_H
        for char_index, char in enumerate(line):
            glyph = FONT.get(char, FONT[" "])
            for gy, row in enumerate(glyph):
                for gx, pixel in enumerate(row):
                    if pixel == "#":
                        x = lx + char_index * CHAR_W + gx * FP
                        y = ly + gy * FP
                        rects.append((x, y, x + FP, y + FP, BUBBLE_FG))
    return rects
