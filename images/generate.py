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


def muenchhausen_mond():
    ink, dark, mid, light, paper = map(hexc, ["#24180f", "#4a3423", "#8a6a48", "#c9a978", "#efe0bd"])
    img = Image.new("RGB", (W, H), ink)
    d = ImageDraw.Draw(img)
    vgradient(img, (0, 0, W, 150), ink, dark)
    rnd = random.Random(3)
    for _ in range(90):
        img.putpixel((rnd.randrange(W), rnd.randrange(140)), rnd.choice([light, paper, mid]))

    # Erde mit Schraffur-Terminator
    ex, ey, er = 62, 38, 22
    m, md = new_mask()
    md.ellipse((ex - er, ey - er, ex + er, ey + er), fill=1)
    fill_mask(img, m, light, dark, lambda x, y: (x - ex + 6) / 20)
    for cx, cy, w, h in [(54, 30, 9, 6), (66, 44, 7, 8), (58, 48, 5, 3)]:
        d.ellipse((cx, cy, cx + w, cy + h), fill=mid)

    # Mondoberfläche mit Kratern
    m, md = new_mask()
    pts = [(x, 140 + 4 * math.sin(x / 17) + 2 * math.sin(x / 5)) for x in range(0, W + 1, 2)]
    md.polygon(pts + [(W, H), (0, H)], fill=1)
    fill_mask(img, m, light, mid, lambda x, y: (y - 136) / 40)
    for cx, cy, rx, ry in [(120, 158, 16, 4), (250, 166, 22, 5), (30, 170, 12, 3), (290, 150, 8, 2)]:
        d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=dark)
        d.arc((cx - rx, cy - ry - 1, cx + rx, cy + ry - 1), 180, 360, fill=paper)

    # Kraterglashaus
    d.chord((38, 124, 86, 156), 180, 360, fill=dark, outline=light)
    for x in range(44, 84, 7):
        d.line((x, 128, x, 140), fill=mid)

    # Bohnenranke, die sich hinauf windet
    stalk = [(62 + 18 * math.sin(t / 9) + t * 0.95, 132 - t * 0.95) for t in range(0, 82)]
    d.line(stalk, fill=dark, width=3)
    d.line(stalk, fill=mid, width=1)
    for i in range(6, 80, 9):
        x, y = stalk[i]
        side = 1 if i % 2 else -1
        d.ellipse((x + side * 2 - 3, y - 2, x + side * 2 + 3, y + 2), fill=mid, outline=dark)
    tip = stalk[-1]

    # Luftschiff
    m, md = new_mask()
    md.ellipse((206, 14, 304, 52), fill=1)
    fill_mask(img, m, paper, mid, lambda x, y: (y - 24) / 30)
    d.ellipse((206, 14, 304, 52), outline=ink)
    mp = m.load()
    for x in range(220, 296, 12):  # Nähte der Hülle
        for y in range(14, 53):
            if mp[x, y]:
                img.putpixel((x, y), light)
    d.rectangle((238, 62, 272, 70), fill=dark, outline=ink)
    for x in (240, 255, 270):
        d.line((x, 50, x, 62), fill=light)
    # Strickleiter aus der Gondel
    for x in (250, 254):
        d.line((x, 70, x, 92), fill=light)
    for y in range(73, 92, 3):
        d.line((250, y, 254, y), fill=light)

    # Seil aus Bohnenstroh: zu kurz
    bx, by = 228, 98
    rope = [(tip[0] + (bx - tip[0]) * t, tip[1] + (by - 3 - tip[1]) * t + 14 * math.sin(t * math.pi))
            for t in [i / 20 for i in range(21)]]
    d.line(rope, fill=paper, width=1)
    for i, (x, y) in enumerate(rope[::2]):
        img.putpixel((int(x), int(y) + 1), light)

    # Münchhausen am Seilende, nach der Leiter greifend
    d.polygon([(bx - 4, by - 9), (bx + 4, by - 9), (bx, by - 13)], fill=ink)  # Dreispitz
    d.rectangle((bx - 2, by - 8, bx + 2, by - 5), fill=paper)  # Gesicht
    d.rectangle((bx - 3, by - 4, bx + 3, by + 4), fill=dark, outline=ink)  # Rock
    d.line((bx - 2, by + 5, bx - 3, by + 10), fill=ink)
    d.line((bx + 2, by + 5, bx + 4, by + 9), fill=ink)
    d.line((bx, by - 4, bx - 1, by - 10), fill=paper)  # Hand am Seil
    d.line((bx + 3, by - 3, bx + 13, by - 8), fill=paper)  # Arm zur Leiter
    save(img, "a-muenchhausen-mond.png")


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


def muenchhausen_wabe():
    sky_top, sky_low = hexc("#5a5957"), hexc("#a3a19c")
    img = Image.new("RGB", (W, H), sky_top)
    d = ImageDraw.Draw(img)
    vgradient(img, (0, 0, W, 140), sky_top, sky_low)
    faces = [hexc("#6a6864"), hexc("#53514e"), hexc("#3e3d3b")]
    top = wabe_tower(d, 276, 142, [(110, 26), (92, 24), (76, 22), (62, 20)], faces, hexc("#2c2b2a"))
    colours = [hexc(c) for c in ["#d9472b", "#3fa58a", "#2f4fa0", "#e8c04a", "#f2ece0"]]
    # Farbspritzer an der Kuppel, wo der Ballon gestartet ist
    rnd = random.Random(11)
    for _ in range(40):
        img.putpixel((276 + rnd.randint(-22, 22), top + rnd.randint(-14, 4)), rnd.choice(colours))

    # Ballon aus Buchseiten
    bx, by, rx, ry = 150, 50, 34, 38
    m, md = new_mask()
    md.ellipse((bx - rx, by - ry, bx + rx, by + ry), fill=1)
    md.polygon([(bx - 26, by + 22), (bx + 26, by + 22), (bx + 8, by + 50), (bx - 8, by + 50)], fill=1)
    mp = m.load()
    ink = hexc("#2b2a29")
    for py in range(by - ry, by + 52, 9):
        offset = (py // 9) % 2 * 6
        for px in range(bx - rx - 12 + offset, bx + rx + 12, 12):
            c = colours[(px // 12 + py // 9 * 3) % len(colours)]
            for y in range(py, py + 9):
                for x in range(px, px + 12):
                    if 0 <= x < W and 0 <= y < H and mp[x, y]:
                        edge = y == py or x == px
                        line = (y - py) in (3, 6) and px + 2 < x < px + 10
                        img.putpixel((x, y), ink if edge else (hexc("#3a3836") if line else c))
    d.ellipse((bx - rx, by - ry, bx + rx, by + ry), outline=ink)
    # Korb mit Baron
    for x in (bx - 8, bx + 8):
        d.line((x, by + 50, x, by + 60), fill=ink)
    d.rectangle((bx - 9, by + 60, bx + 9, by + 68), fill=hexc("#8a6a48"), outline=ink)
    d.polygon([(bx - 5, by + 54), (bx + 3, by + 54), (bx - 1, by + 50)], fill=ink)
    d.rectangle((bx - 3, by + 55, bx + 1, by + 59), fill=hexc("#f0d2b0"))
    d.line((bx + 2, by + 58, bx + 10, by + 52), fill=hexc("#f0d2b0"))  # winkt

    # Farbspur von der Kuppel zum Ballon
    for i in range(30):
        t = i / 30
        x = int(276 - (276 - bx - 20) * t)
        y = int(top - 4 - (top - by - 30) * t + 8 * math.sin(t * math.pi))
        img.putpixel((x, y), colours[i % 4])

    # Dünen
    dunes(img, 140, 4, 0.03, 1.0, hexc("#8f8c86"), hexc("#75726c"))
    dunes(img, 156, 5, 0.025, 3.0, hexc("#7a7771"), hexc("#5e5c57"))

    # Aschensegler unten links
    hull, wood, sail = hexc("#4a4642"), hexc("#35322f"), hexc("#cfccc4")
    sx, sy = 52, 150
    d.polygon([(sx - 30, sy - 8), (sx + 30, sy - 8), (sx + 22, sy), (sx - 24, sy)], fill=hull, outline=wood)
    d.line((sx - 26, sy + 3, sx + 26, sy + 3), fill=wood, width=2)  # Kufen
    for x in (sx - 20, sx + 18):
        d.line((x, sy, x, sy + 3), fill=wood)
    d.line((sx - 2, sy - 8, sx - 2, sy - 58), fill=wood)
    d.polygon([(sx, sy - 56), (sx + 26, sy - 14), (sx, sy - 12)], fill=sail, outline=wood)
    d.polygon([(sx - 4, sy - 50), (sx - 24, sy - 14), (sx - 4, sy - 12)], fill=hexc("#b5b2aa"), outline=wood)
    for x in (sx + 10, sx + 16):  # Crew zeigt nach oben
        d.rectangle((x, sy - 13, x + 1, sy - 9), fill=wood)
        d.line((x + 1, sy - 13, x + 4, sy - 18), fill=wood)

    rnd = random.Random(5)
    for _ in range(110):
        img.putpixel((rnd.randrange(W), rnd.randrange(H)), hexc("#c4c1ba"))
    save(img, "c-aschenland-muenchhausen.png")


if __name__ == "__main__":
    muenchhausen_mond()
    alchemistin_aschenland()
    muenchhausen_wabe()
