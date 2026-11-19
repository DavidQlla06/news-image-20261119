#!/usr/bin/env python3
"""One-day world-news infographic generator (make.fun news-image daily).

Reads a stories JSON file and draws a 1024x1024 newspaper-front-page
PNG with PIL. The picture is fully self-contained: it names its day in
the masthead and shows each story with a flat drawn illustration, a
short headline and a one-line summary, so a viewer who missed the day
can tell what happened from the image alone.

Usage:  python3 generate.py stories.json entry.png

Only the standard library + Pillow are used (local build step). The entry
program (main.py) only copies the finished PNG, so the graded run needs
no fonts and no Pillow.
"""
import json
import sys
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 36
PAPER = (251, 248, 241)      # newsprint off-white
INK = (20, 20, 20)
GRAY = (90, 88, 82)
RULE = (20, 20, 20)
WHITE = (255, 255, 255)
SKY = (214, 232, 242)
SEA = (127, 168, 201)
RED = (179, 38, 30)
BLUE = (29, 78, 137)
GREEN = (46, 125, 50)
GOLD = (176, 132, 24)

FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, leading):
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def chip(draw, x, y, text, bg):
    """Small white-on-colour kicker tag; returns its width."""
    fnt = font(FONT_SANS_B, 19)
    tw = draw.textlength(text, font=fnt)
    pad_x, pad_y = 10, 5
    draw.rounded_rectangle([x, y, x + tw + 2 * pad_x, y + 28],
                           radius=4, fill=bg)
    draw.text((x + pad_x, y + pad_y), text, font=fnt, fill=WHITE)
    return tw + 2 * pad_x


# ---------------------------------------------------------------- icons
def icon_bridge(d, x, y, w, h, collapsed=False):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.rectangle([x, y + int(h * 0.68), x + w, y + h], fill=SEA)
    for i in range(3):  # waves
        yy = y + int(h * (0.74 + 0.08 * i))
        d.arc([x + 8 + i * 14, yy, x + 48 + i * 14, yy + 18],
              200, 340, fill=WHITE, width=3)
    deck_y = y + int(h * 0.52)
    d.rectangle([x + 6, deck_y, x + w - 6, deck_y + 10], fill=INK)
    for tx in (x + int(w * 0.22), x + int(w * 0.70)):
        d.rectangle([tx, y + int(h * 0.14), tx + 12, deck_y], fill=INK)
        d.line([tx + 6, y + int(h * 0.14), x + 10, deck_y], fill=INK, width=2)
        d.line([tx + 6, y + int(h * 0.14), x + w - 10, deck_y], fill=INK, width=2)
    cx = x + w // 2
    if collapsed:  # middle span dropped into the water, tilted
        d.rectangle([x + 6, deck_y, cx - 26, deck_y + 10], fill=INK)
        d.rectangle([cx + 26, deck_y, x + w - 6, deck_y + 10], fill=INK)
        d.polygon([(cx - 30, deck_y + 2), (cx + 30, deck_y + 34),
                   (cx + 30, deck_y + 46), (cx - 30, deck_y + 14)], fill=INK)
        d.polygon([(cx - 30, deck_y + 2), (cx - 14, deck_y - 12),
                   (cx - 2, deck_y - 12), (cx - 30, deck_y + 2)], fill=INK)
        for sx, sy, r in ((cx - 8, deck_y - 26, 12), (cx + 12, deck_y - 40, 15),
                          (cx + 2, deck_y - 58, 10)):
            d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(120, 120, 120))
    else:  # gap blasted in the deck + smoke
        d.rectangle([x + 6, deck_y, cx - 22, deck_y + 10], fill=INK)
        d.rectangle([cx + 22, deck_y, x + w - 6, deck_y + 10], fill=INK)
        d.polygon([(cx - 22, deck_y), (cx - 12, deck_y - 16),
                   (cx + 4, deck_y - 16), (cx + 22, deck_y)], fill=RED)
        for sx, sy, r in ((cx - 6, deck_y - 34, 13), (cx + 14, deck_y - 52, 16),
                          (cx + 2, deck_y - 74, 11)):
            d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(110, 110, 110))


def icon_tanker(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.rectangle([x, y + int(h * 0.66), x + w, y + h], fill=SEA)
    # mine: spiked circle, clear of the containers
    mx, my, mr = x + int(w * 0.82), y + int(h * 0.26), 11
    for k in range(8):
        ang = k * 3.14159 / 4
        d.line([mx + int(mr * 0.9 * _cos(ang)), my + int(mr * 0.9 * _sin(ang)),
                mx + int((mr + 9) * _cos(ang)), my + int((mr + 9) * _sin(ang))],
               fill=INK, width=3)
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=INK)
    # tanker hull + containers
    d.polygon([(x + 8, y + int(h * 0.52)), (x + w - 8, y + int(h * 0.52)),
               (x + w - 26, y + int(h * 0.66)), (x + 22, y + int(h * 0.66))],
              fill=(60, 60, 60))
    for i, c in enumerate((RED, BLUE, GOLD)):
        d.rectangle([x + 22 + i * 34, y + int(h * 0.36), x + 50 + i * 34,
                     y + int(h * 0.52)], fill=c, outline=INK)
    # flame above the hull
    fx = x + int(w * 0.42)
    d.polygon([(fx - 12, y + int(h * 0.34)), (fx, y + int(h * 0.16)),
               (fx + 12, y + int(h * 0.34))], fill=(232, 120, 20))
    d.polygon([(fx - 6, y + int(h * 0.34)), (fx, y + int(h * 0.24)),
               (fx + 6, y + int(h * 0.34))], fill=(245, 200, 40))


def _cos(a):
    import math
    return math.cos(a)


def _sin(a):
    import math
    return math.sin(a)


def icon_jet(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    for cx, cy, r in ((x + 18, y + 18, 12), (x + 48, y + 34, 9),
                      (x + 88, y + 14, 10)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WHITE)
    # fighter jet silhouette, nose to the right, large in the frame
    jx, jy = x + int(w * 0.46), y + int(h * 0.52)
    d.polygon([(jx - 46, jy), (jx + 40, jy - 12), (jx + 56, jy),
               (jx + 40, jy + 12)], fill=(70, 70, 70))
    d.polygon([(jx - 6, jy - 4), (jx - 30, jy - 32), (jx - 14, jy - 2)],
              fill=(70, 70, 70))
    d.polygon([(jx - 6, jy + 4), (jx - 26, jy + 28), (jx - 12, jy + 2)],
              fill=(70, 70, 70))
    d.polygon([(jx - 46, jy - 6), (jx - 58, jy - 22), (jx - 48, jy)],
              fill=(70, 70, 70))
    d.polygon([(jx - 46, jy + 6), (jx - 58, jy + 22), (jx - 48, jy)],
              fill=(70, 70, 70))
    for i in range(3):  # contrail
        d.line([jx - 58 - i * 4, jy - 4 + i * 5, x + 4, jy - 4 + i * 5],
               fill=WHITE, width=3)


def icon_aid(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(253, 236, 234))
    bx, by, bw, bh = x + int(w * 0.20), y + int(h * 0.42), int(w * 0.60), int(h * 0.38)
    d.rectangle([bx, by, bx + bw, by + bh], fill=(176, 132, 80), outline=INK, width=3)
    d.line([bx + bw // 2, by, bx + bw // 2, by + bh], fill=INK, width=3)
    d.line([bx, by + bh // 2, bx + bw, by + bh // 2], fill=INK, width=3)
    cx, cy, r = x + w // 2, y + int(h * 0.26), 26
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WHITE, outline=RED, width=3)
    d.rectangle([cx - 5, cy - 14, cx + 5, cy + 14], fill=RED)
    d.rectangle([cx - 14, cy - 5, cx + 14, cy + 5], fill=RED)


def icon_chart(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=WHITE)
    d.line([x + 18, y + 14, x + 18, y + h - 18], fill=INK, width=3)
    d.line([x + 18, y + h - 18, x + w - 12, y + h - 18], fill=INK, width=3)
    for gy in (y + 30, y + 58, y + 86):
        d.line([x + 18, gy, x + w - 12, gy], fill=(220, 220, 220), width=1)
    pts = [(x + 24, y + 30), (x + 52, y + 44), (x + 80, y + 40),
           (x + 108, y + 66), (x + 132, y + 88)]
    d.line(pts, fill=RED, width=4, joint="curve")
    for px, py in pts:
        d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=RED)
    ax, ay = pts[-1]
    d.polygon([(ax, ay + 16), (ax - 9, ay + 2), (ax + 9, ay + 2)], fill=RED)


def icon_climate(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(227, 242, 225))
    cx, cy, r = x + w // 2, y + int(h * 0.52), 44
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(88, 160, 200))
    d.ellipse([cx - 26, cy - 22, cx + 2, cy + 4], fill=(90, 170, 90))
    d.ellipse([cx + 4, cy + 8, cx + 28, cy + 30], fill=(90, 170, 90))
    d.ellipse([cx - 8, cy - 34, cx + 18, cy - 14], fill=(120, 190, 110))
    sx, sy = x + int(w * 0.78), y + int(h * 0.20)
    for k in range(8):
        ang = k * 3.14159 / 4
        d.line([sx + int(20 * _cos(ang)), sy + int(20 * _sin(ang)),
                sx + int(30 * _cos(ang)), sy + int(30 * _sin(ang))],
               fill=(245, 180, 20), width=3)
    d.ellipse([sx - 14, sy - 14, sx + 14, sy + 14], fill=(245, 200, 40))


def icon_virus(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(253, 236, 234))
    cx, cy, r = x + w // 2, y + h // 2, 34
    for k in range(10):
        ang = k * 3.14159 / 5
        ex, ey = cx + int((r + 14) * _cos(ang)), cy + int((r + 14) * _sin(ang))
        d.line([cx + int(r * _cos(ang)), cy + int(r * _sin(ang)), ex, ey],
               fill=RED, width=4)
        d.ellipse([ex - 5, ey - 5, ex + 5, ey + 5], fill=RED)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    for ox, oy in ((-12, -8), (10, -14), (14, 10), (-10, 12)):
        d.ellipse([cx + ox - 5, cy + oy - 5, cx + ox + 5, cy + oy + 5],
                  fill=(255, 120, 110))


def icon_plane(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.polygon([(x + 6, y + h - 14), (x + int(w * 0.34), y + int(h * 0.52)),
               (x + int(w * 0.62), y + h - 14)], fill=(90, 110, 130))
    d.polygon([(x + int(w * 0.62), y + h - 14), (x + int(w * 0.86), y + int(h * 0.68)),
               (x + w - 4, y + h - 14)], fill=(90, 110, 130))
    px, py = x + int(w * 0.52), y + int(h * 0.34)
    d.polygon([(px - 46, py + 16), (px + 40, py - 14), (px + 52, py - 4),
               (px + 10, py + 22)], fill=(60, 60, 60))
    d.polygon([(px - 8, py + 6), (px - 30, py + 34), (px - 16, py + 10)],
              fill=(60, 60, 60))
    for sx, sy, r in ((px + 56, py - 26, 10), (px + 70, py - 40, 13),
                      (px + 58, py - 56, 9)):
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(110, 110, 110))


def icon_capitol(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 236, 243))
    cx = x + w // 2
    d.rectangle([cx - 52, y + int(h * 0.52), cx + 52, y + int(h * 0.78)],
                fill=WHITE, outline=INK, width=3)
    d.pieslice([cx - 34, y + int(h * 0.18), cx + 34, y + int(h * 0.62)],
               180, 360, fill=WHITE, outline=INK, width=3)
    d.rectangle([cx - 3, y + int(h * 0.12), cx + 3, y + int(h * 0.20)], fill=INK)
    for i in range(5):
        colx = cx - 44 + i * 22
        d.rectangle([colx, y + int(h * 0.56), colx + 8, y + int(h * 0.76)],
                    fill=INK)
    d.rectangle([x + 12, y + int(h * 0.78), x + w - 12, y + int(h * 0.84)],
                fill=INK)
    d.line([x + int(w * 0.68), y + int(h * 0.30), x + int(w * 0.76), y + int(h * 0.44)],
           fill=GREEN, width=5)
    d.line([x + int(w * 0.76), y + int(h * 0.44), x + int(w * 0.94), y + int(h * 0.16)],
           fill=GREEN, width=5)


def icon_summit(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(234, 240, 248))
    bw = int(w * 0.24)
    for i, c in enumerate((RED, GOLD, BLUE)):
        bx = x + int(w * 0.14) + i * (bw + 6)
        d.rectangle([bx, y + int(h * 0.16), bx + bw, y + int(h * 0.62)],
                    fill=c, outline=INK, width=2)
    d.ellipse([x + int(w * 0.30), y + int(h * 0.56), x + int(w * 0.70),
               y + int(h * 0.96)], fill=(88, 160, 200),
              outline=INK, width=2)
    d.ellipse([x + int(w * 0.38), y + int(h * 0.64), x + int(w * 0.52),
               y + int(h * 0.78)], fill=(90, 170, 90))
    d.ellipse([x + int(w * 0.56), y + int(h * 0.76), x + int(w * 0.66),
               y + int(h * 0.88)], fill=(90, 170, 90))


ICONS = {
    "bridge": icon_bridge,
    "bridge_collapsed": lambda d, x, y, w, h: icon_bridge(d, x, y, w, h, True),
    "tanker": icon_tanker,
    "jet": icon_jet,
    "aid": icon_aid,
    "chart": icon_chart,
    "climate": icon_climate,
    "virus": icon_virus,
    "plane": icon_plane,
    "capitol": icon_capitol,
    "summit": icon_summit,
}

KICKER_COLORS = {
    "WAR IN EUROPE": RED, "GULF CRISIS": RED, "ASIA": BLUE,
    "GAZA": (120, 60, 140), "MARKETS": GOLD, "CLIMATE": GREEN,
    "SUMMIT": BLUE, "US POLITICS": BLUE, "HEALTH": RED, "DISASTER": INK,
}


def build(spec, out_path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    date_str = spec["date"]          # e.g. THURSDAY 19 NOVEMBER 2026
    lead = spec["lead"]
    stories = spec["stories"]       # 4 grid stories
    bottom = spec["bottom"]         # 2 short headlines
    footer = spec["footer"]

    # ---- masthead
    eyebrow = font(FONT_SANS_B, 22)
    d.text(((W - d.textlength("THE WORLD IN ONE IMAGE", font=eyebrow)) / 2,
            26), "THE WORLD IN ONE IMAGE", font=eyebrow, fill=GRAY)
    date_size = 56
    while date_size > 30:
        date_f = font(FONT_SERIF_B, date_size)
        if d.textlength(date_str, font=date_f) <= W - 2 * MARGIN - 8:
            break
        date_size -= 2
    d.text(((W - d.textlength(date_str, font=date_f)) / 2, 56),
           date_str, font=date_f, fill=INK)
    d.line([MARGIN, 140, W - MARGIN, 140], fill=RULE, width=4)
    d.line([MARGIN, 148, W - MARGIN, 148], fill=RULE, width=1)

    # ---- lead story
    ly, lh = 164, 320
    d.rectangle([MARGIN, ly, W - MARGIN, ly + lh], fill=WHITE, outline=INK, width=2)
    ix, iy, iw, ih = MARGIN + 2, ly + 2, 372, lh - 4
    ICONS[lead["icon"]](d, ix, iy, iw, ih)
    d.line([ix + iw, ly, ix + iw, ly + lh], fill=INK, width=2)
    tx = ix + iw + 22
    tw = W - MARGIN - tx - 18
    chip(d, tx, ly + 20, lead["kicker"], KICKER_COLORS.get(lead["kicker"], INK))
    hf = font(FONT_SANS_B, 40)
    lines = wrap(d, lead["headline"], hf, tw)
    y = draw_lines(d, lines[:3], tx, ly + 62, hf, INK, 48)
    bf = font(FONT_SANS, 26)
    lines = wrap(d, lead["summary"], bf, tw)
    draw_lines(d, lines[:3], tx, y + 8, bf, (50, 50, 50), 33)

    # ---- grid of 4 stories
    gy = ly + lh + 16
    cw, chh, gap = 468, 198, 16
    for i, s in enumerate(stories):
        cx = MARGIN + (i % 2) * (cw + gap)
        cy = gy + (i // 2) * (chh + gap)
        d.rectangle([cx, cy, cx + cw, cy + chh], fill=WHITE, outline=INK, width=2)
        ICONS[s["icon"]](d, cx + 2, cy + 2, 120, chh - 4)
        d.line([cx + 122, cy, cx + 122, cy + chh], fill=(200, 200, 200), width=1)
        tx2 = cx + 136
        tw2 = cx + cw - tx2 - 12
        chip(d, tx2, cy + 12, s["kicker"], KICKER_COLORS.get(s["kicker"], INK))
        hf2 = font(FONT_SANS_B, 26)
        lines = wrap(d, s["headline"], hf2, tw2)
        y2 = draw_lines(d, lines[:3], tx2, cy + 48, hf2, INK, 31)
        bf2 = font(FONT_SANS, 21)
        lines = wrap(d, s["summary"], bf2, tw2)
        draw_lines(d, lines[:2], tx2, y2 + 4, bf2, (60, 60, 60), 26)

    # ---- bottom strip: two short headlines (auto-fit so they never clip)
    by = gy + 2 * chh + gap + 14
    d.rectangle([MARGIN, by, W - MARGIN, by + 52], fill=(238, 234, 224),
                outline=INK, width=1)
    left = "•  " + bottom[0]
    right = "•  " + bottom[1]
    bsize = 22
    while bsize > 16:
        bf3 = font(FONT_SANS_B, bsize)
        if (d.textlength(left, font=bf3) + d.textlength(right, font=bf3)
                + 40) <= W - 2 * MARGIN - 16:
            break
        bsize -= 1
    lw = d.textlength(left, font=bf3)
    rw = d.textlength(right, font=bf3)
    total = lw + rw + 40
    x0 = (W - total) / 2
    d.text((x0, by + 14), left, font=bf3, fill=INK)
    d.text((x0 + lw + 40, by + 14), right, font=bf3, fill=INK)

    # ---- footer
    ff = font(FONT_SANS, 18)
    d.text(((W - d.textlength(footer, font=ff)) / 2, by + 66),
           footer, font=ff, fill=GRAY)

    img.save(out_path, "PNG", optimize=True)
    return out_path


def main():
    spec = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    build(spec, out)
    import os
    size = os.path.getsize(out)
    # Competition gate: at most 1 MiB and 1024 by 1024 pixels.
    assert size <= 1048576, f"{out} is {size} bytes, over the 1 MiB cap"
    with Image.open(out) as im:
        assert im.size[0] <= 1024 and im.size[1] <= 1024, im.size
    print(out, size, "bytes")


if __name__ == "__main__":
    main()
