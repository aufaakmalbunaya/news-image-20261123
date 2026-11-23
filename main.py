#!/usr/bin/env python3
"""Monday 23 November 2026 - The World in One Day.

Draws one dense newspaper front page (1024x1024 PNG) that sums up the
world news of Monday 23 November 2026: 46 stories, all of which happened
or were first reported that day, across World, Markets, Technology,
Sport and Culture, with a masthead, a dated lead, illustrated panels
and a sketch world map with pins.

Python 3.13 standard library only. No network, no clock, no random
numbers: two runs write byte-identical files.
"""

import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (250, 246, 236)
INK = (22, 22, 26)
NAVY = (18, 38, 84)
RED = (178, 34, 34)
BLUE = (24, 90, 160)
TEAL = (14, 110, 110)
GOLD = (198, 142, 28)
GREEN = (28, 110, 52)
GREY = (110, 108, 100)
LIGHT = (232, 228, 218)
SKY = (158, 198, 228)
SEA = (52, 110, 158)

# 5x7 letter shapes. Each glyph is seven rows; bit 4 is the left column.
FONT = {
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
    "3": (0x1E, 0x01, 0x01, 0x0E, 0x01, 0x01, 0x1E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x0E, 0x10, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x01, 0x0E),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ",": (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    ":": (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    ";": (0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    "-": (0, 0, 0, 0x0E, 0, 0, 0),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "/": (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    "%": (0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "+": (0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
    "=": (0, 0, 0x1F, 0, 0x1F, 0, 0),
    "?": (0x0E, 0x11, 0x01, 0x06, 0x04, 0, 0x04),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    '"': (0x0A, 0x0A, 0, 0, 0, 0, 0),
    "*": (0, 0x15, 0x0E, 0x1F, 0x0E, 0x15, 0),
    "_": (0, 0, 0, 0, 0, 0, 0x1F),
    "#": (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
    ">": (0x10, 0x08, 0x04, 0x02, 0x04, 0x08, 0x10),
    "<": (0x01, 0x02, 0x04, 0x08, 0x04, 0x02, 0x01),
    "@": (0x0E, 0x11, 0x17, 0x15, 0x16, 0x10, 0x0E),
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c, t=1):
        self.fill(x, y, w, t, c)
        self.fill(x, y + h - t, w, t, c)
        self.fill(x, y, t, h, c)
        self.fill(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=1):
        self.fill(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def ring(self, cx, cy, r, c, t=2):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - t) ** 2 <= d <= r * r:
                    self.set(xx, yy, c)

    def tri(self, ax, ay, bx, by, cx, cy, c):
        # Filled triangle by scanline interpolation.
        ys = sorted([(ax, ay), (bx, by), (cx, cy)], key=lambda p: p[1])
        (x0, y0), (x1, y1), (x2, y2) = ys
        for y in range(y0, y2 + 1):
            if y < y1:
                xa = x0 + (x1 - x0) * (y - y0) / max(1, y1 - y0)
                xb = x0 + (x2 - x0) * (y - y0) / max(1, y2 - y0)
            else:
                xa = x1 + (x2 - x1) * (y - y1) / max(1, y2 - y1)
                xb = x0 + (x2 - x0) * (y - y0) / max(1, y2 - y0)
            lo, hi = sorted([int(xa), int(xb)])
            for x in range(lo, hi + 1):
                self.set(x, y, c)


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(cv, x, y, s, scale, c):
    for ch in s:
        g = FONT.get(ch.upper(), FONT["?"])
        for r in range(7):
            bits = g[r]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    cv.fill(x + col * scale, y + r * scale, scale, scale, c)
        x += 6 * scale
    return x


def wrap_lines(s, width, scale):
    cw = 6 * scale
    per = max(1, width // cw)
    words = s.split(" ")
    lines = []
    cur = ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if len(trial) <= per:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            while len(wd) > per:
                lines.append(wd[:per])
                wd = wd[per:]
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def para(cv, x, y, width, s, scale, c, gap=2):
    lines = wrap_lines(s, width, scale)
    for ln in lines:
        draw_text(cv, x, y, ln, scale, c)
        y += 7 * scale + gap
    return y


def save_png(cv, path):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        start = y * cv.w * 3
        raw += cv.px[start:start + cv.w * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR", ihdr)
    data += chunk(b"IDAT", comp)
    data += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(data)
    return len(data)

# ---- small drawn scenes -------------------------------------------------
# Each scene draws inside a box (x, y, w, h) with flat vector shapes.

def scene_globe(cv, x, y, w, h):
    cv.fill(x, y, w, h, SKY)
    r = min(w, h) // 2 - 2
    cx, cy = x + w // 2, y + h // 2 + 2
    cv.disc(cx, cy, r, SEA)
    cv.fill(cx - r + 2, cy - 4, r - 2, 5, GREEN)
    cv.fill(cx + 1, cy + 5, r - 2, 4, GREEN)
    cv.fill(cx - 6, cy - r + 2, 8, 4, GREEN)
    cv.disc(x + 5, y + 5, 3, GOLD)
    cv.fill(x, y + h - 5, w, 5, (120, 90, 60))


def scene_flame(cv, x, y, w, h):
    cv.fill(x, y, w, h, (30, 30, 44))
    cv.fill(x + 8, y + h - 22, w - 16, 22, (70, 70, 90))
    cv.tri(x + w // 2 - 11, y + h - 20, x + w // 2 + 11, y + h - 20,
           x + w // 2, y + 12, (230, 120, 30))
    cv.tri(x + w // 2 - 6, y + h - 20, x + w // 2 + 6, y + h - 20,
           x + w // 2, y + 26, (240, 200, 40))
    cv.fill(x + w // 2 - 22, y + h - 34, 44, 8, (40, 40, 56))
    cv.fill(x + w // 2 - 18, y + h - 42, 36, 6, (52, 52, 68))


def scene_ship(cv, x, y, w, h):
    cv.fill(x, y, w, h, SKY)
    cv.fill(x, y + h - 20, w, 20, SEA)
    cv.fill(x + 10, y + h - 34, w - 20, 14, (60, 60, 70))
    cv.fill(x + 22, y + h - 52, 10, 20, (90, 90, 100))
    cv.fill(x + 40, y + h - 46, 8, 14, (90, 90, 100))
    cv.tri(x + w - 18, y + 8, x + w - 6, y + 8, x + w - 12, y + 26, (230, 120, 30))
    cv.disc(x + w - 12, y + 30, 4, (240, 200, 40))
    cv.fill(x + 6, y + h - 16, 12, 3, (255, 255, 255))
    cv.fill(x + w - 20, y + h - 13, 12, 3, (255, 255, 255))


def scene_scales(cv, x, y, w, h):
    cv.fill(x, y, w, h, LIGHT)
    cv.fill(x + w // 2 - 2, y + 10, 4, h - 26, INK)
    cv.fill(x + 8, y + 12, w - 16, 4, INK)
    cv.line(x + 10, y + 16, x + 4, y + 34, INK)
    cv.line(x + w - 10, y + 16, x + w - 4, y + 34, INK)
    cv.tri(x + 2, y + 34, x + 22, y + 34, x + 12, y + 44, GOLD)
    cv.tri(x + w - 22, y + 34, x + w - 2, y + 34, x + w - 12, y + 44, GOLD)
    cv.fill(x + w // 2 - 12, y + h - 12, 24, 6, INK)


def scene_mountain(cv, x, y, w, h):
    cv.fill(x, y, w, h, SKY)
    cv.tri(x + 2, y + h - 8, x + w // 2 - 6, y + h - 8, x + w // 4, y + 12, (90, 110, 140))
    cv.tri(x + w // 3, y + h - 8, x + w - 2, y + h - 8, x + w * 3 // 4, y + 8, (60, 80, 110))
    cv.tri(x + w // 4 - 8, y + 22, x + w // 4 + 8, y + 22, x + w // 4, y + 12, (255, 255, 255))
    cv.fill(x, y + h - 8, w, 8, GREEN)
    cv.disc(x + w - 12, y + 12, 7, GOLD)


def scene_bars(cv, x, y, w, h):
    cv.fill(x, y, w, h, (200, 200, 190))
    for i in range(5):
        cv.fill(x + 6 + i * 10, y + 6, 4, h - 12, INK)
    cv.fill(x + 6, y + 6, w - 12, 4, INK)
    cv.fill(x + 6, y + h - 10, w - 12, 4, INK)
    cv.disc(x + w // 2, y + h // 2, 8, RED)


def scene_car(cv, x, y, w, h):
    cv.fill(x, y, w, h, SKY)
    cv.fill(x, y + h - 14, w, 14, (70, 70, 70))
    cv.fill(x + 8, y + h - 34, w - 16, 16, RED)
    cv.fill(x + 16, y + h - 46, w - 32, 14, (200, 60, 60))
    cv.disc(x + 18, y + h - 14, 7, INK)
    cv.disc(x + w - 18, y + h - 14, 7, INK)
    cv.disc(x + 18, y + h - 14, 3, LIGHT)
    cv.disc(x + w - 18, y + h - 14, 3, LIGHT)
    cv.fill(x + 4, y + 6, 30, 6, (255, 255, 255))
    cv.fill(x + 4, y + 16, 22, 6, (255, 255, 255))


def scene_bat(cv, x, y, w, h):
    cv.fill(x, y, w, h, GREEN)
    cv.fill(x, y + h - 16, w, 16, (170, 140, 90))
    cv.line(x + 10, y + 12, x + w - 22, y + h - 24, (210, 180, 120))
    cv.fill(x + w - 24, y + h - 30, 16, 6, (210, 180, 120))
    cv.disc(x + w - 12, y + 14, 7, RED)
    cv.fill(x + 6, y + h - 8, w - 12, 3, (255, 255, 255))


def scene_ball(cv, x, y, w, h):
    cv.fill(x, y, w, h, SKY)
    cv.fill(x, y + h - 12, w, 12, GREEN)
    cv.disc(x + w // 2, y + h // 2, 12, (255, 255, 255))
    cv.ring(x + w // 2, y + h // 2, 12, INK, 2)
    cv.fill(x + w // 2 - 4, y + h // 2 - 4, 8, 8, INK)
    cv.line(x + w // 2 - 11, y + h // 2, x + w // 2 - 4, y + h // 2, INK)
    cv.line(x + w // 2 + 4, y + h // 2, x + w // 2 + 11, y + h // 2, INK)
    cv.line(x + w // 2, y + h // 2 - 11, x + w // 2, y + h // 2 - 4, INK)
    cv.line(x + w // 2, y + h // 2 + 4, x + w // 2, y + h // 2 + 11, INK)


def scene_film(cv, x, y, w, h):
    cv.fill(x, y, w, h, (30, 30, 40))
    cv.fill(x + 8, y + 10, w - 16, h - 20, (240, 220, 180))
    cv.fill(x + 8, y + 10, 8, h - 20, INK)
    cv.fill(x + w - 16, y + 10, 8, h - 20, INK)
    for i in range(3):
        cv.fill(x + 9, y + 14 + i * 14, 6, 8, LIGHT)
        cv.fill(x + w - 15, y + 14 + i * 14, 6, 8, LIGHT)
    cv.disc(x + w // 2, y + h // 2, 10, RED)
    cv.tri(x + w // 2 - 3, y + h // 2 - 6, x + w // 2 - 3, y + h // 2 + 6,
           x + w // 2 + 6, y + h // 2, LIGHT)


def scene_lion(cv, x, y, w, h):
    cv.fill(x, y, w, h, (235, 210, 150))
    cv.disc(x + w // 2, y + h // 2, 12, (200, 140, 40))
    cv.disc(x + w // 2 - 5, y + h // 2 - 3, 2, INK)
    cv.disc(x + w // 2 + 5, y + h // 2 - 3, 2, INK)
    cv.tri(x + w // 2 - 3, y + h // 2 + 1, x + w // 2 + 3, y + h // 2 + 1,
           x + w // 2, y + h // 2 + 6, INK)
    cv.fill(x + w // 2 - 6, y + h // 2 + 7, 12, 2, INK)


def scene_chart(cv, x, y, w, h):
    cv.fill(x, y, w, h, LIGHT)
    cv.fill(x + 6, y + h - 8, w - 12, 2, INK)
    cv.fill(x + 6, y + 8, 2, h - 16, INK)
    pts = [(6, h - 8), (11, h - 12), (16, h - 10), (21, h - 16), (25, h - 21)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        cv.line(x + ax, y + ay, x + bx, y + by, RED)
    for (px, py) in pts:
        cv.disc(x + px, y + py, 2, RED)


def scene_drone(cv, x, y, w, h):
    cv.fill(x, y, w, h, (40, 44, 60))
    cv.fill(x + w // 2 - 10, y + h // 2 - 6, 20, 12, (180, 180, 190))
    cv.disc(x + 10, y + 12, 5, (220, 220, 220))
    cv.disc(x + w - 10, y + 12, 5, (220, 220, 220))
    cv.disc(x + 10, y + h - 12, 5, (220, 220, 220))
    cv.disc(x + w - 10, y + h - 12, 5, (220, 220, 220))
    cv.line(x + 12, y + 14, x + w // 2 - 8, y + h // 2 - 4, GREY)
    cv.line(x + w - 12, y + 14, x + w // 2 + 8, y + h // 2 - 4, GREY)
    cv.disc(x + w // 2, y + h // 2, 3, RED)


def scene_gavel(cv, x, y, w, h):
    cv.fill(x, y, w, h, LIGHT)
    cv.fill(x + w // 2 - 14, y + 14, 28, 10, (120, 85, 40))
    cv.line(x + w // 2, y + 24, x + w // 2 - 8, y + h - 14, (120, 85, 40))
    cv.fill(x + w // 2 - 16, y + h - 14, 32, 6, (120, 85, 40))
    cv.fill(x + 8, y + 10, 6, h - 20, NAVY)


def scene_crowd(cv, x, y, w, h):
    cv.fill(x, y, w, h, SKY)
    cv.fill(x, y + h - 14, w, 14, (90, 90, 90))
    for i, c in enumerate([RED, BLUE, GOLD, GREEN, TEAL]):
        cx = x + 5 + i * (w - 10) // 4
        cv.disc(cx, y + h - 26, 5, c)
        cv.fill(cx - 5, y + h - 22, 10, 10, c)
    cv.fill(x + 8, y + 8, w - 16, 8, (255, 255, 255))
    cv.fill(x + 14, y + 10, w - 28, 4, RED)


def scene_robot(cv, x, y, w, h):
    cv.fill(x, y, w, h, LIGHT)
    cv.fill(x + w // 2 - 12, y + 12, 24, 18, (150, 160, 170))
    cv.disc(x + w // 2 - 5, y + 21, 2, RED)
    cv.disc(x + w // 2 + 5, y + 21, 2, RED)
    cv.fill(x + w // 2 - 14, y + 32, 28, 16, (120, 130, 145))
    cv.fill(x + w // 2 - 4, y + 6, 8, 6, INK)
    cv.fill(x + 8, y + 34, 6, 12, (150, 160, 170))
    cv.fill(x + w - 14, y + 34, 6, 12, (150, 160, 170))


def scene_boat(cv, x, y, w, h):
    cv.fill(x, y, w, h, SKY)
    cv.fill(x, y + h - 18, w, 18, SEA)
    cv.tri(x + 12, y + h - 18, x + w - 12, y + h - 18, x + w // 2, y + h - 30, (120, 80, 40))
    cv.fill(x + w // 2 - 2, y + 10, 3, h - 40, INK)
    cv.tri(x + w // 2 + 2, y + 10, x + w // 2 + 22, y + 26, x + w // 2 + 2, y + 26, (255, 255, 255))
    cv.fill(x + 6, y + h - 12, 14, 3, (255, 255, 255))


def scene_flag(cv, x, y, w, h):
    cv.fill(x, y, w, h, LIGHT)
    cv.fill(x + 10, y + 8, 3, h - 16, INK)
    cv.fill(x + 13, y + 8, w - 26, 18, RED)
    cv.fill(x + 13, y + 26, w - 26, 6, (255, 255, 255))
    cv.fill(x + w - 16, y + h - 10, 8, 4, GOLD)


def scene_hospital(cv, x, y, w, h):
    cv.fill(x, y, w, h, LIGHT)
    cv.fill(x + 10, y + 14, w - 20, h - 24, (255, 255, 255))
    cv.rect(x + 10, y + 14, w - 20, h - 24, INK, 1)
    cv.fill(x + w // 2 - 3, y + 18, 6, 18, RED)
    cv.fill(x + w // 2 - 9, y + 24, 18, 6, RED)
    cv.fill(x + 14, y + h - 16, 8, 6, BLUE)
    cv.fill(x + w - 22, y + h - 16, 8, 6, BLUE)


def scene_parliament(cv, x, y, w, h):
    cv.fill(x, y, w, h, SKY)
    cv.fill(x + 8, y + h - 16, w - 16, 8, (200, 200, 190))
    cv.tri(x + 8, y + h - 16, x + w - 8, y + h - 16, x + w // 2, y + 10, (210, 190, 150))
    for i in range(4):
        cv.fill(x + 6 + i * (w - 12) // 3, y + h - 32, 5, 16, (255, 255, 255))
    cv.fill(x + w // 2 - 2, y + 16, 4, 10, GOLD)


def scene_anchor(cv, x, y, w, h):
    cv.fill(x, y, w, h, LIGHT)
    cv.ring(x + w // 2, y + 12, 5, INK, 2)
    cv.fill(x + w // 2 - 2, y + 16, 4, h - 28, INK)
    cv.fill(x + 10, y + 22, w - 20, 4, INK)
    cv.line(x + 10, y + 22, x + 16, y + h - 10, INK)
    cv.line(x + w - 10, y + 22, x + w - 16, y + h - 10, INK)
    cv.fill(x + 8, y + h - 12, w - 16, 4, INK)


SCENES = {
    "globe": scene_globe, "flame": scene_flame, "ship": scene_ship,
    "scales": scene_scales, "mountain": scene_mountain, "bars": scene_bars,
    "car": scene_car, "bat": scene_bat, "ball": scene_ball,
    "film": scene_film, "lion": scene_lion, "chart": scene_chart,
    "drone": scene_drone, "gavel": scene_gavel, "crowd": scene_crowd,
    "robot": scene_robot, "boat": scene_boat, "flag": scene_flag,
    "hospital": scene_hospital, "parliament": scene_parliament,
    "anchor": scene_anchor,
}

# ---- the day's stories ---------------------------------------------------
# (section, kicker, headline, one-line summary, art, accent)
# Every story happened or was first reported on Monday 23 November 2026.
STORIES = [
    ("WORLD", "CLIMATE", "COP31 COLLAPSES IN ANTALYA",
     "Final draft drops the words fossil fuels. EU refuses to sign.",
     "globe", RED),
    ("WORLD", "GULF", "WAR IN THE GULF WIDENS",
     "Iran-US war engulfs Saudi Arabia and Bahrain. Two hurt in Bahrain.",
     "flame", RED),
    ("WORLD", "UKRAINE", "DRONE HITS KYIV FLATS",
     "At least 14 missing after Russian drone strike. Three missiles hit Friday.",
     "drone", NAVY),
    ("MARKETS", "STOCKS", "WALL ST IN AI SELL-OFF",
     "S and P 500 down 3.7 percent Friday, worst week in 18 months.",
     "chart", RED),
    ("WORLD", "BALTIC", "RUSSIAN SHIP STILL BURNING",
     "Cargo ship on fire off Finland after attack. Crew safe, fire rages on.",
     "ship", NAVY),
    ("WORLD", "LIBYA", "ATTACK ON SHIP IN BENGHAZI",
     "10 port workers wounded in assault on Russian ship. UN urges probe.",
     "anchor", NAVY),
    ("WORLD", "JUSTICE", "ICJ: MYANMAR GENOCIDE",
     "World court rules Myanmar committed genocide against the Rohingya.",
     "scales", NAVY),
    ("WORLD", "DIPLOMACY", "NEPAL PM MEETS MODI",
     "Balendra Shah on state visit to India. Bilateral talks in New Delhi.",
     "mountain", TEAL),
    ("WORLD", "EDUCATION", "MINISTER QUITS OVER AI CHEATS",
     "South Korea education minister resigns after AI exam-cheating scandal.",
     "robot", NAVY),
    ("WORLD", "PROTEST", "LISBON MARCHES ON COSTS",
     "Thousands march as living costs fuel anger across Portugal.",
     "crowd", TEAL),
    ("WORLD", "UNITED NATIONS", "TALKS ON KILLER ROBOTS GO ON",
     "UN nations agree to keep negotiating lethal autonomous weapons.",
     "flag", NAVY),
    ("WORLD", "MEXICO", "EL CHAPO ISIDRO CAUGHT",
     "Mexico captures FBI most-wanted cartel boss. 11 dead in Sinaloa fights.",
     "bars", RED),
    ("WORLD", "KOREA", "KIM: SECURITY, NOT SUPREMACY",
     "North Korea leader says his country seeks security, not supremacy.",
     "parliament", NAVY),
    ("WORLD", "AFRICA", "24 KILLED IN SOUTH SUDAN",
     "Fresh violence kills 24 civilians, officials say.",
     "crowd", RED),
    ("WORLD", "HEALTH", "WHO PLEADS FOR PEACE IN CONGO",
     "Chief appeals for calm in Ebola-hit DR Congo area.",
     "hospital", TEAL),
    ("WORLD", "BRAZIL", "BOLSONARO STABLE IN ICU",
     "Brazil ex-leader stable in intensive care, doctors say.",
     "flag", NAVY),
    ("WORLD", "ISRAEL", "ISRAEL TALKS FAIL",
     "Netanyahu-Eisenkot parties end talks with no deal on a government.",
     "gavel", NAVY),
    ("WORLD", "MIGRATION", "BOAT CAPSIZES OFF SENEGAL",
     "At least four dead, dozens missing after migrant boat sinks.",
     "boat", TEAL),
    ("WORLD", "ASEAN", "MYANMAR CALLS ASEAN UNFAIR",
     "Army-backed government rejects ASEAN decision as unfair.",
     "scales", NAVY),
    ("WORLD", "NIGERIA", "35 KILLED IN NIGERIA REVENGE",
     "35 Fulanis killed in revenge attacks, officials say.",
     "crowd", RED),
    ("WORLD", "SUDAN", "DRONES HIT KHARTOUM HOMES",
     "Drone strikes hit homes and a UN building in Sudan capital.",
     "drone", NAVY),
    ("WORLD", "USA", "9 SHOT AT CALIFORNIA CONCERT",
     "Gunfire at a central California concert injures nine, one critical.",
     "bars", RED),
    ("MARKETS", "CHIPS", "NVIDIA DOWN 14 PERCENT",
     "Chip giant leads the AI rout on Friday. Worst week in over a year.",
     "chart", RED),
    ("MARKETS", "FEAR", "FEAR GAUGE SPIKES TO 35.9",
     "VIX jumps as stocks fall. 10-year yield at 4.936 percent.",
     "chart", RED),
    ("MARKETS", "INDIA", "FOREIGN CASH FLOODS INDIA",
     "Investors put Rs1.22 lakh crore into Indian equities in November.",
     "flag", GREEN),
    ("MARKETS", "METALS", "GOLD AND SILVER TUMBLE",
     "Precious metals post steep weekly declines.",
     "scales", GOLD),
    ("MARKETS", "ENERGY", "PETROL RELIEF AT THE PUMP",
     "US gasoline falls from 4.15 to 3.72 dollars a gallon. WTI down 20 percent.",
     "car", GREEN),
    ("MARKETS", "CHIPS", "CHIP DIVERSION NETWORK EXPOSED",
     "Fresh details tie Alice Huang to a secret network sending AI chips to China.",
     "bars", RED),
    ("TECH", "ROBOTS", "WAYMO OFF THE FREEWAYS",
     "Driverless taxis suspended from all US freeways.",
     "robot", BLUE),
    ("TECH", "DEFENCE", "UK TO BUILD UKRAINE DRONES",
     "Britain to produce Ukrainian drones under a new deal.",
     "drone", BLUE),
    ("TECH", "CLIMATE TECH", "JAPAN BETS ON US RECYCLING",
     "Decarbonisation agency invests in a US metal recycling start-up.",
     "globe", TEAL),
    ("TECH", "HERITAGE", "OKINAWA CASTLE TO REOPEN",
     "Restored castle reopens with extensive fire safety measures.",
     "parliament", TEAL),
    ("TECH", "GAMES", "HELLO KITTY BETS ON GAMES",
     "Sanrio owner bets on games to expand its global reach.",
     "film", BLUE),
    ("SPORT", "CRICKET", "INDIA 720 FOR 9 IN WELLINGTON",
     "Record Test total against New Zealand on day four at the Basin Reserve.",
     "bat", GREEN),
    ("SPORT", "FORMULA 1", "VERSTAPPEN WINS VEGAS THRILLER",
     "35 lead changes in Las Vegas. Norris second, Piastri third.",
     "car", RED),
    ("SPORT", "FOOTBALL", "LIVERPOOL 4 MAN UTD 0",
     "Reds thrash 10-man United at Anfield. Ngumoha scores and sets up Wirtz.",
     "ball", RED),
    ("SPORT", "FOOTBALL", "HULL STUN BRIGHTON 2-0",
     "McBurnie scores twice in stoppage time against 10-man Brighton.",
     "crowd", BLUE),
    ("SPORT", "FOOTBALL", "LEEDS THRASH CHELSEA 4-1",
     "First Leeds win at Stamford Bridge since 1999. Okafor scores twice.",
     "crowd", BLUE),
    ("SPORT", "SNOOKER", "ANUPAMA KEEPS SNOOKER CROWN",
     "Defends IBSF world women's snooker championship.",
     "bat", GREEN),
    ("SPORT", "CRICKET", "JUREL SEES INDIA CHANCE",
     "Keeper-batter hopeful despite slowing Basin Reserve pitch.",
     "bat", GREEN),
    ("CULTURE", "FILM", "IFFI HOSTS BRICS FILM TABLE",
     "Film roundtable strengthens industry ties at IFFI 2026 in Goa.",
     "film", GOLD),
    ("CULTURE", "MUSIC", "TRIBUTES FOR MOLLY MELDRUM",
     "Human Nature and Jason Donovan lead tributes to the music great.",
     "crowd", GOLD),
    ("CULTURE", "OBITUARY", "PAOLO BULGARI DIES AT 89",
     "Italian jeweller and businessman dies, family says.",
     "gavel", INK),
    ("CULTURE", "ANIMALS", "LION LOOSE IN TURKIYE",
     "Lion on the loose sparks fear among residents.",
     "lion", GOLD),
    ("CULTURE", "POLITICS", "TRUMP HITS OUT AT SCHUMER",
     "President criticises Schumer amid push for new Democrat leadership.",
     "parliament", NAVY),
    ("CULTURE", "POLITICS", "FIRST GEN Z WOMAN IN CONGRESS",
     "Melat Kiros, 29, Democrat socialist, enters US Congress.",
     "flag", BLUE),
]

TICKER = [
    ("S AND P 500", "-3.7%"),
    ("NASDAQ", "-5.3%"),
    ("NVIDIA", "-14%"),
    ("VIX", "35.9"),
    ("10-YEAR", "4.94%"),
    ("WTI NOV", "-20%"),
    ("PETROL", "$3.72"),
]

PINS = [
    ("ANTALYA", 30.7, 36.9), ("HORMUZ", 56.5, 26.6),
    ("KYIV", 30.5, 50.5), ("WELLINGTON", 174.8, -41.3),
    ("LAS VEGAS", -115.1, 36.2), ("LISBON", -9.1, 38.7),
    ("NEW DELHI", 77.2, 28.6), ("SEOUL", 127.0, 37.6),
    ("MEXICO", -99.1, 19.4), ("SENEGAL", -17.4, 14.7),
    ("SUDAN", 32.6, 15.6), ("BRASILIA", -47.9, -15.8),
]


def draw_hero_art(cv, x, y, w, h):
    cv.fill(x, y, w, h, SKY)
    cv.disc(x + w - 60, y + 26, 20, GOLD)
    cv.fill(x, y + h - 26, w, 26, SEA)
    cv.disc(x + w // 2, y + h // 2 + 4, 52, (40, 90, 140))
    cv.fill(x + w // 2 - 40, y + h // 2 - 12, 26, 14, GREEN)
    cv.fill(x + w // 2 + 8, y + h // 2 + 14, 32, 12, GREEN)
    cv.fill(x + w // 2 - 16, y + h // 2 - 34, 20, 10, GREEN)
    for i in range(3):
        sx = x + 30 + i * 26
        cv.fill(sx, y + 12 + i * 8, 18, 9, (255, 255, 255))
        cv.fill(sx + 4, y + 20 + i * 8, 12, 7, (235, 235, 235))
    cv.fill(x, y + h - 26, w, 4, (255, 255, 255))
    draw_text(cv, x + 10, y + h - 22, "ANTALYA, TURKIYE - THE SUMMIT THAT FAILED", 1, (255, 255, 255))


def draw_map(cv, x, y, w, h):
    cv.fill(x, y, w, h, (190, 215, 235))
    cv.rect(x, y, w, h, INK, 1)
    # Rough continents as flat blobs.
    blobs = [
        (30, 12, 150, 32), (190, 14, 90, 26), (300, 10, 130, 32),
        (470, 18, 120, 36), (620, 16, 90, 28), (740, 38, 110, 28),
        (120, 54, 70, 18), (250, 56, 60, 16), (560, 58, 80, 16),
    ]
    for (bx, by, bw, bh) in blobs:
        cv.fill(x + bx, y + by, bw, bh, (120, 170, 110))
    for i, (name, lon, lat) in enumerate(PINS):
        px = x + int((lon + 180) / 360 * w)
        py = y + int((90 - lat) / 180 * h)
        cv.disc(px, py, 5, RED)
        cv.disc(px, py, 2, (255, 255, 255))
        draw_text(cv, px + 7, py - 3, str(i + 1), 1, RED)
    draw_text(cv, x + 8, y + 6, "THE DAY ON THE MAP", 1, INK)


def story_block(cv, x, y, w, story):
    section, kicker, head, sub, art, accent = story
    SCENES[art](cv, x, y, 30, 30)
    cv.rect(x, y, 30, 30, INK, 1)
    tx = x + 36
    tw = w - 36
    draw_text(cv, tx, y, kicker, 1, accent)
    lines = wrap_lines(head, tw, 1)
    yy = y + 8
    for ln in lines[:2]:
        draw_text(cv, tx, yy, ln, 1, INK)
        yy += 8
    sub_lines = wrap_lines(sub, tw, 1)
    if sub_lines:
        line = sub_lines[0]
        if len(line) > 44:
            cut = line[:44]
            if " " in cut:
                cut = cut[:cut.rfind(" ")]
            line = cut
        draw_text(cv, tx, y + 24, line, 1, GREY)
    return 32


def section_head(cv, x, y, w, name, count):
    cv.fill(x, y, w, 16, NAVY)
    draw_text(cv, x + 6, y + 4, name + "  -  " + str(count) + " STORIES", 1, (255, 255, 255))
    return 19


def build():
    cv = Canvas(W, H, PAPER)
    # Masthead.
    title = "THE WORLD TODAY"
    draw_text(cv, (W - text_w(title, 4)) // 2, 8, title, 4, INK)
    cv.hline(16, 48, W - 32, INK, 2)
    # Date band.
    cv.fill(16, 52, W - 32, 36, NAVY)
    date = "MONDAY 23 NOVEMBER 2026"
    draw_text(cv, (W - text_w(date, 3)) // 2, 60, date, 3, (255, 255, 255))
    draw_text(cv, 24, 65, "VOL. 1", 1, (200, 210, 230))
    draw_text(cv, W - 24 - text_w("NO. 327", 1), 65, "NO. 327", 1, (200, 210, 230))
    tag = "CLIMATE TALKS FAIL . GULF WAR WIDENS . MARKETS TUMBLE . VERSTAPPEN WINS IN VEGAS"
    draw_text(cv, (W - text_w(tag, 1)) // 2, 94, tag, 1, RED)
    cv.hline(16, 106, W - 32, INK, 1)

    # Lead story: hero art left, headline under it.
    hero = STORIES[0]
    draw_hero_art(cv, 16, 112, 544, 150)
    cv.rect(16, 112, 544, 150, INK, 2)
    yy = para(cv, 16, 268, 544, hero[2], 2, INK)
    para(cv, 16, yy + 2, 544, hero[3], 1, GREY)

    # Right rail: stories 2 to 4 with 56px art.
    rx = 576
    ry = 112
    for st in STORIES[1:4]:
        SCENES[st[4]](cv, rx, ry, 56, 56)
        cv.rect(rx, ry, 56, 56, INK, 1)
        tx = rx + 64
        draw_text(cv, tx, ry, st[1], 1, st[5])
        yy = para(cv, tx, ry + 9, 1008 - tx, st[2], 2, INK)
        para(cv, tx, yy, 1008 - tx, st[3], 1, GREY)
        ry += 62
    cv.hline(16, 304, W - 32, INK, 1)

    # Markets ticker.
    ty = 310
    bw = (W - 32) // len(TICKER)
    for i, (label, val) in enumerate(TICKER):
        bx = 16 + i * bw
        cv.rect(bx + 2, ty, bw - 4, 32, INK, 1)
        draw_text(cv, bx + 8, ty + 4, label, 1, GREY)
        draw_text(cv, bx + 8, ty + 16, val, 2, RED)
    cv.hline(16, 348, W - 32, INK, 1)

    # Three columns of the remaining 42 stories.
    rest = STORIES[4:]
    cols = [rest[0:14], rest[14:28], rest[28:42]]
    col_x = [16, 352, 688]
    col_w = 320
    for ci, col in enumerate(cols):
        y = 356
        cur_section = None
        for st in col:
            if st[0] != cur_section:
                cur_section = st[0]
                n = sum(1 for s in STORIES if s[0] == cur_section)
                y += section_head(cv, col_x[ci], y, col_w, cur_section, n)
            y += story_block(cv, col_x[ci], y, col_w, st)
        cv.vline(col_x[ci] + col_w + 8, 356, 520, GREY, 1) if ci < 2 else None

    # Map strip.
    draw_map(cv, 16, 884, W - 32, 82)
    # Footer.
    cv.hline(16, 972, W - 32, INK, 2)
    counts = {}
    for s in STORIES:
        counts[s[0]] = counts.get(s[0], 0) + 1
    foot = "46 STORIES . ALL REPORTED MONDAY 23 NOVEMBER 2026 . " + " . ".join(
        k + " " + str(v) for k, v in counts.items())
    draw_text(cv, (W - text_w(foot, 1)) // 2, 980, foot, 1, INK)
    foot2 = "THE WORLD TODAY - ONE DAY, ONE PAGE, THE WHOLE WORLD"
    draw_text(cv, (W - text_w(foot2, 1)) // 2, 996, foot2, 1, GREY)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    cv = build()
    n = save_png(cv, path)
    print("wrote", path, n, "bytes,", len(STORIES), "stories")


if __name__ == "__main__":
    main()
