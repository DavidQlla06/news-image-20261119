#!/usr/bin/env python3
"""Paint the 19 November 2026 world-news front page as one square image.

Input: stories.json in this folder (date, lead story, four grid stories,
two bottom stories, footer line). Output: entry.png, 1024 x 1024.

The page is built by a small renderer class that walks down the canvas
with a cursor instead of hard-coding every y coordinate: masthead, lead
story, a two-by-two grid, a bottom pair, and a footer rule. Run it with
`python3 generate.py` from this folder.
"""

import json
import os

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE_W, PAGE_H = 1024, 1024
MARGIN = 46
GUTTER = 26
COL_W = (PAGE_W - 2 * MARGIN - GUTTER) // 2

PALETTE = {
    "ink": (18, 18, 18),
    "soft": (74, 74, 74),
    "faint": (140, 140, 140),
    "paper": (253, 252, 248),
    "accent": (158, 28, 28),
    "wash": (242, 240, 234),
    "rule": (18, 18, 18),
}

DEJAVU = "/usr/share/fonts/truetype/dejavu"


def pick_font(size, bold=False):
    """Return a TrueType font, falling back to the PIL default."""
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    path = os.path.join(DEJAVU, name)
    try:
        return ImageFont.truetype(path, size)
    except (OSError, IOError):
        return ImageFont.load_default()


def wrap(pen, text, font, max_width):
    """Greedy word wrap measured with the real font, not char counts."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = (current + " " + word).strip()
        if pen.textlength(trial, font=font) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(pen, x, y, text, font, max_width, fill, spacing=6):
    """Draw wrapped text starting at (x, y); return the y after it."""
    for line in wrap(pen, text, font, max_width):
        pen.text((x, y), line, font=font, fill=fill)
        y += font.size + spacing
    return y


class FrontPage:
    """A 1024x1024 newspaper front page drawn top to bottom."""

    def __init__(self):
        self.canvas = Image.new("RGB", (PAGE_W, PAGE_H), PALETTE["paper"])
        self.pen = ImageDraw.Draw(self.canvas)
        self.y = 34

    def rule(self, weight=2, gap_above=0, gap_below=0):
        self.y += gap_above
        self.pen.line(
            [(MARGIN, self.y), (PAGE_W - MARGIN, self.y)],
            fill=PALETTE["rule"],
            width=weight,
        )
        self.y += weight + gap_below

    def masthead(self, date_line):
        title_font = pick_font(68, bold=True)
        title = "THE WORLD IN ONE PAGE"
        tw = self.pen.textlength(title, font=title_font)
        self.pen.text(
            ((PAGE_W - tw) / 2, self.y), title, font=title_font, fill=PALETTE["ink"]
        )
        self.y += 88
        date_font = pick_font(22)
        dw = self.pen.textlength(date_line, font=date_font)
        self.pen.text(
            ((PAGE_W - dw) / 2, self.y),
            date_line,
            font=date_font,
            fill=PALETTE["soft"],
        )
        self.y += 38
        self.rule(weight=4, gap_below=4)
        self.rule(weight=1, gap_below=16)

    def kicker(self, text):
        font = pick_font(20, bold=True)
        self.pen.text((MARGIN, self.y), text.upper(), font=font, fill=PALETTE["accent"])
        self.y += 30

    def headline(self, text, size, width):
        font = pick_font(size, bold=True)
        return draw_wrapped(
            self.pen, MARGIN, self.y, text, font, width, PALETTE["ink"], spacing=4
        )

    def lead(self, story):
        self.kicker(story["kicker"])
        self.y = self.headline(story["title"], 46, PAGE_W - 2 * MARGIN)
        self.y += 6
        body = pick_font(25)
        self.y = draw_wrapped(
            self.pen,
            MARGIN,
            self.y,
            story["summary"],
            body,
            PAGE_W - 2 * MARGIN,
            PALETTE["soft"],
            spacing=7,
        )
        self.y += 10
        self.rule(weight=1, gap_below=14)

    def cell(self, x, y_top, story, width):
        """One grid cell; returns the y just below it."""
        font_k = pick_font(18, bold=True)
        self.pen.text((x, y_top), story["kicker"].upper(), font=font_k, fill=PALETTE["accent"])
        y = y_top + 28
        font_h = pick_font(30, bold=True)
        y = draw_wrapped(self.pen, x, y, story["title"], font_h, width, PALETTE["ink"], spacing=4)
        y += 4
        font_b = pick_font(21)
        y = draw_wrapped(self.pen, x, y, story["summary"], font_b, width, PALETTE["soft"], spacing=5)
        return y

    def grid(self, stories):
        top = self.y
        left_end = self.cell(MARGIN, top, stories[0], COL_W)
        right_end = self.cell(MARGIN + COL_W + GUTTER, top, stories[1], COL_W)
        self.y = max(left_end, right_end) + 22
        self.rule(weight=1, gap_below=16)
        top = self.y
        left_end = self.cell(MARGIN, top, stories[2], COL_W)
        right_end = self.cell(MARGIN + COL_W + GUTTER, top, stories[3], COL_W)
        self.y = max(left_end, right_end) + 10
        self.rule(weight=1, gap_below=14)

    def bottom_pair(self, stories):
        top = self.y
        ends = []
        for i, story in enumerate(stories):
            x = MARGIN + i * (COL_W + GUTTER)
            font_h = pick_font(26, bold=True)
            y = draw_wrapped(self.pen, x, top, story["title"], font_h, COL_W, PALETTE["ink"], spacing=4)
            y += 4
            font_b = pick_font(20)
            y = draw_wrapped(self.pen, x, y, story["summary"], font_b, COL_W, PALETTE["soft"], spacing=5)
            ends.append(y)
        self.y = max(ends) + 12

    def footer(self, text):
        self.rule(weight=4, gap_above=6, gap_below=10)
        font = pick_font(17)
        tw = self.pen.textlength(text, font=font)
        self.pen.text(((PAGE_W - tw) / 2, self.y), text, font=font, fill=PALETTE["faint"])

    def save(self, path):
        # Thin frame around the whole page, then write the file.
        self.pen.rectangle([4, 4, PAGE_W - 5, PAGE_H - 5], outline=PALETTE["ink"], width=2)
        self.canvas.save(path, "PNG")


def main():
    with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    page = FrontPage()
    page.masthead(data["date"])
    page.lead(data["lead"])
    page.grid(data["grid"])
    page.bottom_pair(data["bottom"])
    page.footer(data["footer"])
    out = os.path.join(HERE, "entry.png")
    page.save(out)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
