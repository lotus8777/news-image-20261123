#!/usr/bin/env python3
"""Build the news-image-20261123 poster: a 1024x1024 cartoon news poster.

Reads the flat-vector hero illustration (hero-cop31.png, made for this entry)
and composites it with a cherry-red masthead, a lead headline band and four
story cards. Output is entry.png next to this script. Deterministic: same
inputs give the same bytes.
"""

import hashlib
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
HERO_PATH = os.path.join(HERE, "..", "hero-cop31.png")
OUT_PATH = os.path.join(HERE, "entry.png")

W, H = 1024, 1024

CREAM = (255, 246, 229)
RED = (193, 39, 45)
INK = (20, 33, 61)
BODY = (58, 58, 58)
MUTED = (120, 110, 96)
WHITE = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    path = os.path.join(FONT_DIR, name)
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap to a pixel width; returns a list of lines."""
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def cover_crop(img, target_w, target_h, focus_y=0.45):
    """Scale img to cover target_w x target_h, cropping around focus_y."""
    sw, sh = img.size
    scale = max(target_w / sw, target_h / sh)
    nw, nh = int(sw * scale + 0.5), int(sh * scale + 0.5)
    img = img.resize((nw, nh), Image.LANCZOS)
    top = int((nh - target_h) * focus_y)
    top = max(0, min(top, nh - target_h))
    return img.crop((0, top, target_w, top + target_h))


def rounded_card(draw, box, radius, fill, accent):
    """A white card with rounded corners and a coloured top strip."""
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=radius, fill=fill)
    draw.rounded_rectangle((x0, y0, x1, y0 + 12), radius=6, fill=accent)
    # square off the strip's bottom corners so it sits flush in the card
    draw.rectangle((x0, y0 + 6, x1, y0 + 12), fill=accent)


def draw_card(draw, box, accent, kicker, headline, body):
    x0, y0, x1, y1 = box
    rounded_card(draw, box, 16, WHITE, accent)
    pad = 20
    inner = x1 - x0 - 2 * pad
    kf = font("DejaVuSans-Bold.ttf", 15)
    hf = font("DejaVuSans-Bold.ttf", 25)
    bf = font("DejaVuSans.ttf", 19)
    draw.text((x0 + pad, y0 + 22), kicker, font=kf, fill=accent)
    draw.text((x0 + pad, y0 + 46), headline, font=hf, fill=INK)
    lines = wrap(draw, body, bf, inner)[:2]
    y = y0 + 76
    for line in lines:
        draw.text((x0 + pad, y), line, font=bf, fill=BODY)
        y += 25


def main():
    hero = Image.open(HERO_PATH).convert("RGB")
    poster = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(poster)

    # Masthead: cherry red, paper name + the date it sums up.
    draw.rectangle((0, 0, W, 108), fill=RED)
    title_f = font("DejaVuSans-Bold.ttf", 52)
    date_f = font("DejaVuSans-Bold.ttf", 24)
    title = "WORLD NEWS"
    tw = draw.textlength(title, font=title_f)
    draw.text(((W - tw) / 2, 12), title, font=title_f, fill=WHITE)
    date = "MONDAY  ·  23 NOVEMBER 2026"
    dw = draw.textlength(date, font=date_f)
    draw.text(((W - dw) / 2, 70), date, font=date_f, fill=WHITE)

    # Hero illustration, full width under the masthead.
    hero_img = cover_crop(hero, W, 500, focus_y=0.5)
    poster.paste(hero_img, (0, 108))

    # Lead headline band.
    draw.rectangle((0, 608, W, 692), fill=INK)
    lead_f = font("DejaVuSans-Bold.ttf", 42)
    sub_f = font("DejaVuSans.ttf", 20)
    draw.text((40, 616), "COP31 COLLAPSES", font=lead_f, fill=WHITE)
    draw.text(
        (40, 662),
        "No deal in Antalya \u2014 EU & UK reject a pact with no fossil-fuel phase-out",
        font=sub_f,
        fill=(214, 222, 235),
    )

    # Four story cards, 2 x 2.
    cards = [
        (
            (228, 87, 46),
            "MIDDLE EAST \u00b7 WAR",
            "HOUTHIS CLAIM REFINERY HIT",
            "Rabigh refinery & radar near Riyadh targeted, group says; "
            "6 hurt in Sanaa strike.",
        ),
        (
            (233, 164, 38),
            "INDONESIA",
            "CANDY FACTORY FIRE",
            "3 dead, 34 missing in Banten blaze; rescuers pull "
            "24 body bags from the ruins.",
        ),
        (
            (46, 111, 219),
            "UKRAINE \u00b7 LIBYA",
            "KYIV FLAT HIT, WARSHIP SUNK",
            "11 killed in Dymer strike, 14 missing; sea drones sink "
            "Russian corvette at Benghazi.",
        ),
        (
            (29, 53, 87),
            "USA \u00b7 MIDTERMS",
            "DEMOCRATS TAKE THE HOUSE",
            "258 seats \u2014 biggest majority since 1992 as Hubbard "
            "flips North Carolina.",
        ),
    ]
    xs = (24, 524)
    ys = (704, 854)
    cw, ch = 476, 140
    for i, (accent, kicker, headline, body) in enumerate(cards):
        x0 = xs[i % 2]
        y0 = ys[i // 2]
        draw_card(draw, (x0, y0, x0 + cw, y0 + ch), accent, kicker, headline, body)

    # Footer: date again plus sources.
    foot_f = font("DejaVuSans.ttf", 15)
    foot = "23 NOVEMBER 2026  \u00b7  SOURCES: REUTERS \u00b7 AP \u00b7 CNN \u00b7 LE MONDE \u00b7 THE INDEPENDENT"
    fw = draw.textlength(foot, font=foot_f)
    draw.text(((W - fw) / 2, 1002), foot, font=foot_f, fill=MUTED)

    poster.save(OUT_PATH, format="PNG", optimize=True)
    data = open(OUT_PATH, "rb").read()
    print("wrote", OUT_PATH)
    print("bytes:", len(data), "(limit 1048576)")
    print("sha256:", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
