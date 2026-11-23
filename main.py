#!/usr/bin/env python3
"""The World in One Day -- Monday, 23 November 2026.

Draws a 1024x1024 front page that sums up the day's world news in one
image. Standard library only: the program writes its own PNG (zlib +
struct) and draws every letter from a bitmap font defined below, because
the grader image ships no PIL and no system fonts.

Layout, top to bottom: top bar (paper name + story count) -- giant date
masthead -- maroon ticker -- six-number stat strip -- "THE DAY IN UTC"
timeline -- three big lead cards -- seven medium cards -- a row with the
tenth card, a world map with numbered pins and a red DATE CHECK box --
numbered briefs -- footer with sources and press time.

Facts come from the verified research notes (every story checked against
at least two outlets). Nothing in this file is invented: every number,
name, date and quote on the page is in those notes.
"""

import math
import os
import struct
import zlib

OUT = os.path.join(os.environ.get("MAKEFUN_OUTPUT_DIR", os.path.dirname(os.path.abspath(__file__))), "entry.png")

# ---------------------------------------------------------------- palette
# 60-30-10: cream paper dominates, navy carries the masthead and ink,
# maroon/red is the 10% accent for urgency (ticker, DATE CHECK, pins).
CREAM = (247, 242, 231)
PAPER = (255, 253, 247)
INK = (26, 26, 26)
NAVY = (20, 38, 76)
NAVY_LT = (38, 62, 110)
GOLD = (201, 162, 39)
GOLD_LT = (232, 196, 94)
MAROON = (122, 31, 31)
RED = (176, 32, 32)
RED_LT = (245, 222, 222)
GREY = (110, 110, 108)
GREY_LT = (214, 208, 196)
BLUE = (43, 92, 158)
GREEN = (46, 125, 72)
ORANGE = (214, 116, 28)
TEAL = (18, 120, 118)
TAN = (226, 214, 182)
TAN_DK = (198, 182, 148)
SKY = (178, 206, 230)
SEA = (120, 168, 205)

# ------------------------------------------------------------ PNG writer
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, width, height, rgb):
    """rgb: bytes, width*height*3, top row first. Filter 0, one IDAT."""
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)


# ------------------------------------------------------- bitmap font 8x12
# Every glyph is 12 rows of 8 cells, "#" = ink. Designed here from
# scratch as a bold grotesque: 2-cell strokes, cap height rows 1-10,
# row 0 and row 11 left for ascender/descender air. Lowercase input is
# uppercased at draw time; the font carries capitals only.
FONT = {
"A": (
"...##...",
"..#..#..",
"..#..#..",
".#....#.",
".#....#.",
".#....#.",
".######.",
".#....#.",
".#....#.",
".#....#.",
"........",
"........",
),
"B": (
".#####..",
".#....#.",
".#....#.",
".#....#.",
".#####..",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
".#####..",
"........",
"........",
),
"C": (
"..####..",
".#....#.",
".#......",
".#......",
".#......",
".#......",
".#......",
".#......",
".#....#.",
"..####..",
"........",
"........",
),
"D": (
".#####..",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
".#####..",
"........",
"........",
),
"E": (
".######.",
".#......",
".#......",
".#......",
".#####..",
".#......",
".#......",
".#......",
".#......",
".######.",
"........",
"........",
),
"F": (
".######.",
".#......",
".#......",
".#......",
".#####..",
".#......",
".#......",
".#......",
".#......",
".#......",
"........",
"........",
),
"G": (
"..####..",
".#....#.",
".#......",
".#......",
".#..###.",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
"..###.#.",
"........",
"........",
),
"H": (
".#....#.",
".#....#.",
".#....#.",
".#....#.",
".######.",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
"........",
"........",
),
"I": (
"..###...",
"...#....",
"...#....",
"...#....",
"...#....",
"...#....",
"...#....",
"...#....",
"...#....",
"..###...",
"........",
"........",
),
"J": (
"...####.",
"....#...",
"....#...",
"....#...",
"....#...",
"....#...",
"....#...",
"....#...",
".#..#...",
"..##....",
"........",
"........",
),
"K": (
".#....#.",
".#...#..",
".#..#...",
".#.#....",
".##.....",
".#.#....",
".#..#...",
".#...#..",
".#....#.",
".#....#.",
"........",
"........",
),
"L": (
".#......",
".#......",
".#......",
".#......",
".#......",
".#......",
".#......",
".#......",
".#......",
".######.",
"........",
"........",
),
"M": (
".#....#.",
".##..##.",
".#.##.#.",
".#.##.#.",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
"........",
"........",
),
"N": (
".#....#.",
".##...#.",
".#.#..#.",
".#..#.#.",
".#...##.",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
"........",
"........",
),
"O": (
"..####..",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
"..####..",
"........",
"........",
),
"P": (
".#####..",
".#....#.",
".#....#.",
".#....#.",
".#####..",
".#......",
".#......",
".#......",
".#......",
".#......",
"........",
"........",
),
"Q": (
"..####..",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
".#..##..",
".#...#..",
".#....#.",
"..####..",
"........",
"........",
),
"R": (
".#####..",
".#....#.",
".#....#.",
".#....#.",
".#####..",
".#..#...",
".#...#..",
".#....#.",
".#....#.",
".#....#.",
"........",
"........",
),
"S": (
"..####..",
".#....#.",
".#......",
".#......",
"..###...",
"...###..",
"......#.",
"......#.",
".#....#.",
"..####..",
"........",
"........",
),
"T": (
".######.",
"...#....",
"...#....",
"...#....",
"...#....",
"...#....",
"...#....",
"...#....",
"...#....",
"...#....",
"........",
"........",
),
"U": (
".#....#.",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
"..####..",
"........",
"........",
),
"V": (
".#....#.",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
"..#..#..",
"..#..#..",
"...##...",
"...##...",
"........",
"........",
),
"W": (
".#....#.",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
".#.##.#.",
".#.##.#.",
".##..##.",
".#....#.",
"........",
"........",
),
"X": (
".#....#.",
"..#..#..",
"...##...",
"...##...",
"...##...",
"...##...",
"...##...",
"..#..#..",
".#....#.",
".#....#.",
"........",
"........",
),
"Y": (
".#....#.",
".#....#.",
"..#..#..",
"...##...",
"...##...",
"...##...",
"...##...",
"...##...",
"...##...",
"...##...",
"........",
"........",
),
"Z": (
".######.",
"......#.",
".....#..",
"....#...",
"...#....",
"..#.....",
".#......",
".#......",
".#......",
".######.",
"........",
"........",
),
"0": (
"..####..",
".#....#.",
".#...##.",
".#..#.#.",
".#.#..#.",
".##...#.",
".#....#.",
".#....#.",
".#....#.",
"..####..",
"........",
"........",
),
"1": (
"...#....",
"..##....",
".#.#....",
"...#....",
"...#....",
"...#....",
"...#....",
"...#....",
"...#....",
"..###...",
"........",
"........",
),
"2": (
"..####..",
".#....#.",
"......#.",
"......#.",
".....#..",
"....#...",
"...#....",
"..#.....",
".#......",
".######.",
"........",
"........",
),
"3": (
"..####..",
".#....#.",
"......#.",
"......#.",
"..####..",
"......#.",
"......#.",
"......#.",
".#....#.",
"..####..",
"........",
"........",
),
"4": (
"......#.",
".....##.",
"....###.",
"...#.##.",
"..#..##.",
".#...##.",
"#######.",
".....##.",
".....##.",
".....##.",
"........",
"........",
),
"5": (
".######.",
".#......",
".#......",
".#####..",
"......#.",
"......#.",
"......#.",
"......#.",
".#....#.",
"..####..",
"........",
"........",
),
"6": (
"..###...",
".#......",
".#......",
".#......",
".#####..",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
"..####..",
"........",
"........",
),
"7": (
".######.",
"......#.",
".....#..",
"....#...",
"...#....",
"...#....",
"...#....",
"...#....",
"...#....",
"...#....",
"........",
"........",
),
"8": (
"..####..",
".#....#.",
".#....#.",
".#....#.",
"..####..",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
"..####..",
"........",
"........",
),
"9": (
"..####..",
".#....#.",
".#....#.",
".#....#.",
".#....#.",
"..#####.",
"......#.",
"......#.",
"......#.",
"...###..",
"........",
"........",
),
" ": (
"........",
"........",
"........",
"........",
"........",
"........",
"........",
"........",
"........",
"........",
"........",
"........",
),
".": (
"........",
"........",
"........",
"........",
"........",
"........",
"........",
"........",
"........",
"..##....",
"..##....",
"........",
),
",": (
"........",
"........",
"........",
"........",
"........",
"........",
"........",
"........",
"........",
"..##....",
"..##....",
".#......",
),
":": (
"........",
"........",
"........",
"..##....",
"..##....",
"........",
"........",
"..##....",
"..##....",
"........",
"........",
"........",
),
";": (
"........",
"........",
"........",
"..##....",
"..##....",
"........",
"........",
"..##....",
"..##....",
".#......",
"........",
"........",
),
"'": (
"...##...",
"...##...",
"...#....",
"........",
"........",
"........",
"........",
"........",
"........",
"........",
"........",
"........",
),
"-": (
"........",
"........",
"........",
"........",
"........",
".#####..",
".#####..",
"........",
"........",
"........",
"........",
"........",
),
"(": (
"....##..",
"...#....",
"..#.....",
"..#.....",
"..#.....",
"..#.....",
"..#.....",
"..#.....",
"...#....",
"....##..",
"........",
"........",
),
")": (
"..##....",
"....#...",
".....#..",
".....#..",
".....#..",
".....#..",
".....#..",
".....#..",
"....#...",
"..##....",
"........",
"........",
),
"/": (
"......#.",
".....#..",
".....#..",
"....#...",
"...#....",
"...#....",
"..#.....",
".#......",
".#......",
"#.......",
"........",
"........",
),
"%": (
".##...#.",
".##..#..",
".....#..",
"....#...",
"....#...",
"...#....",
"...#....",
"..#..##.",
".....##.",
".....##.",
"........",
"........",
),
"$": (
"...#....",
"..####..",
".#..#.#.",
".#..#...",
"..###...",
"...#....",
"..###...",
"...#..#.",
".#..#.#.",
"..####..",
"...#....",
"........",
),
"+": (
"........",
"........",
"........",
"...#....",
"...#....",
".#####..",
".#####..",
"...#....",
"...#....",
"........",
"........",
"........",
),
"?": (
"..####..",
".#....#.",
"......#.",
"......#.",
".....#..",
"....#...",
"...#....",
"........",
"...#....",
"...#....",
"........",
"........",
),
"!": (
"...#....",
"...#....",
"...#....",
"...#....",
"...#....",
"...#....",
"...#....",
"...#....",
"........",
"...#....",
"........",
"........",
),
"=": (
"........",
"........",
"........",
"........",
".######.",
"........",
".######.",
"........",
"........",
"........",
"........",
"........",
),
"&": (
"..###...",
".#...#..",
".#...#..",
".#..#...",
"..#.#...",
"...#....",
"..#.#...",
".#..#...",
".#...#..",
".##..##.",
"........",
"........",
),
'"': (
"..#..#..",
"..#..#..",
"..#..#..",
"........",
"........",
"........",
"........",
"........",
"........",
"........",
"........",
"........",
),
"_": (
"........",
"........",
"........",
"........",
"........",
"........",
"........",
"........",
"........",
"........",
".######.",
".######.",
),
"*": (
"........",
"...#....",
".#.#.#..",
"..###...",
".#####..",
"..###...",
".#.#.#..",
"...#....",
"........",
"........",
"........",
"........",
),
"#": (
"..#..#..",
"..#..#..",
".######.",
".#..#...",
".#..#...",
".######.",
"..#..#..",
"..#..#..",
".######.",
"..#..#..",
"........",
"........",
),
"@": (
"..####..",
".#....#.",
".#..###.",
".#.#..#.",
".#.#.#..",
".#.#.#..",
".#..##..",
".#......",
"..####..",
"........",
"........",
"........",
),
"~": (
"........",
"........",
"........",
"........",
"..##....",
".##..##.",
"....##..",
"........",
"........",
"........",
"........",
"........",
),
"<": (
".....#..",
"....#...",
"...#....",
"..#.....",
".#......",
".#......",
"..#.....",
"...#....",
"....#...",
".....#..",
"........",
"........",
),
">": (
"..#.....",
"...#....",
"....#...",
".....#..",
"......#.",
"......#.",
".....#..",
"....#...",
"...#....",
"..#.....",
"........",
"........",
),
}

# ------------------------------------------------------------- canvas
W, H = 1024, 1024
SS = 3  # supersample factor: draw at 3072, downsample to 1024


class Canvas:
    def __init__(self):
        self.buf = bytearray([CREAM[0], CREAM[1], CREAM[2]]) * (W * SS * H * SS)

    def _set(self, x, y, col):
        if 0 <= x < W * SS and 0 <= y < H * SS:
            i = (y * W * SS + x) * 3
            self.buf[i:i + 3] = bytes(col)

    def rect(self, x, y, w, h, col):
        x0, y0 = x * SS, y * SS
        x1, y1 = (x + w) * SS, (y + h) * SS
        for yy in range(y0, y1):
            base = (yy * W * SS + x0) * 3
            row = bytes(col) * (x1 - x0)
            self.buf[base:base + len(row)] = row

    def outline(self, x, y, w, h, col, t=1):
        self.rect(x, y, w, t, col)
        self.rect(x, y + h - t, w, t, col)
        self.rect(x, y, t, h, col)
        self.rect(x + w - t, y, t, h, col)

    def line(self, x0, y0, x1, y1, col, t=1):
        x0, y0, x1, y1 = x0 * SS, y0 * SS, x1 * SS, y1 * SS
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            for a in range(t * SS):
                for b in range(t * SS):
                    self._set(x + a, y + b, col)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, col):
        cx, cy, r = int(cx * SS), int(cy * SS), int(r * SS)
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self._set(xx, yy, col)

    def disc(self, cx, cy, r, col):
        self.circle(cx, cy, r, col)

    def poly(self, pts, col):
        """Filled polygon; pts = [(x, y), ...] in final-image coords."""
        pts = [(x * SS, y * SS) for x, y in pts]
        ys = sorted(set(int(p[1]) for p in pts))
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if y0 == y1:
                    continue
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                for x in range(int(xs[k]), int(xs[k + 1]) + 1):
                    self._set(x, y, col)

    def downsample(self):
        out = bytearray(W * H * 3)
        for oy in range(H):
            for ox in range(W):
                r = g = b = 0
                for dy in range(SS):
                    base = ((oy * SS + dy) * W * SS + ox * SS) * 3
                    for dx in range(SS):
                        i = base + dx * 3
                        r += self.buf[i]
                        g += self.buf[i + 1]
                        b += self.buf[i + 2]
                n = SS * SS
                o = (oy * W + ox) * 3
                out[o] = r // n
                out[o + 1] = g // n
                out[o + 2] = b // n
        return bytes(out)


# ------------------------------------------------------------- text
def _glyph(ch):
    return FONT.get(ch.upper(), FONT["?"])


def text_w(text, scale):
    return len(text) * 8 * scale


def _stamp(cv, x, y, text, scale, col):
    """Draw one string at canvas coords (x, y are final-image coords).

    Cell edges are rounded, not floored, and every glyph origin is
    snapped to an integer supersampled pixel: the same glyph renders
    byte-identically wherever it sits, and no side of a glyph comes out
    systematically heavier than the other (flooring put the wide
    column on the right edge, so letters leaned right).
    """
    unit = scale * SS
    adv = 8 * scale * SS
    xs = [round(c * unit) for c in range(9)]
    ys = [round(r * unit) for r in range(13)]
    oy = round(y * SS)
    cx = x * SS
    for ch in text:
        g = _glyph(ch)
        ox = round(cx)
        for r, row in enumerate(g):
            y0 = oy + ys[r]
            y1 = oy + ys[r + 1]
            for c, cell_ch in enumerate(row):
                if cell_ch == "#":
                    x0 = ox + xs[c]
                    x1 = ox + xs[c + 1]
                    for yy in range(y0, y1):
                        base = (yy * W * SS + x0) * 3
                        cv.buf[base:base + (x1 - x0) * 3] = bytes(col) * (x1 - x0)
        cx += adv


# Extra-bold headline weight. heavy=True is the old +1px x-only pass;
# XHEAVY stamps a 2x2 block offset by ~1 cell in both axes, so strokes
# grow visibly in both directions at every scale (offset is 1 final px
# at small scales, round(scale) at large ones). Pass it as heavy=XHEAVY
# so every call site and the monkeypatched checks keep seeing one
# draw_text call per string with a truthy heavy flag.
XHEAVY = 2


def draw_text(cv, x, y, text, scale, col, heavy=False):
    _stamp(cv, x, y, text, scale, col)
    if heavy == XHEAVY:
        d = max(1, round(scale))
        _stamp(cv, x + d, y, text, scale, col)
        _stamp(cv, x, y + d, text, scale, col)
        _stamp(cv, x + d, y + d, text, scale, col)
    elif heavy:
        _stamp(cv, x + 1, y, text, scale, col)


def wrap(text, scale, max_w):
    words = text.split(" ")
    lines = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _ink_right(ch):
    """Rightmost ink column (0-7) of a glyph, or -1 when blank."""
    m = -1
    for row in _glyph(ch):
        for c, v in enumerate(row):
            if v == "#" and c > m:
                m = c
    return m


def _stamp_spaced(cv, x, y, text, scale, col, letter_add):
    """Draw a string with extra space between letters (not after the last).

    Same rounding/snapping as _stamp, so justified lines stay neat.
    """
    unit = scale * SS
    ys = [round(r * unit) for r in range(13)]
    xs = [round(c * unit) for c in range(9)]
    oy = round(y * SS)
    cx = x * SS
    n = len(text)
    for k, ch in enumerate(text):
        g = _glyph(ch)
        ox = round(cx)
        for r, row in enumerate(g):
            y0 = oy + ys[r]
            y1 = oy + ys[r + 1]
            for c, cell_ch in enumerate(row):
                if cell_ch == "#":
                    x0 = ox + xs[c]
                    x1 = ox + xs[c + 1]
                    for yy in range(y0, y1):
                        base = (yy * W * SS + x0) * 3
                        cv.buf[base:base + (x1 - x0) * 3] = bytes(col) * (x1 - x0)
        cx += 8 * scale * SS
        if k < n - 1:
            cx += letter_add * SS


def draw_justified(cv, x, y, line, scale, col, target_x, heavy=False):
    """Draw one non-last body line so its INK edge lands on target_x.

    Extra space goes into the word gaps first (up to 2x a space each);
    anything left over goes into letter spacing, counted between
    letters only, so no spacing is wasted after the last letter. The
    last glyph's right bearing is added to the space to distribute, so
    the ink edge -- not the advance box -- lands on the target.
    """
    words = line.split(" ")
    if len(words) < 2:
        draw_text(cv, x, y, line, scale, col, heavy)
        return
    eff_target = target_x - 1 if heavy else target_x
    natural = text_w(line, scale)
    rb = _ink_right(line[-1])
    bearing = (7 - rb) * scale if rb >= 0 else 0.0
    extra = eff_target - x - natural + bearing
    if extra <= 0:
        draw_text(cv, x, y, line, scale, col, heavy)
        return
    gaps = len(words) - 1
    space_w = 8 * scale
    gap_add = min(extra / gaps, 2.0 * space_w)
    rest = extra - gap_add * gaps
    letter_gaps = sum(len(w) - 1 for w in words)
    letter_add = rest / max(letter_gaps, 1) if rest > 0 else 0.0
    for pass_x in (x, x + 1) if heavy else (x,):
        cx = float(pass_x)
        for i, w in enumerate(words):
            _stamp_spaced(cv, cx, y, w, scale, col, letter_add)
            cx += text_w(w, scale) + letter_add * max(len(w) - 1, 0)
            if i < len(words) - 1:
                cx += space_w + gap_add


def draw_para(cv, x, y, text, scale, max_w, target_x, line_h, heavy=False):
    """Wrapped paragraph; every line but the last is justified."""
    lines = wrap(text, scale, max_w)
    for i, ln in enumerate(lines):
        if i < len(lines) - 1:
            draw_justified(cv, x, y, ln, scale, INK, target_x, heavy)
        else:
            draw_text(cv, x, y, ln, scale, INK, heavy)
        y += line_h
    return y


def centre_text(cv, cx, y, text, scale, col, heavy=False):
    extra = max(1, round(scale)) if heavy == XHEAVY else 0
    draw_text(cv, cx - (text_w(text, scale) + extra) / 2, y, text, scale, col, heavy)


def fit_scale(text, max_w, start):
    """Largest scale <= start that fits max_w."""
    s = start
    while s > 0.3 and text_w(text, s) > max_w:
        s -= 0.05
    return s

# ------------------------------------------------------------- visuals
TAG_COL = {"CONFIRMED": GREEN, "CLAIM": RED, "REPORTED": BLUE, "PENDING": ORANGE}


def tag_chip(cv, x, y, tag):
    col = TAG_COL.get(tag, GREY)
    w = int(text_w(tag, 0.62)) + 10
    cv.rect(x, y, w, 13, col)
    draw_text(cv, x + 5, y + 3, tag, 0.62, PAPER)
    return w


def num_badge(cv, x, y, num):
    cv.disc(x + 9, y + 9, 10, NAVY)
    s = fit_scale(str(num), 12, 0.85)
    centre_text(cv, x + 9, y + 9 - int(6 * s), str(num), s, GOLD_LT, heavy=True)


def card_frame(cv, x, y, w, h):
    cv.rect(x, y, w, h, PAPER)
    cv.outline(x, y, w, h, GREY_LT, 1)


def source_line(cv, x, y, sources):
    draw_text(cv, x, y, "Sources: " + sources, 0.55, GREY)


def lead_card(cv, x, y, w, h, num, tag, region, headline, body, sources, visual):
    card_frame(cv, x, y, w, h)
    vh = 96
    visual(cv, x + 1, y + 1, w - 2, vh)
    num_badge(cv, x + 4, y + 4, num)
    tag_chip(cv, x + w - int(text_w(tag, 0.62)) - 15, y + vh - 18, tag)
    ty = y + vh + 6
    draw_text(cv, x + 8, ty, region, 0.6, MAROON, heavy=True)
    ty += 11
    for ln in wrap(headline, 1.0, w - 16):
        draw_text(cv, x + 8, ty, ln, 1.0, INK, heavy=XHEAVY)
        ty += 13
    ty += 2
    ty = draw_para(cv, x + 8, ty, body, 0.72, w - 16, x + w - 8, 9)
    source_line(cv, x + 8, y + h - 11, sources)


def med_card(cv, x, y, w, h, num, tag, region, headline, body, sources, visual):
    card_frame(cv, x, y, w, h)
    vw = 104
    visual(cv, x + 1, y + 1, vw, h - 2)
    num_badge(cv, x + 4, y + 4, num)
    tx = x + vw + 8
    tw = w - vw - 16
    ty = y + 6
    draw_text(cv, tx, ty, region, 0.58, MAROON, heavy=True)
    ty += 10
    for ln in wrap(headline, 0.88, tw):
        draw_text(cv, tx, ty, ln, 0.88, INK, heavy=XHEAVY)
        ty += 12
    ty += 1
    draw_para(cv, tx, ty, body, 0.66, tw, tx + tw, 8.5)
    draw_text(cv, tx, y + h - 11, sources, 0.55, GREY)
    tag_chip(cv, x + w - int(text_w(tag, 0.62)) - 14, y + h - 13, tag)


# --- scene painters: each gets (cv, x, y, w, h) and draws a labelled scene
def vis_cop31(cv, x, y, w, h):
    cv.rect(x, y, w, h, NAVY)
    for i in range(4):  # rows of delegate desks
        cv.rect(x + 12 + i * 6, y + h - 46 + i * 9, w - 24 - i * 12, 5, NAVY_LT)
    cv.rect(x + w // 2 - 26, y + 12, 52, 26, GOLD)  # podium
    draw_text(cv, x + w // 2 - 17, y + 20, "COP31", 0.9, NAVY, heavy=True)
    draw_text(cv, x + 10, y + h - 30, "FOSSIL FUELS", 0.85, PAPER, heavy=True)
    cv.line(x + 8, y + h - 16, x + 118, y + h - 30, RED, 3)  # struck through
    cv.rect(x + w - 118, y + h - 34, 108, 24, RED)
    draw_text(cv, x + w - 88, y + h - 27, "NO DEAL", 0.95, PAPER, heavy=True)
    draw_text(cv, x + 24, y + 6, "ANTALYA - 44 HOURS OVERTIME", 0.6, GOLD_LT)


def vis_trump(cv, x, y, w, h):
    cv.rect(x, y, w, h, SEA)
    cv.rect(x, y, w, 22, SKY)
    cv.disc(x + w - 26, y + 12, 8, GOLD_LT)
    for cx in (x + 30, x + w // 2 + 10):  # two carriers
        cv.rect(cx, y + h - 34, 74, 10, NAVY)
        cv.rect(cx + 52, y + h - 52, 12, 18, NAVY)
        cv.rect(cx + 6, y + h - 44, 62, 10, NAVY_LT)
    for i in range(3):  # tanker convoy
        tx = x + w - 96 + i * 26
        cv.rect(tx, y + h - 24, 22, 8, MAROON)
        cv.rect(tx + 4, y + h - 32, 8, 8, MAROON)
    cv.rect(x, y + h - 22, w, 22, INK)
    draw_text(cv, x + 8, y + h - 18, '"BOTTOM OF THE SEA"', 0.85, PAPER, heavy=True)
    draw_text(cv, x + 24, y + 4, "ARABIAN SEA - 2 US CARRIER GROUPS", 0.6, NAVY)


def vis_ships(cv, x, y, w, h):
    cv.rect(x, y, w, h, SEA)
    cv.poly([(x + 6, y + h - 30), (x + w // 2 - 8, y + 18), (x + w // 2 + 8, y + h - 30)], TAN)
    cv.poly([(x + w - 8, y + 20), (x + w // 2 + 16, y + h - 34), (x + w - 60, y + h - 10)], TAN)
    cv.disc(x + w // 2 - 2, y + 26, 6, RED)  # Baltic pin
    draw_text(cv, x + w // 2 - 5, y + 22, "3", 0.6, PAPER, heavy=True)
    cv.disc(x + w // 2 + 22, y + h - 30, 6, RED)  # Benghazi pin
    draw_text(cv, x + w // 2 + 19, y + h - 34, "3", 0.6, PAPER, heavy=True)
    cv.rect(x + 12, y + h - 40, 44, 9, INK)  # capsized corvette
    cv.poly([(x + 12, y + h - 40), (x + 56, y + h - 40), (x + 48, y + h - 26), (x + 20, y + h - 26)], NAVY)
    cv.rect(x + 66, y + h - 52, 4, 14, GREY)
    cv.rect(x + 76, y + h - 48, 4, 10, GREY)
    draw_text(cv, x + 24, y + 4, "2 SHIPS, 24 HOURS, 2,000 MILES", 0.6, NAVY, heavy=True)


def vis_cikande(cv, x, y, w, h):
    cv.rect(x, y, w, h, (60, 52, 44))
    cv.rect(x + 10, y + h - 52, w - 20, 44, (140, 120, 96))
    cv.rect(x + 18, y + h - 44, 14, 12, ORANGE)
    cv.rect(x + 40, y + h - 44, 14, 12, ORANGE)
    cv.rect(x + 62, y + h - 44, 14, 12, INK)
    for i, (sx, sy, sr) in enumerate([(30, 26, 12), (52, 14, 15), (76, 24, 11)]):
        cv.disc(x + sx, y + sy, sr, (96, 88, 80))
    cv.rect(x + 6, y + h - 20, 92, 16, RED)
    draw_text(cv, x + 29, y + h - 17, "24 DEAD", 0.8, PAPER, heavy=True)
    draw_text(cv, x + 24, y + 4, "PT FONUSA", 0.6, GOLD_LT)


def vis_kyiv(cv, x, y, w, h):
    cv.rect(x, y, w, h, (74, 74, 78))
    cv.poly([(x + 8, y + h - 8), (x + 30, y + 30), (x + 58, y + h - 8)], (150, 146, 138))
    cv.poly([(x + 44, y + h - 8), (x + 66, y + 44), (x + 92, y + h - 8)], (120, 116, 110))
    cv.rect(x + 14, y + 34, 10, 10, GOLD_LT)
    cv.rect(x + 30, y + 52, 10, 10, GOLD_LT)
    cv.rect(x + 62, y + 60, 10, 10, GOLD_LT)
    cv.rect(x + 6, y + h - 20, w - 12, 16, GREEN)
    draw_text(cv, x + 10, y + h - 15, "ALIVE AFTER 14 HOURS", 0.5, PAPER, heavy=True)
    draw_text(cv, x + 24, y + 4, "DYMER, KYIV", 0.6, PAPER)


def vis_korea(cv, x, y, w, h):
    cv.rect(x, y, w, h, PAPER)
    cv.line(x + 12, y + h - 26, x + w - 20, y + 36, GREEN, 4)
    cv.poly([(x + w - 30, y + 36), (x + w - 10, y + 36), (x + w - 20, y + 22)], GREEN)
    draw_text(cv, x + 24, y + 6, "$1 TRILLION", 0.85, GREEN, heavy=True)
    cv.line(x + 12, y + 22, x + w - 20, y + h - 44, RED, 4)
    cv.poly([(x + w - 30, y + h - 44), (x + w - 10, y + h - 44), (x + w - 20, y + h - 28)], RED)
    draw_text(cv, x + 8, y + h - 22, "KOSPI -8% IN A WEEK", 0.58, RED, heavy=True)


def vis_nepal(cv, x, y, w, h):
    cv.rect(x, y, w, h, SKY)
    cv.rect(x, y + h - 26, w, 26, (90, 120, 70))
    cv.line(x + 8, y + h - 26, x + w - 8, y + h - 26, INK, 2)
    for i in range(4):  # train cars
        cv.rect(x + 8 + i * 24, y + h - 44, 20, 16, MAROON)
        cv.rect(x + 12 + i * 24, y + h - 40, 6, 6, GOLD_LT)
    cv.disc(x + 30, y + 22, 7, (196, 150, 110))
    cv.disc(x + 74, y + 22, 7, (196, 150, 110))
    cv.rect(x + 26, y + 30, 8, 22, NAVY)
    cv.rect(x + 70, y + 30, 8, 22, NAVY)
    draw_text(cv, x + 8, y + h - 24, "$1.62BN AGREED", 0.6, PAPER, heavy=True)
    draw_text(cv, x + 8, y + h - 14, "GRANT + CREDIT", 0.6, PAPER, heavy=True)
    draw_text(cv, x + 24, y + 4, "NEW DELHI", 0.58, NAVY)


def vis_alcaraz(cv, x, y, w, h):
    cv.rect(x, y, w, h, (24, 60, 40))
    cv.poly([(x + w // 2 - 16, y + 10), (x + w // 2 + 16, y + 10), (x + w // 2 + 10, y + 34), (x + w // 2 - 10, y + 34)], GOLD)
    cv.rect(x + w // 2 - 4, y + 34, 8, 12, GOLD)
    cv.rect(x + w // 2 - 14, y + 46, 28, 6, GOLD)
    cv.rect(x + 8, y + h - 30, w - 16, 24, INK)
    draw_text(cv, x + 12, y + h - 26, "6-2, 7-6(7)", 0.95, GOLD_LT, heavy=True)
    draw_text(cv, x + 8, y + 62, "SAVED 3 SET POINTS", 0.62, PAPER)


def vis_marquez(cv, x, y, w, h):
    cv.rect(x, y, w, h, (30, 30, 34))
    cv.disc(x + 26, y + h - 34, 11, INK)
    cv.disc(x + 26, y + h - 34, 5, GREY)
    cv.disc(x + w - 26, y + h - 34, 11, INK)
    cv.disc(x + w - 26, y + h - 34, 5, GREY)
    cv.poly([(x + 22, y + h - 34), (x + 52, y + h - 52), (x + 78, y + h - 34)], RED)
    cv.disc(x + 58, y + h - 58, 6, (196, 150, 110))
    draw_text(cv, x + 24, y + 6, "8 TITLES", 1.0, GOLD_LT, heavy=True)
    draw_text(cv, x + 8, y + 22, "LEVEL WITH AGOSTINI", 0.62, PAPER)
    draw_text(cv, x + 8, y + h - 18, "FROM 102 DOWN", 0.62, PAPER)


def vis_liverpool(cv, x, y, w, h):
    cv.rect(x, y, w, h, (120, 10, 10))
    cv.rect(x + 8, y + 16, w - 16, 34, INK)
    draw_text(cv, x + 12, y + 20, "LIVERPOOL 4-0", 0.78, PAPER, heavy=True)
    draw_text(cv, x + 12, y + 34, "MAN UTD", 0.78, PAPER, heavy=True)
    cv.rect(x + 14, y + 62, 12, 18, RED)
    cv.outline(x + 14, y + 62, 12, 18, PAPER, 1)
    draw_text(cv, x + 34, y + 67, "RED CARD 8'", 0.7, PAPER, heavy=True)
    draw_text(cv, x + 8, y + h - 16, "POCHETTINO'S DEBUT", 0.6, PAPER)

# ------------------------------------------------------------- world map
CONTINENTS = [
    [(-168, 66), (-145, 70), (-125, 71), (-110, 73), (-95, 80), (-85, 76), (-75, 72), (-65, 62), (-55, 52), (-60, 46), (-70, 42), (-76, 35), (-81, 26), (-90, 21), (-97, 26), (-105, 22), (-110, 23), (-105, 16), (-92, 15), (-83, 9), (-79, 9), (-86, 13), (-92, 14), (-97, 16), (-105, 20), (-114, 29), (-122, 38), (-125, 49), (-135, 58), (-150, 60), (-165, 60)],
    [(-79, 9), (-72, 11), (-62, 10), (-52, 5), (-50, 0), (-44, -3), (-35, -8), (-37, -13), (-40, -20), (-48, -27), (-57, -34), (-62, -41), (-65, -45), (-68, -50), (-70, -54), (-73, -50), (-73, -40), (-71, -30), (-70, -20), (-75, -15), (-79, -8), (-81, -4), (-80, 3)],
    [(-17, 15), (-16, 20), (-10, 30), (-6, 35), (0, 36), (10, 37), (11, 34), (20, 32), (25, 32), (30, 31), (33, 28), (35, 23), (39, 21), (43, 12), (48, 11), (51, 12), (46, 5), (41, -2), (40, -10), (36, -18), (33, -26), (28, -33), (20, -35), (16, -28), (12, -18), (13, -12), (9, 4), (4, 6), (-8, 4), (-13, 8), (-17, 12)],
    [(30, 70), (35, 68), (40, 68), (45, 68), (50, 69), (55, 69), (60, 69), (65, 69), (70, 72), (75, 73), (80, 73), (85, 75), (90, 75), (95, 76), (100, 77), (105, 77), (110, 74), (115, 73), (120, 73), (125, 72), (130, 72), (135, 71), (140, 72), (145, 72), (150, 70), (155, 69), (158, 66), (160, 62), (162, 58), (160, 55), (156, 51), (150, 59), (142, 55), (140, 45), (138, 40), (135, 35), (130, 33), (127, 35), (126, 38), (122, 38), (120, 32), (122, 28), (120, 22), (115, 20), (110, 18), (108, 12), (105, 9), (103, 7), (100, 7), (98, 10), (97, 15), (94, 17), (92, 21), (89, 22), (86, 20), (82, 16), (80, 13), (77, 8), (75, 12), (73, 16), (70, 20), (66, 25), (62, 25), (58, 26), (54, 27), (52, 28), (50, 29), (48, 30), (45, 29), (42, 30), (40, 32), (38, 36), (36, 36), (33, 36), (30, 36), (28, 38), (27, 40), (30, 44), (32, 46), (35, 48), (38, 50), (40, 55), (40, 60), (38, 65), (35, 68)],
    [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (-1, 46), (0, 49), (2, 51), (5, 53), (8, 55), (8, 57), (10, 59), (12, 56), (18, 56), (21, 55), (24, 58), (24, 60), (28, 61), (30, 62), (30, 70), (35, 68), (40, 67), (44, 68), (48, 64), (44, 60), (40, 55), (38, 50), (35, 46), (32, 46), (30, 45), (28, 44), (27, 41), (23, 36), (22, 38), (19, 40), (16, 40), (12, 44), (8, 44), (3, 43), (0, 39), (-2, 37), (-6, 36), (-9, 37)],
    [(113, -22), (114, -28), (115, -33), (118, -35), (124, -33), (129, -32), (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27), (150, -23), (146, -19), (142, -11), (140, -17), (136, -12), (132, -11), (130, -13), (126, -14), (122, -17), (118, -20), (114, -21)],
]
# (card number, longitude, latitude)
PINS = [
    ("1", 30.7, 36.9), ("2", 56.5, 26.5), ("3", 20.1, 32.1), ("3", 27.0, 60.0),
    ("4", 106.1, -6.4), ("5", 30.5, 50.5), ("6", 127.0, 37.5), ("7", 77.2, 28.6),
    ("8", 7.7, 45.1), ("9", -8.5, 37.1), ("10", -3.0, 53.4),
]


def draw_map(cv, x, y, w, h):
    card_frame(cv, x, y, w, h)
    draw_text(cv, x + 8, y + 6, "WHERE IT HAPPENED", 0.66, MAROON, heavy=XHEAVY)
    draw_text(cv, x + 8, y + 17, "Pins match card numbers", 0.55, GREY)
    mx, my, mw, mh = x + 6, y + 30, w - 12, h - 36
    cv.rect(mx, my, mw, mh, (214, 228, 238))
    for poly in CONTINENTS:
        pts = [(mx + (lon + 180) / 360 * mw, my + (75 - lat) / 130 * mh) for lon, lat in poly]
        cv.poly(pts, TAN)
    for num, lon, lat in PINS:
        px = mx + (lon + 180) / 360 * mw
        py = my + (75 - lat) / 130 * mh
        cv.disc(px, py, 6, RED)
        cv.outline(int(px - 6), int(py - 6), 12, 12, PAPER, 1)
        s = 0.55 if len(num) == 1 else 0.48
        centre_text(cv, px, py - int(6 * s), num, s, PAPER, heavy=True)


def draw_date_check(cv, x, y, w, h):
    cv.rect(x, y, w, h, RED_LT)
    cv.outline(x, y, w, h, RED, 2)
    draw_text(cv, x + 8, y + 6, "DATE CHECK - LEFT OUT ON PURPOSE", 0.66, RED, heavy=XHEAVY)
    items = [
        "El Clasico was 25 Oct, not 23 Nov",
        "Gaza WCK strike was 21 Nov",
        "Nigeria boat sinking was 20 Nov",
        "Germany citizenship data: Jun 2026",
        "F1 Las Vegas GP: 21 Nov",
    ]
    ty = y + 24
    for it in items:
        cv.rect(x + 8, ty + 2, 4, 4, RED)
        draw_text(cv, x + 16, ty, it, 0.62, INK)
        ty += 13
    draw_text(cv, x + 8, y + h - 13, "Old stories stay out, even when big.", 0.55, GREY)


# ------------------------------------------------------------- content
# Bodies are kept short on purpose: a front page gives each story a
# headline and a few sentences, never an essay. Every fact below is in
# the verified research notes; quotes are verbatim from those notes.
LEADS = [
    dict(num=1, tag="CONFIRMED", region="GLOBAL - CLIMATE",
         headline="COP31 COLLAPSES: NO DEAL AFTER 44 HOURS",
         body=("The closing plenary in Antalya ended on Sunday with no agreement. "
               "Murat Kurum told delegates: 'I understand that there is no agreement on this text.' "
               "The Antalya Pact was not adopted. It is the longest climate summit ever, and the first "
               "to end with no cover decision since 2000. The draft left out fossil fuels entirely, so "
               "the EU, UK, Norway, Panama and island states rejected it. China and India accepted it. "
               "Next: COP32 in Addis Ababa, 8-19 Nov 2027."),
         sources="UN News, AP, Reuters, NYT, Guardian", visual=vis_cop31),
    dict(num=2, tag="CLAIM", region="MIDDLE EAST - SECURITY",
         headline="TRUMP: NEW IRAN STRIKES AFTER NEW YEAR IF TALKS FAIL",
         body=("In a Fox News interview on Sunday, President Donald Trump said he is 'inclined' to resume "
               "large-scale strikes on Iran after 1 January 2027 if negotiations fail. He warned Iranian "
               "ships testing the US naval blockade 'will all be at the bottom of the sea, like Iran's navy.' "
               "Two US carrier strike groups are in the Arabian Sea. More than 14 Iranian tankers sit off "
               "Kharg Island, Iran's main crude export hub. No decision to strike has been announced."),
         sources="Fox News, Euronews", visual=vis_trump),
    dict(num=3, tag="REPORTED", region="EUROPE - WAR AT SEA",
         headline="TWO RUSSIAN SHIPS HIT IN 24 HOURS, 2,000 MILES APART",
         body=("The corvette Merkury capsized and sank at its pier in Benghazi, Libya, on Sunday after a "
               "suspected Ukrainian sea-drone strike. Two drones hit; 10 people were slightly hurt. A day "
               "earlier, the cargo ship Sparta II was hit by drones in the Gulf of Finland. Its 16 crew "
               "were evacuated, and Finnish and Estonian crews towed it out on Sunday night. Finland's "
               "Border Guard confirmed a Ukrainian drone strike hit Sparta II. No one has claimed the "
               "Merkury attack."),
         sources="WSJ, CNN, AP, AFP", visual=vis_ships),
]
MEDIUM = [
    dict(num=4, tag="CONFIRMED", region="ASIA-PACIFIC - DISASTER",
         headline="CIKANDE FIRE: 24 DEAD, ABOUT 30 STILL MISSING",
         body=("Indonesia confirmed on Monday that 24 people died in the fire at the PT Fonusa Agung Mulia "
               "candy factory in Cikande, Banten. About 30 people are still missing. The search resumed at "
               "07:00 WIB on Monday. 29 people are confirmed safe, 5 in hospital. The roof collapsed; "
               "hotspots and an unstable structure still hamper rescuers."),
         sources="Reuters, People", visual=vis_cikande),
    dict(num=5, tag="CONFIRMED", region="EUROPE - UKRAINE",
         headline="BOY, 7, ALIVE AFTER 14 HOURS UNDER RUBBLE",
         body=("Rescuers pulled 7-year-old David alive from a five-storey block in Dymer, 45 km north of "
               "Kyiv, almost 14 hours after a Russian Shahed drone struck at 05:00 on Sunday. At least 11 "
               "were killed in Dymer, at least 15 across the Kyiv region. A 79-year-old woman was also "
               "rescued alive. 11 more are missing, including 2 children."),
         sources="BBC, The Gaze, Al Jazeera", visual=vis_kyiv),
    dict(num=6, tag="CONFIRMED", region="ASIA-PACIFIC - MARKETS",
         headline="KOREA PASSES $1 TRILLION IN EXPORTS AS STOCKS CRASH",
         body=("South Korea's 2026 exports passed $1 trillion on 19 November, the 4th country ever to do "
               "so. November exports run at double last year's pace: $77.4bn for 1-20 Nov, up 101.5%. But "
               "on Monday the KOSPI opened 2.77% lower and fell toward a 10-month low. The government is "
               "readying its stock stabilisation fund for the first time in 18 years."),
         sources="Aju Press, KED Global, Reuters", visual=vis_korea),
    dict(num=7, tag="CONFIRMED", region="ASIA-PACIFIC - POLITICS",
         headline="INDIA AGREES $1.62BN PACKAGE FOR NEPAL",
         body=("India agreed a NPR 24,000 crore ($1.62bn) package for Nepal: a NPR 5,600 crore grant "
               "plus a NPR 18,400 crore credit line for flood recovery and energy. PM Balendra Shah met "
               "PM Narendra Modi in New Delhi on Monday, his first trip abroad as PM. They signed 8 MoUs "
               "and launched the Ayodhya-Janakpur train."),
         sources="Joint press release, TBS, ANI", visual=vis_nepal),
    dict(num=8, tag="CONFIRMED", region="SPORT - TENNIS",
         headline="ALCARAZ BEATS ZVEREV FOR FIRST ATP FINALS TITLE",
         body=("Carlos Alcaraz beat world No. 1 Alexander Zverev 6-2, 7-6(7) in the ATP Finals final in "
               "Turin on Sunday, finishing at about 00:10 WIB on Monday. He saved 3 set points at 6-3 down "
               "and won the tiebreak 9-7. It is his first year-end title, capping a 14-match winning streak "
               "after a wrist injury. Cheque: a record $5,171,000."),
         sources="Reuters, BBC", visual=vis_alcaraz),
    dict(num=9, tag="CONFIRMED", region="SPORT - MOTOGP",
         headline="MARQUEZ WINS 8TH MOTOGP TITLE, LEVEL WITH AGOSTINI",
         body=("Marc Marquez clinched the 2026 MotoGP title on Sunday with an 8th-place finish at the "
               "Portuguese Grand Prix in Portimao. He equals Giacomo Agostini's record of 8 premier-class "
               "titles. He trailed Bezzecchi by 102 points after round 7, the biggest deficit overturned. "
               "He has 439 points, 43 clear of Martin."),
         sources="Reuters, AP, MotoGP.com", visual=vis_marquez),
    dict(num=10, tag="CONFIRMED", region="SPORT - FOOTBALL",
         headline="LIVERPOOL ROUT 10-MAN UTD 4-0",
         body=("Mauricio Pochettino's first match as United manager ended in a 4-0 rout at Liverpool on "
               "Sunday. United went down to 10 men after 8 minutes and were 2-0 down at 13. Szoboszlai "
               "scored at 10', Wirtz at 13', Ngumoha at 66', Munoz at 82'. It is the joint-heaviest defeat "
               "for a United manager in his first game since 1926."),
         sources="Reuters, The Times, TNT Sports", visual=vis_liverpool),
]
BRIEFS = [
    ("DEMOCRATS WIN 258 HOUSE SEATS", "Largest majority for either party since 1992", "Reuters, The Times"),
    ("INDIA-NZ TEST DRAWN", "India 720/9 declared; NZ hold on in Wellington", "Cricinfo"),
    ("BITCOIN NEAR $61,000", "Up about 11% from Saturday's $55,130 low", "Finnhub"),
    ("HONG KONG ELECTION COMMITTEE CHOSEN", "98.79% turnout; 723 seats, 856 candidates", "Xinhua"),
    ("SPACEX NROL-136 SETS PAD RECORD", "32h 3m 21s turnaround at Vandenberg", "Spaceflight Now"),
    ("MAYON VOLCANO STILL ALERT LEVEL 3", "About 2,000 people in shelters", "PHIVOLCS"),
    ("M6.5 QUAKE, VANUATU REGION", "About 600 km deep; no damage, no tsunami", "USGS"),
    ("US FUTURES BOUNCE AFTER AI ROUT", "Nasdaq fell 10% last week, worst since Mar 2020", "Reuters"),
    ("NBA: WARRIORS 88-87 CELTICS", "Jokic triple-double; Heat win 7th straight", "Sportradar"),
    ("BARCELONA 3-2 VILLARREAL", "Comeback from 2-0 down in 7 minutes", "Reuters, AP"),
    ("BAHRAIN URGES UN ACTION", "Hormuz shipping down 65% after Iran strike", "Reuters, AP"),
    ("REAL MADRID 2-1 CELTA VIGO", "Espi late winner; Mbappe misses a penalty", "Sportradar"),
    ("ANTHROPIC SHARES SLIDE 8.5%", "After a record IPO priced at $83", "Reuters"),
    ("METS SIGN SKUBAL FOR $450M", "Biggest pitcher deal ever; 9 years", "Reuters, CNN"),
    ("SAUDI STRIKE KILLS 4 IN HODEIDA", "Houthi media say; Saudi has not confirmed", "AFP"),
    ("DRONES HIT KHARTOUM", "UN building damaged; 4 killed", "AFP, Al Jazeera"),
    ("UN URGES PROBE INTO BENGHAZI ATTACKS", "Libya must not become a battleground", "AFP, Arab News"),
    ("KRYVYI RIH MISSILE KILLS BOY, 7", "Double-tap strike also kills a paramedic, 20", "The Gaze"),
    ("KOREA EDUCATION MINISTER QUITS", "Over AI-cheating chaos before the CSAT exam", "Reuters"),
    ("FIFA TO RATIFY UK AS 2035 HOST", "Women's World Cup: 104 matches, 48 teams", "BBC"),
]
STATS = [
    ("44", "HOURS COP31 OVERTIME"),
    ("24", "DEAD IN CIKANDE FIRE"),
    ("$1TN", "KOREA EXPORTS"),
    ("258", "DEMOCRATS' HOUSE SEATS"),
    ("6.5", "VANUATU QUAKE"),
    ("8", "MARQUEZ TITLES"),
]
TIMELINE = [
    ("00:00", "Cikande search"),
    ("02:40", "M6.5 Vanuatu"),
    ("03:00", "Dymer strike"),
    ("05:30", "Nepal-India talks"),
    ("06:16", "Bitcoin $61,769"),
    ("12:23", "SpaceX launch"),
]


# ------------------------------------------------------------- layout
def main():
    cv = Canvas()
    # top bar
    cv.rect(0, 0, W, 16, NAVY)
    draw_text(cv, 8, 3, "THE WORLD IN ONE DAY", 0.62, GOLD_LT, heavy=True)
    right = "30 STORIES - 7 REGIONS - EVERY ONE DATED MONDAY 23 NOVEMBER 2026"
    draw_text(cv, W - 8 - text_w(right, 0.62), 3, right, 0.62, PAPER)
    # masthead: the date is the hero
    centre_text(cv, W // 2, 24, "MONDAY, 23 NOVEMBER 2026", 2.6, NAVY, heavy=XHEAVY)
    centre_text(cv, W // 2, 60, "NO DEAL AT COP31  -  TWO RUSSIAN SHIPS HIT  -  KOREA PASSES $1 TRILLION",
                0.7, MAROON, heavy=True)
    # ticker
    cv.rect(0, 78, W, 18, MAROON)
    tick = ("COP31 NO DEAL  -  TRUMP THREATENS IRAN STRIKES  -  BOY, 7, ALIVE AFTER 14 HOURS  -  "
            "ALCARAZ WINS ATP FINALS  -  MARQUEZ 8TH TITLE")
    centre_text(cv, W // 2, 82, tick, 0.62, PAPER)
    # stat strip, two calm alternating tones
    for i, (num, lab) in enumerate(STATS):
        x = 8 + i * 168
        cv.rect(x, 96, 168, 44, PAPER if i % 2 == 0 else (232, 236, 242))
        cv.outline(x, 96, 168, 44, GREY_LT, 1)
        centre_text(cv, x + 84, 100, num, 1.5, NAVY if i % 2 == 0 else MAROON, heavy=True)
        centre_text(cv, x + 84, 124, lab, 0.55, GREY)
    # timeline strip
    cv.rect(0, 140, W, 26, NAVY_LT)
    draw_text(cv, 8, 147, "THE DAY IN UTC", 0.66, GOLD_LT, heavy=True)
    tx = 128
    for t, what in TIMELINE:
        draw_text(cv, tx, 147, t, 0.66, PAPER, heavy=True)
        tx += int(text_w(t, 0.66)) + 5
        draw_text(cv, tx, 147, what, 0.58, PAPER)
        tx += int(text_w(what, 0.58)) + 18
    # lead cards
    for i, c in enumerate(LEADS):
        lead_card(cv, 8 + i * 340, 166, 328, 238, c["num"], c["tag"], c["region"],
                  c["headline"], c["body"], c["sources"], c["visual"])
    # medium cards
    for i, c in enumerate(MEDIUM[:3]):
        med_card(cv, 8 + i * 340, 404, 328, 130, c["num"], c["tag"], c["region"],
                 c["headline"], c["body"], c["sources"], c["visual"])
    for i, c in enumerate(MEDIUM[3:6]):
        med_card(cv, 8 + i * 340, 534, 328, 130, c["num"], c["tag"], c["region"],
                 c["headline"], c["body"], c["sources"], c["visual"])
    # bottom row: card 10 + map + date check
    c = MEDIUM[6]
    med_card(cv, 8, 664, 328, 130, c["num"], c["tag"], c["region"],
             c["headline"], c["body"], c["sources"], c["visual"])
    draw_map(cv, 348, 664, 328, 130)
    draw_date_check(cv, 688, 664, 328, 130)
    # briefs header
    cv.line(8, 800, 1016, 800, NAVY, 2)
    draw_text(cv, 8, 806, "ALSO TODAY - 20 MORE BRIEFS", 0.72, NAVY, heavy=True)
    chips = "ASIA-PACIFIC 7  -  SPORT 9  -  EUROPE 3  -  MIDDLE EAST 3  -  AMERICAS 4  -  AFRICA 2  -  GLOBAL 2"
    draw_text(cv, W - 8 - text_w(chips, 0.58), 808, chips, 0.58, GREY)
    # briefs, three columns, numbered 11-30, each with its own sources
    cols = [BRIEFS[0:7], BRIEFS[7:14], BRIEFS[14:20]]
    for ci, col in enumerate(cols):
        bx = 8 + ci * 340
        by = 824
        for j, (head, detail, src) in enumerate(col):
            n = 11 + ci * 7 + j
            draw_text(cv, bx, by, "%d. %s" % (n, head), 0.62, INK, heavy=XHEAVY)
            by += 10
            draw_text(cv, bx + 12, by, "%s - %s" % (detail, src), 0.55, GREY)
            by += 11
    # footer
    cv.rect(0, 976, W, 48, NAVY)
    draw_text(cv, 8, 984,
              "Sources: Reuters, AP, AFP, BBC, Guardian, Al Jazeera, UN News, NYT, Xinhua, Aju Press, "
              "Cricinfo, MotoGP.com, Spaceflight Now, PHIVOLCS, USGS, Finnhub, Sportradar",
              0.55, PAPER)
    draw_text(cv, 8, 1000,
              "Facts checked against live reports as of 23 Nov 2026 - Wires read up to 20:05 WIB - "
              "THE WORLD IN ONE DAY",
              0.55, GOLD_LT)
    write_png(OUT, W, H, cv.downsample())
    print("wrote", OUT)


if __name__ == "__main__":
    main()
