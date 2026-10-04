"""Generates the pixel-art vision images (320x180, scaled 4x) for the vision statements."""
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

W, H, SCALE = 320, 180, 4
OUT = Path(__file__).parent
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def hexc(s):
    return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))


def dither(img, x, y, c1, c2, t):
    """Pixel takes c2 with probability t (ordered Bayer dithering)."""
    img.putpixel((x, y), c2 if t * 16 > BAYER[y % 4][x % 4] + 0.5 else c1)


def vgradient(img, box, c1, c2):
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        t = (y - y0) / max(1, y1 - y0 - 1)
        for x in range(x0, x1):
            dither(img, x, y, c1, c2, t)


def fill_mask(img, mask, c1, c2, tfunc):
    px = mask.load()
    for y in range(H):
        for x in range(W):
            if px[x, y]:
                dither(img, x, y, c1, c2, max(0.0, min(1.0, tfunc(x, y))))


def new_mask():
    m = Image.new("1", (W, H), 0)
    return m, ImageDraw.Draw(m)


def dunes(img, base, amp, freq, phase, c1, c2):
    m, md = new_mask()
    pts = [(x, base + amp * math.sin(x * freq + phase) + amp * 0.5 * math.sin(x * freq * 2.3 + phase))
           for x in range(0, W + 1, 2)]
    md.polygon(pts + [(W, H), (0, H)], fill=1)
    fill_mask(img, m, c1, c2, lambda x, y: (y - base + amp) / 40)


def save(img, name):
    img.resize((W * SCALE, H * SCALE), Image.NEAREST).save(OUT / name)


def wabe_tower(d, cx, base, tiers, faces, window, lit=None):
    """Hexagonal tiered tower in side view: left, front and right face per tier."""
    y = base
    for i, (w, h) in enumerate(tiers):
        x0, x1 = cx - w // 2, cx + w // 2
        q = w // 4
        d.rectangle((x0, y - h, x0 + q, y), fill=faces[0])
        d.rectangle((x0 + q, y - h, x1 - q, y), fill=faces[1])
        d.rectangle((x1 - q, y - h, x1, y), fill=faces[2])
        d.line((x0, y - h, x1, y - h), fill=faces[0])
        for wx in range(x0 + q + 4, x1 - q - 3, 7):
            d.rectangle((wx, y - h + 6, wx + 2, y - h + 11), fill=window)
        y -= h
    top_w = tiers[-1][0]
    d.chord((cx - top_w // 2, y - top_w // 2, cx + top_w // 2, y + top_w // 2), 180, 360, fill=faces[1], outline=faces[0])
    return y


def alchemistin_aschenland():
    sky_top, sky_low = hexc("#4b4a48"), hexc("#9a9893")
    img = Image.new("RGB", (W, H), sky_top)
    d = ImageDraw.Draw(img)
    vgradient(img, (0, 0, W, 130), sky_top, sky_low)
    faces = [hexc("#55534f"), hexc("#3d3c3a"), hexc("#2b2a29")]
    window = hexc("#1e1d1c")
    tiers = [(120, 24), (104, 22), (90, 22), (76, 20), (62, 20)]
    wabe_tower(d, 210, 138, tiers, faces, window)
    # Risse und abgebrochene Kanten
    for x, y0, y1 in [(170, 120, 132), (246, 96, 108), (196, 60, 70)]:
        d.line((x, y0, x + 2, y1), fill=window)

    # Ein einziges warmes Licht – und sein Schein
    lx, ly = 222, 79
    warm, glow = hexc("#ffcf6b"), hexc("#c98a3a")
    for y in range(ly - 9, ly + 10):
        for x in range(lx - 9, lx + 10):
            r = math.hypot(x - lx, y - ly)
            if r < 9:
                dither(img, x, y, img.getpixel((x, y)), glow, (1 - r / 9) * 0.6)
    d.rectangle((lx - 1, ly - 3, lx + 1, ly + 2), fill=warm)

    # Aschedünen
    dunes(img, 136, 4, 0.03, 0.5, hexc("#8a8780"), hexc("#6f6c66"))
    dunes(img, 150, 5, 0.025, 2.0, hexc("#77746e"), hexc("#5a5853"))
    dunes(img, 166, 4, 0.04, 4.0, hexc("#5f5c57"), hexc("#46443f"))

    # Ascheflocken
    rnd = random.Random(7)
    for _ in range(160):
        x, y = rnd.randrange(W), rnd.randrange(H)
        img.putpixel((x, y), hexc("#c4c1ba") if rnd.random() < 0.6 else hexc("#a9a69f"))
    save(img, "c-aschenland-alchemistin.png")


INK, DARK, MID, LIGHT, PAPER = map(hexc, ["#24180f", "#4a3423", "#8a6a48", "#c9a978", "#efe0bd"])
RED, GREEN, BLUE, GOLD = map(hexc, ["#c8432b", "#4f9a4a", "#3a5ba8", "#e2b53e"])


def sepia_sky(img, d, earth, seed=3):
    """Sepia night sky with stars and a hatched Earth (cx, cy, r)."""
    vgradient(img, (0, 0, W, H), INK, DARK)
    rnd = random.Random(seed)
    for _ in range(90):
        img.putpixel((rnd.randrange(W), rnd.randrange(H)), rnd.choice([LIGHT, PAPER, MID]))
    ex, ey, er = earth
    m, md = new_mask()
    md.ellipse((ex - er, ey - er, ex + er, ey + er), fill=1)
    fill_mask(img, m, LIGHT, DARK, lambda x, y: (x - ex + er * 0.3) / er)
    for cx, cy, w, h in [(-8, -8, 9, 6), (4, 6, 7, 8), (-4, 10, 5, 3)]:
        k = er / 22
        d.ellipse((ex + cx * k, ey + cy * k, ex + (cx + w) * k, ey + (cy + h) * k), fill=MID)


def moon_ground(img, d, base):
    m, md = new_mask()
    pts = [(x, base + 4 * math.sin(x / 17) + 2 * math.sin(x / 5)) for x in range(0, W + 1, 2)]
    md.polygon(pts + [(W, H), (0, H)], fill=1)
    fill_mask(img, m, LIGHT, MID, lambda x, y: (y - base + 4) / 40)
    for cx, cy, rx, ry in [(40, base + 26, 14, 3), (290, base + 18, 10, 2), (250, base + 32, 18, 4)]:
        d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=DARK)
        d.arc((cx - rx, cy - ry - 1, cx + rx, cy + ry - 1), 180, 360, fill=PAPER)


def glow(img, d, x0, y0, r, colour, strength=0.6):
    for y in range(max(0, y0 - r), min(H, y0 + r + 1)):
        for x in range(max(0, x0 - r), min(W, x0 + r + 1)):
            dist = math.hypot(x - x0, y - y0)
            if dist < r:
                dither(img, x, y, img.getpixel((x, y)), colour, (1 - dist / r) * strength)


def baron(d, x, y, coat=DARK):
    """Tiny Münchhausen with tricorn; y = feet. Returns the hand position."""
    d.line((x - 1, y - 4, x - 2, y), fill=INK)
    d.line((x + 1, y - 4, x + 2, y), fill=INK)
    d.rectangle((x - 3, y - 12, x + 3, y - 4), fill=coat, outline=INK)
    d.rectangle((x - 2, y - 16, x + 2, y - 13), fill=PAPER)
    d.polygon([(x - 5, y - 17), (x + 5, y - 17), (x, y - 21)], fill=INK)
    return x + 3, y - 11


def selenothek_aussen():
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)
    sepia_sky(img, d, (52, 36, 20))
    moon_ground(img, d, 140)
    d.ellipse((120, 138, 280, 158), fill=DARK)
    d.arc((120, 137, 280, 157), 180, 360, fill=PAPER)
    top = wabe_tower(d, 200, 148, [(120, 24), (104, 22), (90, 22), (76, 20), (62, 18)], [LIGHT, MID, DARK], INK)
    # Tür mit Licht, ein erleuchtetes Fenster
    d.chord((193, 134, 207, 154), 180, 360, fill=GOLD)
    d.rectangle((193, 144, 207, 148), fill=GOLD)
    glow(img, d, 200, 142, 14, GOLD, 0.5)
    glow(img, d, 214, 85, 8, GOLD, 0.6)
    d.rectangle((213, 82, 215, 87), fill=GOLD)
    # Bohnenranken klettern an der Fassade empor
    for x0 in (148, 154):
        for t in range(46):
            img.putpixel((int(x0 + 3 * math.sin(t / 3)), 146 - t), GREEN)
    for y in range(110, 146, 6):
        img.putpixel((150, y), hexc("#7cc46f"))
    # Pigmentflecken vor der Tür
    rnd = random.Random(4)
    for _ in range(26):
        img.putpixel((200 + rnd.randint(-28, 28), 149 + rnd.randint(0, 6)), rnd.choice([RED, BLUE, GOLD, GREEN]))
    baron(d, 182, 150)
    save(img, "m-selenothek-aussen.png")


def selenothek_innen():
    img = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(img)
    lamp = (70, 128)
    spines_sepia = [MID, LIGHT, DARK, hexc("#a8865c")]
    spines_colour = [RED, GREEN, BLUE, GOLD, hexc("#8e3b6e")]
    rnd = random.Random(9)

    def shade(c, depth):
        k = min(0.85, depth * 0.28)
        return tuple(int(a * (1 - k) + b * k) for a, b in zip(c, INK))

    box, depth = (-40, -30, W + 40, H + 30), 0
    while box[2] - box[0] > 6:
        x0, y0, x1, y1 = box
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 - 6 * depth
        sw, sh = (x1 - x0) * 0.46, (y1 - y0) * 0.46
        ix0, iy0, ix1, iy1 = cx - sw / 2, cy - sh / 2, cx + sw / 2, cy + sh / 2
        d.polygon([(x0, y0), (ix0, iy0), (ix0, iy1), (x0, y1)], fill=shade(MID, depth))
        d.polygon([(x1, y0), (ix1, iy0), (ix1, iy1), (x1, y1)], fill=shade(DARK, depth))
        d.polygon([(x0, y0), (x1, y0), (ix1, iy0), (ix0, iy0)], fill=shade(INK, depth))
        d.polygon([(x0, y1), (x1, y1), (ix1, iy1), (ix0, iy1)], fill=shade(DARK, depth + 0.5))
        # Regale mit Buchrücken auf beiden Seitenwänden
        for side in (0, 1):
            ox, ix = (x0, ix0) if side == 0 else (x1, ix1)
            steps = max(2, int(abs(ix - ox) / 3))
            for s in range(steps):
                t = s / steps
                x = ox + (ix - ox) * t
                top_y, bot_y = y0 + (iy0 - y0) * t, y1 + (iy1 - y1) * t
                for k in range(1, 6):
                    sy = top_y + (bot_y - top_y) * k / 6
                    near = depth == 0 and math.hypot(x - lamp[0], sy - lamp[1]) < 95
                    c = rnd.choice(spines_colour) if near and rnd.random() < 0.8 else rnd.choice(spines_sepia)
                    hgt = (bot_y - top_y) / 6 * 0.8
                    d.line((x, sy - hgt, x, sy), fill=shade(c, depth))
                    d.line((x, sy, x + 3, sy), fill=shade(INK, depth))
        # sechseckiger Durchgang
        hx, hy, hr = cx, cy, sh / 2
        hexpts = [(hx + hr * 1.15 * math.cos(math.radians(a)), hy + hr * math.sin(math.radians(a))) for a in range(0, 360, 60)]
        d.polygon(hexpts, outline=shade(LIGHT, depth))
        box, depth = (ix0, iy0, ix1, iy1), depth + 1

    # Lampe, Bücherstapel, Baron liest
    glow(img, d, lamp[0], lamp[1] - 6, 34, GOLD, 0.45)
    d.rectangle((lamp[0] - 2, lamp[1] - 10, lamp[0] + 2, lamp[1] - 4), fill=GOLD, outline=INK)
    for i, c in enumerate([RED, BLUE, GREEN, GOLD]):
        d.rectangle((86 - i, 150 - i * 4, 104 + i % 2, 153 - i * 4), fill=c, outline=INK)
    hx, hy = baron(d, 95, 138, coat=RED)
    d.polygon([(hx, hy - 2), (hx + 9, hy - 5), (hx + 9, hy + 1), (hx, hy + 3)], fill=PAPER, outline=INK)
    d.line((hx + 4, hy - 3, hx + 4, hy + 2), fill=MID)
    save(img, "m-selenothek-innen.png")


def selenothek_telegrafie():
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)
    sepia_sky(img, d, (240, 52, 34), seed=8)
    moon_ground(img, d, 150)
    # Kuppel der Selenothek im Vordergrund
    m, md = new_mask()
    md.chord((-40, 110, 220, 300), 180, 360, fill=1)
    fill_mask(img, m, LIGHT, MID, lambda x, y: (x + 20) / 260)
    d.arc((-40, 110, 220, 300), 180, 360, fill=PAPER)
    for a in range(200, 345, 18):
        x = 90 + 130 * math.cos(math.radians(a))
        y = 205 + 95 * math.sin(math.radians(a))
        d.line((90, 205, x, y), fill=MID)
    # Baron auf der Kuppel mit Spiegel
    hx, hy = baron(d, 96, 112, coat=RED)
    mx, my = hx + 6, hy - 6
    d.line((hx, hy, mx, my), fill=PAPER)
    d.ellipse((mx - 3, my - 3, mx + 3, my + 3), fill=GOLD, outline=INK)
    glow(img, d, mx, my, 9, GOLD, 0.7)
    baron(d, 96, 112, coat=RED)  # über den Lichtschein zeichnen
    d.line((hx, hy, mx, my), fill=PAPER)
    d.ellipse((mx - 3, my - 3, mx + 3, my + 3), fill=GOLD, outline=INK)
    # Lichtsignal zur Erde: Strich und Punkt
    ex, ey = 214, 70
    pattern = [1] * 8 + [0] * 4 + [1] * 3 + [0] * 4 + [1] * 8 + [0] * 4 + [1] * 3 + [0] * 4
    n = int(math.hypot(ex - mx, ey - my))
    for i in range(n):
        if pattern[i % len(pattern)]:
            t = i / n
            x, y = int(mx + (ex - mx) * t), int(my + (ey - my) * t)
            img.putpixel((x, y), GOLD)
            img.putpixel((x, y - 1), hexc("#f3d98a"))
    save(img, "m-selenothek-telegrafie.png")


if __name__ == "__main__":
    alchemistin_aschenland()
    selenothek_aussen()
    selenothek_innen()
    selenothek_telegrafie()
