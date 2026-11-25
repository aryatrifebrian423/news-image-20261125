#!/usr/bin/env python3
"""news-image-20261125: one image summing up Wednesday 25 November 2026.

Pure Python 3.13 standard library (zlib + struct PNG writer, embedded
5x7 bitmap font). No network, no randomness, no time: two runs write
byte-identical PNGs. Run: MAKEFUN_OUTPUT_DIR=out python3 main.py
"""
import os
import struct
import zlib

W, H = 1024, 1024

# --- palette: newsprint cream, ink navy, red accent, gold, category inks
PAPER = (247, 243, 234)
INK = (20, 33, 61)
INK2 = (43, 58, 86)
RED = (193, 18, 31)
GOLD = (201, 162, 39)
WHITE = (255, 255, 255)
GREY = (120, 124, 130)
DARK = (16, 24, 40)
GREEN = (31, 122, 74)
TEAL = (14, 116, 120)
ORANGE = (198, 96, 20)
PURPLE = (104, 74, 158)
BROWN = (122, 84, 48)

CAT = {
    "WAR": RED, "POL": INK2, "MKT": GREEN, "SPORT": ORANGE,
    "TECH": PURPLE, "HEALTH": TEAL, "WORLD": BROWN,
}

# --- 5x7 bitmap font: char -> 7 row bitmasks (bit 4 = leftmost pixel)
F = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ",": (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    ":": (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    ";": (0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04),
    "%": (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    "-": (0, 0, 0, 0x0E, 0, 0, 0),
    "+": (0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
    "/": (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "=": (0, 0, 0x1F, 0, 0x1F, 0, 0),
    "*": (0, 0x04, 0x15, 0x0E, 0x15, 0x04, 0),
    "<": (0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02),
    ">": (0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08),
    "#": (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
}


def text_w(s, sc):
    return len(s) * 6 * sc - sc


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                self.px[i], self.px[i + 1], self.px[i + 2] = c
                i += 3

    def hline(self, x, y, w, c):
        self.rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.rect(x, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=False):
        x, y, d = 0, r, 1 - r
        pts = []
        while x <= y:
            pts += [(cx + x, cy + y), (cx - x, cy + y), (cx + x, cy - y),
                    (cx - x, cy - y), (cx + y, cy + x), (cx - y, cy + x),
                    (cx + y, cy - x), (cx - y, cy - x)]
            if d < 0:
                d += 2 * x + 3
            else:
                d += 2 * (x - y) + 5
                y -= 1
            x += 1
        if fill:
            ys = {}
            for px, py in pts:
                ys.setdefault(py, []).append(px)
            for py, xs in ys.items():
                self.hline(min(xs), py, max(xs) - min(xs) + 1, c)
        else:
            for px, py in pts:
                self.set(px, py, c)

    def tri(self, x0, y0, x1, y1, x2, y2, c):
        self.line(x0, y0, x1, y1, c)
        self.line(x1, y1, x2, y2, c)
        self.line(x2, y2, x0, y0, c)
        # scanline fill
        ys = sorted(set([y0, y1, y2]))
        for y in range(min(ys), max(ys) + 1):
            xs = []
            for (ax, ay, bx, by) in ((x0, y0, x1, y1), (x1, y1, x2, y2),
                                    (x2, y2, x0, y0)):
                if ay == by:
                    continue
                if min(ay, by) <= y < max(ay, by):
                    xs.append(ax + (bx - ax) * (y - ay) / (by - ay))
            if len(xs) >= 2:
                self.hline(int(min(xs)), y, int(max(xs)) - int(min(xs)) + 1, c)

    def text(self, x, y, s, sc, c):
        cx = x
        for ch in s.upper():
            g = F.get(ch, F[" "])
            for r in range(7):
                bits = g[r]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.rect(cx + col * sc, y + r * sc, sc, sc, c)
            cx += 6 * sc
        return cx

    def text_c(self, cx, y, s, sc, c):
        self.text(cx - text_w(s, sc) // 2, y, s, sc, c)

    def png_bytes(self):
        raw = bytearray()
        stride = self.w * 3
        for y in range(self.h):
            raw.append(0)
            raw += self.px[y * stride:(y + 1) * stride]
        comp = zlib.compress(bytes(raw), 9)

        def chunk(typ, data):
            out = struct.pack(">I", len(data)) + typ + data
            return out + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
                + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


# --- tiny pictograms, 14x14, drawn per story category
def icon(cv, x, y, cat):
    c = CAT[cat]
    if cat == "WAR":  # missile: body + nose + fins
        cv.tri(x + 7, y, x + 10, y + 5, x + 4, y + 5, c)
        cv.rect(x + 5, y + 5, 5, 7, c)
        cv.tri(x + 5, y + 12, x + 2, y + 14, x + 5, y + 14, c)
        cv.tri(x + 9, y + 12, x + 12, y + 14, x + 9, y + 14, c)
    elif cat == "POL":  # ballot box + tick
        cv.rect(x + 1, y + 4, 12, 9, c)
        cv.rect(x + 4, y + 1, 6, 3, c)
        cv.line(x + 3, y + 9, x + 6, y + 12, WHITE)
        cv.line(x + 6, y + 12, x + 11, y + 6, WHITE)
    elif cat == "MKT":  # rising bars
        cv.rect(x + 1, y + 9, 3, 5, c)
        cv.rect(x + 6, y + 6, 3, 8, c)
        cv.rect(x + 11, y + 2, 3, 12, c)
        cv.line(x, y + 13, x + 14, y + 13, c)
    elif cat == "SPORT":  # ball
        cv.circle(x + 7, y + 7, 6, c)
        cv.circle(x + 7, y + 7, 2, c, fill=True)
        cv.line(x + 7, y + 1, x + 7, y + 5, c)
        cv.line(x + 7, y + 9, x + 7, y + 13, c)
        cv.line(x + 1, y + 7, x + 5, y + 7, c)
        cv.line(x + 9, y + 7, x + 13, y + 7, c)
    elif cat == "TECH":  # chip
        cv.rect(x + 3, y + 3, 8, 8, c)
        cv.rect(x + 5, y + 5, 4, 4, PAPER)
        for dx in (4, 7, 10):
            cv.vline(x + dx, y, 3, c)
            cv.vline(x + dx, y + 11, 3, c)
            cv.hline(x, y + dx, 3, c)
            cv.hline(x + 11, y + dx, 3, c)
    elif cat == "HEALTH":  # cross
        cv.rect(x + 5, y + 1, 4, 12, c)
        cv.rect(x + 1, y + 5, 12, 4, c)
    else:  # WORLD: globe
        cv.circle(x + 7, y + 7, 6, c)
        cv.hline(x + 1, y + 7, 12, c)
        cv.line(x + 4, y + 2, x + 4, y + 12, c)
        cv.line(x + 10, y + 2, x + 10, y + 12, c)

# --- 52 stories, all first reported on 25 November 2026 (see SOURCES.md).
# Each: (category, headline line 1, headline line 2, data line).
# Headline lines <= 14 chars (scale 2), data line <= 32 chars (scale 1).
STORIES = [
    ("WAR", "RUSSIA CALLS", "SHIP STRIKES", "BALTIC + LIBYA"),
    ("WAR", "ZELENSKY: US", "BLOCKS PAID", "MISSILES PAID FOR"),
    ("WAR", "UKRAINE HIT", "RUSSIAN SHIPS", "FINLAND + BENGHAZI"),
    ("WAR", "NATO JETS", "FOR POLAND", "EARLY-WARNING AIRCRAFT"),
    ("WAR", "3 TANKERS HIT", "IN HORMUZ", "MINES - IRGC NAVY CLAIM"),
    ("WAR", "ISRAEL: IRAN", "BUILDS CHEM", "WEAPONS - KATZ VOWS STOP"),
    ("WAR", "GAZA TOLL", "74,746", "WAFA - UN WARNS ON AID"),
    ("WAR", "700,000+", "TROOPS KILLED", "RUSSIANS DEAD - ANALYSIS"),
    ("WAR", "US ENVOY", "UNSURE ON AID", "AID MAY RUN PAST 2026"),
    ("WAR", "RUSSIA-UKRAINE", "CLASH AT UN", "BLACK SEA SHIPPING ROW"),
    ("MKT", "ASIA STOCKS", "PLUNGE", "KOSPI -5.3% TAIWAN -5.1%"),
    ("MKT", "NIKKEI -2.9%", "MSCI -2.3%", "TARIFF THREATS HIT ASIA"),
    ("MKT", "BITCOIN", "$59,257", "ETHER $1,660 - BOTH -1%"),
    ("MKT", "BRENT $90.97", "-0.5% IN ASIA", "OIL CHOPPY AFTER TUESDAY"),
    ("MKT", "SENSEX -1,484", "NIFTY <25,400", "BANK + METAL SELL-OFF"),
    ("MKT", "TATA STEEL", "RS 32,266 CR", "52.38% OF APL APOLLO"),
    ("MKT", "GERMANY TAX", "EUR 1 TN 2027", "TAX TO HIT EUR 1 TN"),
    ("MKT", "US CORE PCE", "DUE TODAY", "AHEAD OF THANKSGIVING"),
    ("MKT", "NVIDIA -5.9%", "HUANG RETURNS", "AS CEO - RALLY FADES"),
    ("MKT", "US BLACKLISTS", "MEGASPEED", "NVIDIA CHIP DIVERSION"),
    ("POL", "BJP-SAD ALLY", "PUNJAB 2027", "SAD REJOINS NDA - 6 YRS"),
    ("POL", "INDIA AID", "RS 15,000 CR", "TO NEPAL AFTER FLOODS"),
    ("POL", "SPAIN VOTES", "29 NOV", "PP LEADS PSOE IN POLLS"),
    ("POL", "TRUMP PARDONS", "TURKEYS", "FREEDOM + FEATHERS"),
    ("POL", "GIULIANI GETS", "TOP US MEDAL", "MEDAL OF FREEDOM - TRUMP"),
    ("POL", "MODI + MERZ", "TALKS", "INDIA-GERMANY TIES"),
    ("POL", "US + QATAR", "TALKS", "STRATEGIC COOPERATION"),
    ("SPORT", "ENGLAND BEAT", "AUSTRALIA", "2ND T20I - 8 WKTS"),
    ("SPORT", "SOORYAVANSHI", "204 OFF 53", "INDIA A WIN BY 7 WKTS"),
    ("SPORT", "PRIYANSH ARYA", "181 IN T20", "2ND-HIGHEST T20 SCORE"),
    ("SPORT", "MARKRAM 150", "FOR S AFRICA", "RECORD KNOCK"),
    ("SPORT", "MUMBAI BEAT", "ODISHA BY 22", "5TH STRAIGHT SMAT WIN"),
    ("SPORT", "GIANTS BEAT", "MI EMIRATES", "ILT20 BY 6 WICKETS"),
    ("SPORT", "BRENTFORD 4-0", "EVERTON", "PREMIER LEAGUE"),
    ("SPORT", "INDIA WOMEN", "BEAT CHINA 6-2", "FOOTBALL"),
    ("SPORT", "J+K BEAT", "RAILWAYS", "CRICKET BY 4 WICKETS"),
    ("SPORT", "PAKISTAN BEAT", "NEPAL BY 96", "ASIA CUP RISING STARS"),
    ("SPORT", "INDO WOMEN", "BEAT CHINA", "T20I BY 91 RUNS"),
    ("SPORT", "FIFA: 2031 WWC", "TO US-MEXICO", "+ COSTA RICA + JAMAICA"),
    ("SPORT", "LALIGA HIT BY", "CYBERATTACK", "FAN DATA EXPOSED"),
    ("SPORT", "NZ HOLD INDIA", "TO DRAW", "1ST TEST - INDIA 720/9"),
    ("SPORT", "TICKNER OUT", "OF INDIA TEST", "HAMSTRING - NZ PACEMAN"),
    ("HEALTH", "WHO FLEES", "AKWE HOSPITAL", "EBOLA: 5,775 DEAD"),
    ("HEALTH", "IRAN RATIONS", "ELECTRICITY", "GRID HIT BY STRIKES"),
    ("WORLD", "NEPAL QUAKE", "5.6 MAGNITUDE", "KOSHI PROVINCE"),
    ("WORLD", "UAE CRASH", "KILLS 11", "RAS AL KHAIMAH"),
    ("WORLD", "GHANA SUMMIT", "ENDS TODAY", "GERMAN-AFRICAN BUSINESS"),
    ("WORLD", "RFE/RL BACK", "ON SHORTWAVE", "AFGHAN GIRLS SCHOOL"),
    ("WORLD", "266M FACE", "ACUTE HUNGER", "WFP WARNING"),
    ("WORLD", "NEPAL NATIONAL", "GAMES OPEN", "10TH EDITION - 5 SPORTS"),
]

MARKETS = [
    ("KOSPI", "-5.3%"), ("TAIWAN", "-5.1%"), ("NIKKEI", "-2.9%"),
    ("MSCI ASIA", "-2.3%"), ("BITCOIN", "$59,257"), ("BRENT", "$90.97"),
]


def draw_masthead(cv):
    cv.rect(0, 0, W, 84, INK)
    cv.rect(0, 80, W, 4, RED)
    cv.text(16, 12, "THE WORLD IN ONE IMAGE", 1, GOLD)
    cv.text(16, 30, "25 NOVEMBER 2026", 5, WHITE)
    cv.text(16, 66, "WEDNESDAY", 2, GOLD)
    right = "52 STORIES  *  REPORTED TODAY  *  MAKE.FUN"
    cv.text(W - 16 - text_w(right, 1), 14, right, 1, (200, 205, 215))
    cv.text(W - 16 - text_w("ONE DAY. ONE PICTURE.", 2), 44,
            "ONE DAY. ONE PICTURE.", 2, WHITE)


def draw_climax(cv):
    y0, y1 = 84, 316
    cv.rect(0, y0, W, y1 - y0, DARK)
    # scene: night sky, HQ block, flag, warning triangle, network nodes
    sx, sy, sw, sh = 24, 104, 400, 192
    cv.rect(sx, sy, sw, sh, (24, 38, 66))
    cv.rect(sx, sy + 150, sw, 42, (18, 30, 54))
    # HQ block with columns
    cv.rect(sx + 60, sy + 40, 280, 110, (52, 70, 104))
    cv.rect(sx + 60, sy + 30, 280, 10, (70, 92, 130))
    for i in range(6):
        cv.rect(sx + 78 + i * 44, sy + 48, 16, 102, (200, 205, 215))
    cv.rect(sx + 60, sy + 40, 280, 8, (150, 158, 172))
    # flag
    cv.vline(sx + 200, sy + 2, 30, (200, 205, 215))
    cv.rect(sx + 200, sy + 2, 34, 20, RED)
    cv.rect(sx + 200, sy + 2, 34, 3, WHITE)
    cv.rect(sx + 200, sy + 19, 34, 3, WHITE)
    # network nodes + links
    for (nx, ny) in ((sx + 20, sy + 30), (sx + 40, sy + 90),
                     (sx + 370, sy + 40), (sx + 350, sy + 110)):
        cv.circle(nx, ny, 5, GOLD, fill=True)
    cv.line(sx + 20, sy + 30, sx + 60, sy + 60, GOLD)
    cv.line(sx + 370, sy + 40, sx + 340, sy + 60, GOLD)
    cv.line(sx + 40, sy + 90, sx + 60, sy + 110, GOLD)
    # red warning triangle + lightning
    tx, ty = sx + 300, sy + 8
    cv.tri(tx, ty + 64, tx + 34, ty, tx + 68, ty + 64, RED)
    cv.tri(tx + 4, ty + 60, tx + 34, ty + 8, tx + 64, ty + 60, (255, 214, 64))
    cv.text(tx + 27, ty + 22, "!", 3, RED)
    # text side
    x = 460
    cv.text(x, 100, "CYBERATTACK * WASHINGTON", 2, GOLD)
    cv.text(x, 128, "CYBERATTACK", 4, WHITE)
    cv.text(x, 162, "HITS THE CIA", 4, (255, 214, 64))
    cv.text(x, 208, "SPY AGENCY + SPY CHIEF'S OFFICE", 2, WHITE)
    cv.text(x, 228, "CLASSIFIED SYSTEMS BREACHED", 2, WHITE)
    cv.text(x, 248, "CNN REPORTS THE INTRUSION", 2, (200, 205, 215))
    cv.text(x, 268, "FBI DATABASE ATTACK 'SEPARATE'", 2, (200, 205, 215))
    # stat chips
    for i, (big, small) in enumerate((("2", "AGENCIES HIT"),
                                      ("25 NOV", "REPORTED TODAY"))):
        cx0 = 460 + i * 250
        cv.rect(cx0, 292, 230, 16, RED if i == 0 else INK2)
        cv.text(cx0 + 8, 296, big + "  " + small, 1, WHITE)


def draw_markets(cv):
    y0 = 316
    cv.rect(0, y0, W, 68, PAPER)
    cv.rect(0, y0, 4, 68, RED)
    cv.text(16, y0 + 10, "MARKETS PLUNGE", 2, RED)
    x = 220
    for name, val in MARKETS:
        cv.text(x, y0 + 12, name, 1, GREY)
        cv.text(x, y0 + 26, val, 3, RED if val.startswith("-") else INK)
        x += 134
    cv.text(16, y0 + 44, "FRESH US TARIFF THREATS", 1, GREY)


def draw_grid(cv):
    cols, rows = 5, 10
    gx, gy = 8, 388
    pw, ph, gap = 196, 58, 6
    for idx, (cat, l1, l2, data) in enumerate(STORIES):
        r, c = divmod(idx, cols)
        x = gx + c * (pw + gap)
        y = gy + r * (ph + gap)
        cv.rect(x, y, pw, ph, WHITE)
        cv.rect(x, y, pw, 3, CAT[cat])
        cv.rect(x, y, 3, ph, CAT[cat])
        icon(cv, x + 8, y + 8, cat)
        cv.text(x + 26, y + 6, l1, 2, INK)
        cv.text(x + 26, y + 22, l2, 2, INK)
        cv.text(x + 8, y + 42, data, 1, GREY)
        cv.text(x + pw - 8 - text_w(cat, 1), y + 42, cat, 1, CAT[cat])


def build():
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    draw_climax(cv)
    draw_markets(cv)
    draw_grid(cv)
    return cv.png_bytes()


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    data = build()
    with open(os.path.join(outdir, "entry.png"), "wb") as fh:
        fh.write(data)
    print("wrote %d bytes" % len(data))


if __name__ == "__main__":
    main()
