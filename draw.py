#!/usr/bin/env python3
"""draw.py — renders the news-image-20261123 v3 entry (30 stories, 23 Nov 2026).

Self-written for the make.fun news-image-20261123 bounty. Renders offline with
PIL + real vector fonts (DejaVu Serif Bold headlines, DejaVu Sans body),
supersampled 3x (3072) then downscaled to 1024x1024 with LANCZOS.
All facts come from ~/workspace/makefun/notes/news-image-20261123-research-v3.md
(30 stories, each verified 23 Nov + 2+ sources, with UTC times).
Layout (1024 canvas): masthead -> UTC timeline -> 3 big leads -> 10 medium
cards (2 rows) -> Day in Numbers -> three-column list (17) + world map ->
DATE CHECK band.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

S = 3                 # supersample factor
W = 1024              # final canvas width/height
MARGIN = 14
GAP = 12
CW = W - 2 * MARGIN  # content width = 996

# ---------------------------------------------------------------- colours
PAPER   = (251, 248, 241)   # warm off-white page
INK     = (26, 35, 50)      # near-black navy text
NAVY    = (22, 50, 79)      # masthead band
NAVY_D  = (16, 38, 62)
GOLD    = (217, 164, 65)
RED     = (180, 35, 24)
TEAL    = (14, 124, 123)
GREEN   = (47, 125, 50)
BLUE    = (21, 101, 192)
AMBER   = (150, 100, 0)
GREY    = (90, 90, 90)
LGREY   = (232, 228, 218)   # panel fill
MGREY   = (200, 194, 182)   # hairlines
WHITE   = (255, 255, 255)
SEA     = (178, 208, 226)   # map ocean
LAND    = (226, 214, 188)   # map land
SKY     = (205, 225, 240)

BADGE_FILL = {"CONFIRMED": GREEN, "OFFICIAL": BLUE, "REPORTED": AMBER, "CLAIM": RED}
REGION_FILL = {
    "GLOBAL": (90, 90, 90), "ME": (180, 35, 24), "EUR": (21, 101, 192),
    "AFR": (120, 72, 20), "APAC": (14, 124, 123), "AMER": (90, 60, 140),
}
REGION_LABEL = {"GLOBAL": "GL", "ME": "ME", "EUR": "EU", "AFR": "AF",
                "APAC": "AP", "AMER": "AM"}

# ---------------------------------------------------------------- fonts
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
for _p in (SERIF_B, SANS, SANS_B):
    if not os.path.exists(_p):
        raise SystemExit("MISSING FONT (never fall back silently): " + _p)

_cache = {}
def F(size, bold=False, serif=False):
    """Font at final-px size (scaled by S internally)."""
    key = (size, bold, serif)
    if key not in _cache:
        path = SERIF_B if serif else (SANS_B if bold else SANS)
        _cache[key] = ImageFont.truetype(path, int(round(size * S)))
    return _cache[key]

# ---------------------------------------------------------------- helpers
WARNINGS = []

def s(v):
    return int(round(v * S))

def wrap(text, font, max_w):
    """Word-wrap by measured width. Returns list of lines."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if font.getlength(trial) <= s(max_w):
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def text_w(text, font):
    return font.getlength(text) / S

def draw_lines(dr, x, y, lines, font, fill, lh):
    """Draw lines of text; return y of the line after the last one."""
    for ln in lines:
        dr.text((s(x), s(y)), ln, font=font, fill=fill)
        y += lh
    return y

def rr(dr, x, y, w, h, r, fill=None, outline=None, width=1):
    dr.rounded_rectangle([s(x), s(y), s(x + w), s(y + h)], radius=s(r),
                         fill=fill, outline=outline, width=s(width))

def chip(dr, x, y, text, bg, fg=WHITE, font=None, pad_x=5, h=13):
    """Small rounded chip; returns its width (final px)."""
    font = font or F(9, bold=True)
    tw = text_w(text, font)
    w = tw + 2 * pad_x
    rr(dr, x, y, w, h, 4, fill=bg)
    dr.text((s(x + pad_x), s(y + (h - 9) / 2 - 0.5)), text, font=font, fill=fg)
    return w

def fit_check(name, used, limit):
    if used > limit + 0.5:
        WARNINGS.append("%s overflow: used %.1f > limit %.1f" % (name, used, limit))

# ---------------------------------------------------------------- data
# kind: big | med | list.  utc: "HH:MM".  pin: (lon, lat) or None.
STORIES = [
    dict(n=1, kind="big", utc="15:00", city="Washington, USA", region="AMER",
         field="conflict", badge="OFFICIAL", pin=(-77.0, 38.9),
         headline="US sanctions 25+ Iran shadow banks",
         summary="Trump had said he may resume strikes; Tehran vows to use 'all its tools'.",
         source="REUTERS"),
    dict(n=2, kind="big", utc="~08:00", city="Benghazi, Libya", region="AFR",
         field="conflict", badge="CLAIM", pin=(20.1, 32.1),
         headline="Zelensky: Ukraine sank ship",
         summary="Kyiv says sea drones sank the corvette Merkury; a second ship, Angara, was also hit.",
         source="REUTERS"),
    dict(n=3, kind="big", utc="06:00", city="Brussels, Belgium", region="EUR",
         field="politics", badge="CONFIRMED", pin=(4.35, 50.85),
         headline="Belgium flights grounded",
         summary="Air traffic control joins a national strike; 404 flights cancelled, 50,000+ hit.",
         source="BRUSSELS TIMES"),
    dict(n=4, kind="med", utc="04:00", city="Cikande, Indonesia", region="APAC",
         field="disaster", badge="CONFIRMED", pin=(106.3, -6.2),
         headline="Cikande fire toll rises to 24",
         summary="24 dead confirmed Monday; about 30 missing.",
         source="REUTERS"),
    dict(n=5, kind="med", utc="16:00", city="Dymer, Ukraine", region="EUR",
         field="human", badge="CONFIRMED", pin=(30.3, 50.8),
         headline="Dymer: final toll 11",
         summary="11 dead, 5 in hospital; boy, 7, pulled alive.",
         source="BBC"),
    dict(n=6, kind="med", utc="00:00", city="Seoul, South Korea", region="APAC",
         field="economy", badge="CONFIRMED", pin=(127.0, 37.5),
         headline="KOSPI falls to 10-month low",
         summary="KOSPI at a 10-month low; exports $1tn last week.",
         source="REUTERS"),
    dict(n=7, kind="med", utc="07:05", city="New Delhi, India", region="APAC",
         field="diplomacy", badge="CONFIRMED", pin=(77.2, 28.6),
         headline="India gives Nepal $1.62bn",
         summary="$1.62bn agreed; 8 deals, a new train.",
         source="THE HINDU"),
    dict(n=8, kind="med", utc="13:55", city="Santa Clara, USA", region="AMER",
         field="tech", badge="CONFIRMED", pin=(-121.95, 37.35),
         headline="Nvidia brings back its boss",
         summary="Board reinstates Jensen Huang; shares up 31%.",
         source="REUTERS"),
    dict(n=9, kind="med", utc="10:00", city="Brussels, Belgium", region="EUR",
         field="conflict", badge="CONFIRMED", pin=(4.35, 50.85),
         headline="NATO sends AWACS",
         summary="Emergency meeting after missiles land in Poland.",
         source="REUTERS"),
    dict(n=10, kind="med", utc="15:40", city="Khartoum, Sudan", region="AFR",
         field="conflict", badge="REPORTED", pin=(32.5, 15.6),
         headline="Sudan strikes condemned",
         summary="US, UN call for a truce.",
         source="AFP"),
    dict(n=11, kind="med", utc="14:00", city="Austin, USA", region="AMER",
         field="tech", badge="CONFIRMED", pin=(-97.7, 30.3),
         headline="CrowdStrike buys Zscaler",
         summary="All-stock $44bn deal; 34% premium.",
         source="REUTERS"),
    dict(n=12, kind="med", utc="12:00", city="Madrid, Spain", region="EUR",
         field="law", badge="CONFIRMED", pin=(-3.7, 40.4),
         headline="Puigdemont case closed",
         summary="Top court drops the case after nine years.",
         source="REUTERS"),
    dict(n=13, kind="med", utc="10:43", city="Germany", region="EUR",
         field="law", badge="REPORTED", pin=(10.0, 51.0),
         headline="Bomb threats at schools",
         summary="Emailed Monday; police say not credible.",
         source="REUTERS"),
    # ---- list items: [region chip] [HH:MM] City: sentence. SOURCE
    dict(n=14, kind="list", utc="06:16", city="Global", region="GLOBAL",
         field="economy", badge="CONFIRMED", pin=None,
         line="Bitcoin near $61,000, up 11% from Sat.",
         source="FINNHUB"),
    dict(n=15, kind="list", utc="02:40", city="Vanuatu", region="APAC",
         field="science", badge="OFFICIAL", pin=(172.2, -13.7),
         line="M6.5 quake, 600 km deep; no tsunami, no damage.",
         source="USGS"),
    dict(n=16, kind="list", utc="07:00", city="New York", region="AMER",
         field="economy", badge="CONFIRMED", pin=(-74.0, 40.7),
         line="US futures bounce; Nasdaq\u2019s worst week.",
         source="REUTERS"),
    dict(n=17, kind="list", utc="11:30", city="Zamfara", region="AFR",
         field="disaster", badge="CONFIRMED", pin=(6.1, 12.6),
         line="15 ruling-party supporters killed in crash.",
         source="FRSC"),
    dict(n=18, kind="list", utc="04:00", city="Wellington", region="APAC",
         field="sport", badge="CONFIRMED", pin=(174.8, -41.3),
         line="New Zealand draw with India on Day 5.",
         source="CRICINFO"),
    dict(n=19, kind="list", utc="04:00", city="San Francisco", region="AMER",
         field="sport", badge="CONFIRMED", pin=(-122.4, 37.8),
         line="Warriors edge Celtics 88\u201387.",
         source="SPORTRADAR"),
    dict(n=20, kind="list", utc="05:00", city="Tripoli", region="AFR",
         field="conflict", badge="OFFICIAL", pin=(13.2, 32.9),
         line="UN calls for a probe into the Benghazi ship attacks.",
         source="AFP"),
    dict(n=21, kind="list", utc="13:00", city="Zurich", region="EUR",
         field="sport", badge="OFFICIAL", pin=(8.5, 47.4),
         line="FIFA confirms UK as 2035 Women\u2019s World Cup host.",
         source="BBC"),
    dict(n=22, kind="list", utc="04:00", city="Hodeida", region="ME",
         field="conflict", badge="CLAIM", pin=(42.8, 14.8),
         line="Houthi media: Saudi attack killed 4, wounded 18.",
         source="AFP"),
    dict(n=23, kind="list", utc="08:00", city="Prague", region="EUR",
         field="politics", badge="CONFIRMED", pin=(14.4, 50.1),
         line="Czechs, Hungarians reject EU budget.",
         source="REUTERS"),
    dict(n=24, kind="list", utc="21:24", city="Pyongyang", region="APAC",
         field="diplomacy", badge="REPORTED", pin=(125.75, 39.03),
         line="N. Korea may shut Swiss office.",
         source="REUTERS"),
    dict(n=25, kind="list", utc="14:00", city="Damascus", region="ME",
         field="diplomacy", badge="REPORTED", pin=(36.3, 33.5),
         line="US weighs training Syrian forces.",
         source="REUTERS"),
    dict(n=26, kind="list", utc="09:00", city="London", region="EUR",
         field="health", badge="OFFICIAL", pin=(-0.1, 51.5),
         line="NHS starts AI trial in breast cancer screening.",
         source="NHS"),
    dict(n=27, kind="list", utc="10:00", city="Mid-Atlantic", region="GLOBAL",
         field="science", badge="CONFIRMED", pin=(-20.0, 0.0),
         line="Sunken coral atoll filmed.",
         source="SOI"),
    dict(n=28, kind="list", utc="11:00", city="Brussels", region="EUR",
         field="energy", badge="OFFICIAL", pin=(4.35, 50.85),
         line="EU: efficiency saved \u20ac120bn in gas, oil imports.",
         source="BBC"),
    dict(n=29, kind="list", utc="12:00", city="Dushanbe", region="APAC",
         field="law", badge="CONFIRMED", pin=(68.8, 38.6),
         line="Tajikistan quits the ICC, fourth country to leave.",
         source="BBC"),
    dict(n=30, kind="list", utc="10:00", city="Jakarta", region="APAC",
         field="politics", badge="REPORTED", pin=(106.8, -6.2),
         line="Prabowo to name VP candidates.",
         source="BUSINESSWORLD"),
]

LEFT_OUT = [
    ("Gaza aid-van strike, 3 killed", "21 Nov"),
    ("F1 Las Vegas GP, Verstappen won", "21 Nov"),
    ("BepiColombo enters Mercury orbit", "21 Nov"),
    ("Sparta II hit in the Baltic, crew evacuated", "21 Nov"),
    ("COP31 climate talks collapse, no deal", "22 Nov"),
    ("Delta flights delayed, 1,000+ flights", "22 Nov"),
    ("Alcaraz wins ATP Finals", "22 Nov"),
    ("Liverpool 4-0 Man Utd", "22 Nov"),
]

TIMELINE = [
    ("00:00", "KOSPI opens \u22122.77%"),
    ("02:40", "Vanuatu quake M6.5"),
    ("04:00", "Cikande toll confirmed"),
    ("06:00", "Belgium flights halted"),
    ("07:05", "Nepal deal announced"),
    ("10:43", "Schools threatened"),
    ("13:55", "Nvidia boss reinstated"),
    ("15:00", "US sanctions Iran"),
    ("21:24", "N. Korea warns Swiss"),
]

# counts computed from the data (cannot mismatch the body)
N_STORIES = len(STORIES)
REGIONS = sorted({st["region"] for st in STORIES if st["region"] != "SPORT"})
N_REGIONS = len(REGIONS)
FIELDS = sorted({st["field"] for st in STORIES})
N_FIELDS = len(FIELDS)

# ---------------------------------------------------------------- illustrations
# Each scene draws a simple flat picture (few shapes, high contrast) inside
# the given box (final-px coordinates). Scenes are drawn illustrations, not
# photographs, and each depicts the reported fact with a label.

def scene_belgium(dr, x, y, w, h):
    rr(dr, x, y, w, h, 4, fill=SKY)
    # tarmac strip
    dr.rectangle([s(x), s(y + h * 0.72), s(x + w), s(y + h)], fill=(90, 90, 96))
    dr.rectangle([s(x), s(y + h * 0.72), s(x + w), s(y + h * 0.75)], fill=WHITE)
    # grounded plane (white silhouette, nose right)
    px, py = x + w * 0.30, y + h * 0.48
    dr.polygon([(s(px - w * 0.22), s(py)), (s(px + w * 0.20), s(py - 6)),
                (s(px + w * 0.26), s(py)), (s(px + w * 0.20), s(py + 6))],
               fill=WHITE)
    dr.polygon([(s(px - w * 0.02), s(py - 4)), (s(px + w * 0.06), s(py - h * 0.22)),
                (s(px + w * 0.10), s(py - 4))], fill=WHITE)
    dr.polygon([(s(px - w * 0.20), s(py + 2)), (s(px - w * 0.14), s(py - h * 0.14)),
                (s(px - w * 0.10), s(py + 2))], fill=WHITE)
    # red prohibition circle + slash over the plane
    cx, cy = x + w * 0.50, y + h * 0.45
    r = h * 0.34
    dr.ellipse([s(cx - r), s(cy - r), s(cx + r), s(cy + r)], outline=RED, width=s(4))
    dr.line([s(cx - r * 0.72), s(cy + r * 0.72), s(cx + r * 0.72), s(cy - r * 0.72)],
            fill=RED, width=s(4))

def scene_trump(dr, x, y, w, h):
    rr(dr, x, y, w, h, 4, fill=NAVY_D)
    # bank building (white on navy): pediment, 3 columns, steps
    cx = x + w * 0.50
    dr.polygon([(s(cx - w * 0.19), s(y + h * 0.30)), (s(cx), s(y + h * 0.06)),
                (s(cx + w * 0.19), s(y + h * 0.30))], fill=WHITE)
    dr.rectangle([s(cx - w * 0.21), s(y + h * 0.30), s(cx + w * 0.21), s(y + h * 0.36)],
                 fill=WHITE)
    for i in range(3):
        colx = cx - w * 0.12 + i * w * 0.12
        dr.rectangle([s(colx - 4), s(y + h * 0.36), s(colx + 4), s(y + h * 0.76)],
                     fill=WHITE)
    dr.rectangle([s(cx - w * 0.23), s(y + h * 0.76), s(cx + w * 0.23), s(y + h * 0.82)],
                 fill=WHITE)
    dr.rectangle([s(cx - w * 0.25), s(y + h * 0.82), s(cx + w * 0.25), s(y + h * 0.88)],
                 fill=WHITE)
    # red prohibition circle + slash over the bank (sanctions = blocked)
    ccx, ccy = cx, y + h * 0.48
    r = h * 0.44
    dr.ellipse([s(ccx - r), s(ccy - r), s(ccx + r), s(ccy + r)], outline=RED, width=s(4))
    dr.line([s(ccx - r * 0.72), s(ccy + r * 0.72), s(ccx + r * 0.72), s(ccy - r * 0.72)],
            fill=RED, width=s(4))

def scene_ships(dr, x, y, w, h):
    rr(dr, x, y, w, h, 4, fill=SKY)
    # left: capsized corvette (tilted hull, half under water)
    dr.rectangle([s(x), s(y + h * 0.55), s(x + w * 0.5), s(y + h)], fill=(44, 110, 168))
    dr.polygon([(s(x + 10), s(y + h * 0.42)), (s(x + w * 0.42), s(y + h * 0.58)),
                (s(x + w * 0.38), s(y + h * 0.72)), (s(x + 16), s(y + h * 0.60))],
               fill=(120, 125, 130))
    dr.rectangle([s(x + 8), s(y + h * 0.55), s(x + w * 0.5), s(y + h * 0.58)],
                 fill=WHITE)
    # right: cargo ship on fire
    dr.rectangle([s(x + w * 0.52), s(y + h * 0.55), s(x + w), s(y + h)], fill=(44, 110, 168))
    dr.rectangle([s(x + w * 0.58), s(y + h * 0.52), s(x + w - 12), s(y + h * 0.68)],
                 fill=(60, 60, 66))
    dr.rectangle([s(x + w * 0.72), s(y + h * 0.40), s(x + w * 0.80), s(y + h * 0.52)],
                 fill=(90, 90, 96))
    for i, (dx, dy, r, c) in enumerate(((0, 0, 9, (230, 120, 40)), (8, -8, 7, (240, 180, 60)),
                                        (16, -2, 6, (220, 80, 30)))):
        dr.ellipse([s(x + w * 0.76 + dx - r), s(y + h * 0.34 + dy - r),
                    s(x + w * 0.76 + dx + r), s(y + h * 0.34 + dy + r)], fill=c)
    dr.ellipse([s(x + w * 0.70), s(y + h * 0.14), s(x + w * 0.78), s(y + h * 0.24)],
               fill=(150, 150, 150))
    dr.ellipse([s(x + w * 0.78), s(y + h * 0.08), s(x + w * 0.88), s(y + h * 0.20)],
               fill=(180, 180, 180))

def scene_fire(dr, x, y, w, h):
    rr(dr, x, y, w, h, 4, fill=(60, 58, 54))
    # smoke plume (kept inside the picture: PIL does not clip)
    for (dx, dy, r) in ((0, 0, 8), (12, -6, 9), (24, -10, 8), (36, -14, 7)):
        dr.ellipse([s(x + w * 0.50 + dx - r), s(y + h * 0.28 + dy),
                    s(x + w * 0.50 + dx + r), s(y + h * 0.28 + dy + 2 * r)],
                   fill=(150, 148, 144))
    # factory building
    dr.rectangle([s(x + 12), s(y + h * 0.42), s(x + w - 12), s(y + h)], fill=(198, 84, 44))
    for i in range(3):
        dr.polygon([(s(x + 12 + i * (w - 24) / 3), s(y + h * 0.42)),
                    (s(x + 12 + (i + 0.5) * (w - 24) / 3), s(y + h * 0.30)),
                    (s(x + 12 + (i + 1) * (w - 24) / 3), s(y + h * 0.42))],
                   fill=(160, 60, 30))
    for i in range(4):
        dr.rectangle([s(x + 22 + i * (w - 44) / 4), s(y + h * 0.55),
                      s(x + 22 + (i + 0.6) * (w - 44) / 4), s(y + h * 0.70)],
                     fill=(255, 220, 120))
    # big 24 badge (scaled to picture height so it fits medium cards too)
    _bd = h * 0.45
    dr.ellipse([s(x + w * 0.70), s(y + h * 0.55),
                s(x + w * 0.70 + _bd), s(y + h * 0.55 + _bd)], fill=RED)
    dr.text((s(x + w * 0.70 + _bd * 0.14), s(y + h * 0.55 + _bd * 0.18)), "24",
            font=F(max(11, int(h * 0.30)), bold=True), fill=WHITE)

def scene_dymer(dr, x, y, w, h):
    rr(dr, x, y, w, h, 4, fill=(90, 88, 84))
    # collapsed slabs (tilted grey blocks)
    dr.polygon([(s(x + 10), s(y + h * 0.30)), (s(x + w * 0.45), s(y + h * 0.22)),
                (s(x + w * 0.52), s(y + h * 0.55)), (s(x + 16), s(y + h * 0.62))],
               fill=(150, 148, 144))
    dr.polygon([(s(x + w * 0.40), s(y + h * 0.55)), (s(x + w * 0.85), s(y + h * 0.45)),
                (s(x + w * 0.95), s(y + h * 0.80)), (s(x + w * 0.50), s(y + h * 0.88))],
               fill=(120, 118, 114))
    dr.rectangle([s(x + w * 0.55), s(y + h * 0.30), s(x + w * 0.62), s(y + h * 0.48)],
                 fill=(90, 88, 84))
    # rescuers carrying a child on a stretcher
    dr.line([s(x + w * 0.30), s(y + h * 0.86), s(x + w * 0.70), s(y + h * 0.86)],
            fill=(255, 200, 60), width=s(4))
    for cx in (x + w * 0.32, x + w * 0.68):
        dr.ellipse([s(cx - 6), s(y + h * 0.70), s(cx + 6), s(y + h * 0.82)], fill=(255, 200, 60))
        dr.rectangle([s(cx - 2), s(y + h * 0.82), s(cx + 2), s(y + h * 0.96)], fill=(255, 200, 60))
    dr.ellipse([s(x + w * 0.50 - 6), s(y + h * 0.78), s(x + w * 0.50 + 6), s(y + h * 0.86)],
               fill=(255, 220, 150))
    # 14 HOURS tag (top, clear of the number badge and status badge)
    rr(dr, x + w * 0.30, y + 6, 66, 15, 3, fill=WHITE)
    dr.text((s(x + w * 0.30 + 5), s(y + 8.5)), "14 HOURS", font=F(10, bold=True), fill=RED)

def scene_korea(dr, x, y, w, h):
    rr(dr, x, y, w, h, 4, fill=WHITE)
    # left: green up arrow $1 TRILLION
    dr.polygon([(s(x + w * 0.16), s(y + h * 0.58)), (s(x + w * 0.16), s(y + h * 0.38)),
                (s(x + w * 0.10), s(y + h * 0.38)), (s(x + w * 0.22), s(y + h * 0.18)),
                (s(x + w * 0.34), s(y + h * 0.38)), (s(x + w * 0.28), s(y + h * 0.38)),
                (s(x + w * 0.28), s(y + h * 0.58))], fill=GREEN)
    dr.text((s(x + w * 0.06), s(y + h * 0.64)), "$1 TRILLION",
            font=F(11, bold=True), fill=GREEN)
    # right: red down arrow KOSPI DOWN
    dr.polygon([(s(x + w * 0.66), s(y + h * 0.26)), (s(x + w * 0.66), s(y + h * 0.44)),
                (s(x + w * 0.60), s(y + h * 0.44)), (s(x + w * 0.72), s(y + h * 0.58)),
                (s(x + w * 0.84), s(y + h * 0.44)), (s(x + w * 0.78), s(y + h * 0.44)),
                (s(x + w * 0.78), s(y + h * 0.26))], fill=RED)
    dr.text((s(x + w * 0.58), s(y + h * 0.64)), "KOSPI DOWN",
            font=F(11, bold=True), fill=RED)

def scene_nepal(dr, x, y, w, h):
    rr(dr, x, y, w, h, 4, fill=SKY)
    # mountains
    dr.polygon([(s(x), s(y + h)), (s(x + w * 0.25), s(y + h * 0.25)),
                (s(x + w * 0.50), s(y + h))], fill=(120, 130, 150))
    dr.polygon([(s(x + w * 0.18), s(y + h * 0.38)), (s(x + w * 0.25), s(y + h * 0.25)),
                (s(x + w * 0.32), s(y + h * 0.38))], fill=WHITE)
    dr.polygon([(s(x + w * 0.45), s(y + h)), (s(x + w * 0.70), s(y + h * 0.35)),
                (s(x + w * 0.95), s(y + h))], fill=(100, 112, 135))
    # two figures shaking hands
    for cx, c in ((x + w * 0.30, NAVY), (x + w * 0.42, RED)):
        dr.ellipse([s(cx - 7), s(y + h * 0.52), s(cx + 7), s(y + h * 0.66)], fill=c)
        dr.rectangle([s(cx - 5), s(y + h * 0.66), s(cx + 5), s(y + h * 0.86)], fill=c)
    dr.line([s(x + w * 0.35), s(y + h * 0.74), s(x + w * 0.40), s(y + h * 0.74)],
            fill=GOLD, width=s(3))
    # train
    dr.rectangle([s(x + w * 0.55), s(y + h * 0.62), s(x + w - 8), s(y + h * 0.86)],
                 fill=(180, 35, 24))
    for i in range(3):
        dr.rectangle([s(x + w * 0.59 + i * 22), s(y + h * 0.67),
                      s(x + w * 0.59 + i * 22 + 14), s(y + h * 0.76)], fill=WHITE)
    for i in range(3):
        dr.ellipse([s(x + w * 0.60 + i * 26), s(y + h * 0.86),
                    s(x + w * 0.60 + i * 26 + 10), s(y + h * 0.94)], fill=INK)

def scene_crowdstrike(dr, x, y, w, h):
    rr(dr, x, y, w, h, 4, fill=NAVY_D)
    # green shield, centre-left
    cx, cy = x + w * 0.26, y + h * 0.50
    dr.polygon([(s(cx), s(cy - h * 0.34)), (s(cx + w * 0.13), s(cy - h * 0.22)),
                (s(cx + w * 0.13), s(cy + h * 0.08)), (s(cx), s(cy + h * 0.34)),
                (s(cx - w * 0.13), s(cy + h * 0.08)), (s(cx - w * 0.13), s(cy - h * 0.22))],
               fill=GREEN)
    dr.line([s(cx - w * 0.06), s(cy), s(cx - w * 0.01), s(cy + h * 0.10)],
            fill=WHITE, width=s(3))
    dr.line([s(cx - w * 0.01), s(cy + h * 0.10), s(cx + w * 0.07), s(cy - h * 0.12)],
            fill=WHITE, width=s(3))
    # network nodes, right
    for (nx, ny) in ((0.60, 0.28), (0.78, 0.55), (0.60, 0.80)):
        dr.ellipse([s(x + w * nx - 5), s(y + h * ny - 5),
                    s(x + w * nx + 5), s(y + h * ny + 5)], fill=(90, 190, 110))
    dr.line([s(x + w * 0.60), s(y + h * 0.28), s(x + w * 0.78), s(y + h * 0.55)],
            fill=(90, 190, 110), width=s(2))
    dr.line([s(x + w * 0.78), s(y + h * 0.55), s(x + w * 0.60), s(y + h * 0.80)],
            fill=(90, 190, 110), width=s(2))

def scene_khartoum(dr, x, y, w, h):
    rr(dr, x, y, w, h, 4, fill=(232, 214, 180))
    # skyline
    for i, (bw, bh, c) in enumerate(((0.16, 0.45, (120, 120, 125)), (0.20, 0.60, (90, 90, 96)),
                                     (0.14, 0.38, (140, 140, 145)), (0.18, 0.52, (100, 100, 106)),
                                     (0.16, 0.42, (130, 130, 135)))):
        bx = x + 8 + i * (w - 16) * 0.19
        dr.rectangle([s(bx), s(y + h - bh * h - 8), s(bx + bw * w), s(y + h - 8)], fill=c)
    # UN-blue building
    dr.rectangle([s(x + w * 0.60), s(y + h * 0.42), s(x + w * 0.82), s(y + h - 8)],
                 fill=(70, 130, 200))
    dr.text((s(x + w * 0.66), s(y + h * 0.52)), "UN", font=F(13, bold=True), fill=WHITE)
    # drone (quadcopter) top right
    cx, cy = x + w * 0.78, y + h * 0.28
    dr.ellipse([s(cx - 8), s(cy - 5), s(cx + 8), s(cy + 5)], fill=INK)
    for dx, dy in ((-16, -10), (16, -10), (-16, 10), (16, 10)):
        dr.ellipse([s(cx + dx - 7), s(cy + dy - 2), s(cx + dx + 7), s(cy + dy + 2)],
                   fill=GREY)

def scene_nvidia(dr, x, y, w, h):
    rr(dr, x, y, w, h, 4, fill=WHITE)
    # chip
    cx, cy = x + w * 0.30, y + h * 0.50
    for i in range(4):
        dr.line([s(cx - 34), s(cy - 18 + i * 12), s(cx - 44), s(cy - 18 + i * 12)],
                fill=GREEN, width=s(3))
        dr.line([s(cx + 34), s(cy - 18 + i * 12), s(cx + 44), s(cy - 18 + i * 12)],
                fill=GREEN, width=s(3))
    dr.rectangle([s(cx - 34), s(cy - 30), s(cx + 34), s(cy + 30)], fill=(30, 120, 60))
    dr.rectangle([s(cx - 20), s(cy - 16), s(cx + 20), s(cy + 16)], fill=(90, 190, 110))
    dr.text((s(cx - 12), s(cy - 7)), "NV", font=F(13, bold=True), fill=WHITE)
    # up arrow
    dr.polygon([(s(x + w * 0.68), s(y + h * 0.66)), (s(x + w * 0.68), s(y + h * 0.40)),
                (s(x + w * 0.62), s(y + h * 0.40)), (s(x + w * 0.74), s(y + h * 0.20)),
                (s(x + w * 0.86), s(y + h * 0.40)), (s(x + w * 0.80), s(y + h * 0.40)),
                (s(x + w * 0.80), s(y + h * 0.66))], fill=GREEN)
    dr.text((s(x + w * 0.58), s(y + h * 0.70)), "UP 31%", font=F(12, bold=True), fill=GREEN)

def scene_puigdemont(dr, x, y, w, h):
    rr(dr, x, y, w, h, 4, fill=NAVY)
    # courthouse: pediment + 3 columns + steps (white on navy)
    cx = x + w * 0.50
    dr.polygon([(s(cx - w * 0.30), s(y + h * 0.30)), (s(cx), s(y + h * 0.08)),
                (s(cx + w * 0.30), s(y + h * 0.30))], fill=WHITE)
    dr.rectangle([s(cx - w * 0.32), s(y + h * 0.30), s(cx + w * 0.32), s(y + h * 0.36)],
                 fill=WHITE)
    for i in range(3):
        colx = cx - w * 0.22 + i * w * 0.22
        dr.rectangle([s(colx - 5), s(y + h * 0.36), s(colx + 5), s(y + h * 0.78)],
                     fill=WHITE)
    dr.rectangle([s(cx - w * 0.34), s(y + h * 0.78), s(cx + w * 0.34), s(y + h * 0.84)],
                 fill=WHITE)
    dr.rectangle([s(cx - w * 0.38), s(y + h * 0.84), s(cx + w * 0.38), s(y + h * 0.90)],
                 fill=WHITE)

def scene_schools(dr, x, y, w, h):
    rr(dr, x, y, w, h, 4, fill=SKY)
    # schoolhouse, left
    dr.polygon([(s(x + w * 0.12), s(y + h * 0.42)), (s(x + w * 0.30), s(y + h * 0.18)),
                (s(x + w * 0.48), s(y + h * 0.42))], fill=(160, 60, 30))
    dr.rectangle([s(x + w * 0.14), s(y + h * 0.42), s(x + w * 0.46), s(y + h * 0.90)],
                 fill=(198, 84, 44))
    dr.rectangle([s(x + w * 0.26), s(y + h * 0.62), s(x + w * 0.34), s(y + h * 0.90)],
                 fill=(90, 60, 40))
    # yellow warning triangle, right
    tx, ty = x + w * 0.70, y + h * 0.45
    dr.polygon([(s(tx), s(ty - h * 0.30)), (s(tx + w * 0.14), s(ty + h * 0.22)),
                (s(tx - w * 0.14), s(ty + h * 0.22))], fill=(255, 193, 7))
    dr.text((s(tx - 3), s(ty - h * 0.16)), "!", font=F(16, bold=True), fill=INK)


def scene_nato(dr, x, y, w, h):
    rr(dr, x, y, w, h, 4, fill=(0, 51, 102))
    cx, cy = x + w * 0.50, y + h * 0.60
    # compass star (white, 4 points)
    star = [(cx, cy - h * 0.28), (cx + w * 0.04, cy - h * 0.08), (cx + w * 0.16, cy),
            (cx + w * 0.04, cy + h * 0.08), (cx, cy + h * 0.28),
            (cx - w * 0.04, cy + h * 0.08), (cx - w * 0.16, cy),
            (cx - w * 0.04, cy - h * 0.08)]
    dr.polygon([(s(a), s(b)) for a, b in star], fill=WHITE)
    dr.ellipse([s(cx - 4), s(cy - 4), s(cx + 4), s(cy + 4)], fill=(0, 51, 102))
    # AWACS plane (white silhouette) with radar dome, top centre
    px, py = x + w * 0.50, y + h * 0.20
    dr.polygon([(s(px), s(py - 5)), (s(px + 6), s(py + 1)), (s(px + w * 0.28), s(py + 1)),
                (s(px + w * 0.28), s(py + 6)), (s(px + 6), s(py + 6)), (s(px), s(py + 11)),
                (s(px - 6), s(py + 6)), (s(px - w * 0.28), s(py + 6)),
                (s(px - w * 0.28), s(py + 1)), (s(px - 6), s(py + 1))], fill=WHITE)
    dr.ellipse([s(px - 9), s(py - 10), s(px + 9), s(py + 2)], fill=WHITE)


SCENES = {1: scene_trump, 2: scene_ships, 3: scene_belgium, 4: scene_fire,
          5: scene_dymer, 6: scene_korea, 7: scene_nepal, 8: scene_nvidia,
          9: scene_nato, 10: scene_khartoum, 11: scene_crowdstrike,
          12: scene_puigdemont, 13: scene_schools}

# ---------------------------------------------------------------- map
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70),
     (-75, 62), (-60, 55), (-55, 47), (-70, 42), (-75, 35), (-80, 26),
     (-85, 20), (-90, 15), (-95, 18), (-105, 20), (-115, 28), (-125, 40),
     (-125, 50), (-140, 60), (-160, 58)],
    # South America
    [(-80, 10), (-75, 5), (-60, 0), (-50, -5), (-35, -8), (-40, -20),
     (-50, -30), (-60, -38), (-70, -52), (-73, -40), (-72, -20), (-80, -5)],
    # Europe
    [(-10, 36), (-5, 44), (0, 48), (5, 55), (10, 58), (18, 56), (25, 60),
     (30, 62), (28, 55), (20, 45), (15, 40), (10, 38), (0, 36)],
    # Africa
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28),
     (40, 15), (48, 11), (51, 10), (40, 0), (35, -15), (30, -28), (20, -35),
     (15, -30), (12, -18), (8, 0), (0, 5), (-8, 5)],
    # Asia
    [(30, 62), (40, 68), (60, 70), (90, 75), (120, 73), (150, 70), (170, 66),
     (180, 65), (170, 60), (160, 55), (150, 45), (140, 40), (130, 35),
     (127, 33), (120, 25), (110, 20), (105, 10), (100, 8), (95, 15),
     (90, 22), (80, 10), (75, 8), (70, 20), (60, 25), (50, 28), (40, 30),
     (35, 36), (30, 42)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (125, -32), (130, -32), (135, -35),
     (140, -38), (145, -38), (150, -37), (153, -27), (150, -22), (146, -19),
     (142, -15), (142, -11), (137, -12), (132, -12), (130, -13), (126, -14),
     (122, -17), (118, -20)],
]

def project(lon, lat, x, y, w, h):
    px = x + (lon + 180.0) / 360.0 * w
    py = y + (75.0 - lat) / 130.0 * h
    return px, py

def draw_map(dr, x, y, w, h):
    rr(dr, x, y, w, h, 4, fill=SEA)
    for poly in CONTINENTS:
        pts = [project(lon, lat, x + 4, y + 4, w - 8, h - 8) for lon, lat in poly]
        dr.polygon([(s(px), s(py)) for px, py in pts], fill=LAND,
                   outline=(160, 148, 120))
    # numbered pins for the 13 card stories (region colour); coincident pins
    # are fanned out with a leader line so no number is hidden
    placed = []
    for st in STORIES:
        if st["kind"] == "list":
            continue
        for key in ("pin", "pin2"):
            if st.get(key) is None:
                continue
            lon, lat = st[key]
            px, py = project(lon, lat, x + 4, y + 4, w - 8, h - 8)
            ox, oy = px, py
            while any(abs(ox - qx) < 15 and abs(oy - qy) < 15 for qx, qy in placed):
                ox, oy = ox + 16, oy - 12
            if (ox, oy) != (px, py):
                dr.line([s(px), s(py), s(ox), s(oy)], fill=GREY, width=s(1))
            placed.append((ox, oy))
            r = 8
            dr.ellipse([s(ox - r), s(oy - r), s(ox + r), s(oy + r)],
                       fill=REGION_FILL[st["region"]],
                       outline=WHITE, width=s(1.5))
            num = str(st["n"])
            tw = text_w(num, F(9, bold=True))
            dr.text((s(ox - tw / 2), s(oy - 5)), num, font=F(9, bold=True), fill=WHITE)
    # small dots for list stories that have a location (region colour)
    for st in STORIES:
        if st["kind"] != "list" or st.get("pin") is None:
            continue
        lon, lat = st["pin"]
        px, py = project(lon, lat, x + 4, y + 4, w - 8, h - 8)
        dr.ellipse([s(px - 2.5), s(py - 2.5), s(px + 2.5), s(py + 2.5)],
                   fill=REGION_FILL[st["region"]])

# ---------------------------------------------------------------- layout
# (1024 canvas)  masthead 156 -> timeline 40 -> big 190 -> med 150 x2 ->
# numbers 52 -> list+map 172 -> date-check 50.  Gaps 6, top/bottom margins 12/10.
NUMBERS = [("24", "DEAD IN CIKANDE"), ("11", "KILLED IN DYMER"),
           ("404", "FLIGHTS CANCELLED"), ("$1.62BN", "NEPAL PACKAGE"),
           ("31%", "NVIDIA SHARES UP")]
REGION_NAMES = {"GLOBAL": "GLOBAL", "ME": "MIDDLE EAST", "EUR": "EUROPE",
                "AFR": "AFRICA", "APAC": "ASIA-PACIFIC", "AMER": "AMERICAS"}
LEFT_OUT_KEYS = ["gaza", "las vegas", "bepicolombo", "sparta", "cop31",
                 "delta", "verstappen", "alcaraz", "liverpool"]


def fit_serif_size(text, max_w, start):
    """Largest serif-bold size <= start whose width fits max_w (final px)."""
    size = start
    while size > 40:
        if text_w(text, F(size, bold=True, serif=True)) <= max_w:
            return size
        size -= 2
    return size


def draw_masthead(dr, x, y, w, h):
    rr(dr, x, y, w, h, 6, fill=NAVY)
    dr.text((s(x + 16), s(y + 12)), "MONDAY", font=F(24, bold=True, serif=True), fill=GOLD)
    counts = "%d STORIES  \u2022  %d REGIONS  \u2022  %d FIELDS" % (N_STORIES, N_REGIONS, N_FIELDS)
    f_cnt = F(13, bold=True)
    tw = text_w(counts, f_cnt)
    px0 = x + w - 16 - tw - 28
    rr(dr, px0, y + 10, tw + 28, 24, 8, fill=GOLD)
    dr.text((s(px0 + 14), s(y + 22)), counts, font=f_cnt, fill=NAVY, anchor="lm")
    size = fit_serif_size("23 NOVEMBER 2026", w - 32, 100)
    dr.text((s(x + w / 2), s(y + 92)), "23 NOVEMBER 2026",
            font=F(size, bold=True, serif=True), fill=WHITE, anchor="mm")
    dr.text((s(x + w / 2), s(y + 146)), "News of Monday 23 November 2026, any time zone",
            font=F(15), fill=(200, 210, 225), anchor="mm")


def draw_timeline(dr, x, y, w, h):
    rr(dr, x, y, w, h, 4, fill=LGREY)
    mid = y + h / 2 + 4
    dr.line([s(x + 10), s(mid), s(x + w - 10), s(mid)], fill=MGREY, width=s(2))
    for i, (utc, label) in enumerate(TIMELINE):
        mx = x + (i + 0.5) * w / len(TIMELINE)
        f_t, f_l = F(10, bold=True), F(9)
        tw = text_w(utc, f_t)
        dr.text((s(mx - tw / 2), s(y + 4)), utc, font=f_t, fill=NAVY)
        dr.ellipse([s(mx - 4), s(mid - 4), s(mx + 4), s(mid + 4)], fill=NAVY)
        lw = text_w(label, f_l)
        dr.text((s(mx - lw / 2), s(y + h - 13)), label, font=f_l, fill=INK)
        fit_check("timeline label %r" % label, lw, w / len(TIMELINE) - 4)


def _card_frame(dr, x, y, w, h):
    rr(dr, x, y, w, h, 5, fill=WHITE, outline=MGREY, width=1)


def _number_badge(dr, cx, cy, n, r, fsize):
    dr.ellipse([s(cx - r), s(cy - r), s(cx + r), s(cy + r)], fill=WHITE,
               outline=NAVY, width=s(1.5))
    f = F(fsize, bold=True)
    num = str(n)
    tw = text_w(num, f)
    dr.text((s(cx - tw / 2), s(cy - fsize / 2 - 1)), num, font=f, fill=NAVY)


def _status_badge(dr, x, y, badge):
    f = F(8, bold=True)
    tw = text_w(badge, f)
    bw = tw + 12
    rr(dr, x - bw, y, bw, 12, 4, fill=BADGE_FILL[badge])
    dr.text((s(x - bw + 6), s(y + 6)), badge, font=f, fill=WHITE, anchor="lm")
    return bw


def _footer(dr, st, x, y, w, fsize, chip_h):
    cw = chip(dr, x, y, REGION_LABEL[st["region"]], REGION_FILL[st["region"]], h=chip_h)
    f = F(fsize, bold=True)
    city = st["city"]
    footer = "%s \u2022 %s" % (city, st["utc"])
    if text_w(footer, f) + cw + 11 > w:
        city = st["city"].split(",")[0]
        footer = "%s \u2022 %s" % (city, st["utc"])
    dr.text((s(x + cw + 6), s(y + chip_h / 2)), footer, font=f,
            fill=REGION_FILL[st["region"]], anchor="lm")
    fit_check("footer #%d" % st["n"], text_w(footer, f) + cw + 6, w)


def draw_big_card(dr, st, x, y, w, h):
    _card_frame(dr, x, y, w, h)
    SCENES[st["n"]](dr, x + 1, y + 1, w - 2, 78)
    _number_badge(dr, x + 14, y + 14, st["n"], 11, 12)
    _status_badge(dr, x + w - 8, y + 6, st["badge"])
    lines = wrap(st["headline"], F(27, bold=True, serif=True), w - 16)
    fit_check("big #%d headline lines" % st["n"], len(lines), 2)
    draw_lines(dr, x + 8, y + 84, lines, F(27, bold=True, serif=True), INK, 30)
    slines = wrap(st["summary"], F(12), w - 16)
    fit_check("big #%d summary lines" % st["n"], len(slines), 2)
    draw_lines(dr, x + 8, y + 146, slines, F(12), INK, 14)
    _footer(dr, st, x + 8, y + 176, w - 16, 11, 13)


def draw_med_card(dr, st, x, y, w, h):
    _card_frame(dr, x, y, w, h)
    SCENES[st["n"]](dr, x + 1, y + 1, w - 2, 50)
    _number_badge(dr, x + 12, y + 12, st["n"], 9, 10)
    _status_badge(dr, x + w - 7, y + 5, st["badge"])
    lines = wrap(st["headline"], F(21, bold=True, serif=True), w - 14)
    fit_check("med #%d headline lines" % st["n"], len(lines), 2)
    draw_lines(dr, x + 7, y + 56, lines, F(21, bold=True, serif=True), INK, 24)
    slines = wrap(st["summary"], F(12), w - 14)
    fit_check("med #%d summary lines" % st["n"], len(slines), 2)
    draw_lines(dr, x + 7, y + 106, slines, F(12), INK, 14)
    _footer(dr, st, x + 7, y + 136, w - 14, 10, 12)


def draw_numbers(dr, x, y, w, h):
    rr(dr, x, y, w, h, 4, fill=LGREY)
    dr.text((s(x + 10), s(y + 12)), "DAY IN", font=F(11, bold=True), fill=NAVY)
    dr.text((s(x + 10), s(y + 26)), "NUMBERS", font=F(11, bold=True), fill=NAVY)
    col0, colw = x + 120, (w - 130) / len(NUMBERS)
    for i, (num, label) in enumerate(NUMBERS):
        cx = col0 + (i + 0.5) * colw
        f_n = F(26, bold=True, serif=True)
        tw = text_w(num, f_n)
        dr.text((s(cx - tw / 2), s(y + 6)), num, font=f_n, fill=NAVY)
        f_l = F(10, bold=True)
        lw = text_w(label, f_l)
        dr.text((s(cx - lw / 2), s(y + 36)), label, font=f_l, fill=GREY)
        fit_check("numbers label %r" % label, lw, colw - 4)


def draw_list_item(dr, cx, iy, col_w, st):
    cw = chip(dr, cx, iy, REGION_LABEL[st["region"]], REGION_FILL[st["region"]], h=12)
    tf = F(10, bold=True)
    tx = cx + cw + 5
    dr.text((s(tx), s(iy)), st["utc"], font=tf, fill=NAVY)
    tx += text_w(st["utc"], tf) + 5
    f, fb = F(11), F(11, bold=True)
    city = st["city"] + ": "
    city_w = text_w(city, fb)
    avail1 = col_w - (tx - cx) - city_w
    l1, l2, cur = [], [], 0.0
    for wd in st["line"].split():
        ww = text_w(wd + " ", f)
        if cur + ww <= avail1 and not l2:
            l1.append(wd)
            cur += ww
        else:
            l2.append(wd)
    dr.text((s(tx), s(iy)), city, font=fb, fill=INK)
    dr.text((s(tx + city_w), s(iy)), " ".join(l1), font=f, fill=INK)
    l2_text = " ".join(l2)
    src = " " + st["source"]
    dr.text((s(cx), s(iy + 13)), l2_text, font=f, fill=INK)
    sx = cx + text_w(l2_text, f)
    dr.text((s(sx), s(iy + 13)), src, font=F(9, bold=True), fill=GREY)
    used = text_w(l2_text, f) + text_w(src, F(9, bold=True))
    fit_check("list #%d line2" % st["n"], used, col_w)


def draw_list(dr, x, y, w, h):
    dr.text((s(x), s(y)), "THE REST OF THE DAY \u2014 ALL TIMES UTC",
            font=F(11, bold=True), fill=NAVY)
    items = [st for st in STORIES if st["kind"] == "list"]
    n = len(items)
    base, rem = n // 3, n % 3
    sizes = [base + 1 if i < rem else base for i in range(3)]
    col_w, gap = 226, 11
    idx = 0
    for c in range(3):
        cx = x + c * (col_w + gap)
        for j in range(sizes[c]):
            draw_list_item(dr, cx, y + 16 + j * 26, col_w, items[idx])
            idx += 1


def draw_map_panel(dr, x, y, w, h):
    dr.text((s(x), s(y)), "WHERE IT HAPPENED", font=F(11, bold=True), fill=NAVY)
    draw_map(dr, x, y + 16, w, 96)
    from collections import Counter
    counts = Counter(st["region"] for st in STORIES)
    order = sorted(counts, key=lambda r: (-counts[r], r))
    ly = y + 118
    for i, r in enumerate(order):
        lx = x + (i % 2) * (w // 2 + 6)
        ry = ly + (i // 2) * 12
        rr(dr, lx, ry + 1, 9, 9, 2, fill=REGION_FILL[r])
        dr.text((s(lx + 13), s(ry)), "%s %d" % (REGION_NAMES[r], counts[r]),
                font=F(9, bold=True), fill=INK)
    hx = x
    for badge in ("CONFIRMED", "OFFICIAL", "REPORTED", "CLAIM"):
        f = F(8, bold=True)
        tw = text_w(badge, f)
        bw = tw + 12
        rr(dr, hx, y + 158, bw, 12, 4, fill=BADGE_FILL[badge])
        dr.text((s(hx + 6), s(y + 164)), badge, font=f, fill=WHITE, anchor="lm")
        hx += bw + 6


def draw_datecheck(dr, x, y, w, h):
    rr(dr, x, y, w, h, 5, fill=NAVY)
    dr.text((s(x + 14), s(y + 8)),
            "DATE CHECK \u2014 Every story on this page happened or was first reported on Monday 23 November 2026 (UTC).",
            font=F(13, bold=True), fill=WHITE)
    dr.text((s(x + 14), s(y + 26)),
            "Left out (21\u201322 Nov, not on this page): Gaza aid-van strike (21) \u2022 F1 Las Vegas GP (21) \u2022 BepiColombo (21) \u2022 Sparta II (21) \u2022 COP31 (22) \u2022 Delta delays (22) \u2022 Alcaraz wins ATP Finals (22) \u2022 Liverpool 4-0 Utd (22)",
            font=F(9), fill=(200, 210, 225))
    dr.text((s(x + 14), s(y + 40)), "Scenes are drawn illustrations, not photographs.",
            font=F(9), fill=GOLD)


def main():
    # left-out cross-check: no left-out phrase may appear in the body
    body = " ".join(
        (st.get("headline", "") + " " + st.get("summary", "") + " " +
         st.get("line", "") + " " + st["city"] + " " + st["source"])
        for st in STORIES).lower()
    for key in LEFT_OUT_KEYS:
        if key in body:
            WARNINGS.append("LEFT-OUT CONTRADICTION: %r appears in the body" % key)
    img = Image.new("RGB", (W * S, W * S), PAPER)
    dr = ImageDraw.Draw(img)
    x0 = MARGIN
    draw_masthead(dr, x0, 12, CW, 156)
    draw_timeline(dr, x0, 174, CW, 40)
    bigs = [st for st in STORIES if st["kind"] == "big"]
    bw = (CW - 2 * GAP) / 3
    for i, st in enumerate(bigs):
        draw_big_card(dr, st, x0 + i * (bw + GAP), 220, bw, 190)
    meds = [st for st in STORIES if st["kind"] == "med"]
    mw = (CW - 4 * GAP) / 5
    for i, st in enumerate(meds):
        row, col = divmod(i, 5)
        draw_med_card(dr, st, x0 + col * (mw + GAP), 416 + row * 156, mw, 150)
    draw_numbers(dr, x0, 728, CW, 52)
    draw_list(dr, x0, 786, 700, 172)
    draw_map_panel(dr, x0 + 712, 786, 284, 172)
    draw_datecheck(dr, x0, 964, CW, 50)
    out = img.resize((W, W), Image.LANCZOS)
    out.save("entry.png")
    out.resize((300, 300), Image.LANCZOS).save("entry-300.png")
    size = os.path.getsize("entry.png")
    print("stories=%d regions=%d fields=%d" % (N_STORIES, N_REGIONS, N_FIELDS))
    print("entry.png bytes=%d (limit 1048576)" % size)
    if size >= 1048576:
        WARNINGS.append("entry.png too big: %d bytes" % size)
    if WARNINGS:
        print("WARNINGS (%d):" % len(WARNINGS))
        for wmsg in WARNINGS:
            print(" - " + wmsg)
    else:
        print("no warnings")


if __name__ == "__main__":
    main()
