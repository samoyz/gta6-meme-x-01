#!/usr/bin/env python3
"""Build the DBWD-style GTA 6 meme (v2) for make.fun bounty gta6-meme-x-01.

Concept (promised to Firham 2026-11-21 ~02:11 WIB, "besok bikin yang lebih
spektakuler dengan gaya art dbwb"): the meme as a reconstructed denim
jacket, in the DBWD Atelier language from
~/workspace/design-references/dbwd-studio.md:
- charcoal denim background with a woven texture, not a digital gradient
- the make.fun ghost as a cream fabric patch, stitched on with sashiko
  X stitches at the corners, ghost printed in charcoal
- the Vice City sun as patchwork: gold / cream / faded-denim wedges with
  dashed stitch seams, ONE orange-red wedge as the single accent
- palm silhouettes as dark denim cut-outs framing the scene
- serif capitals for the title, wide-spaced monospace for the label,
  like a sewn-on woven label
- ONE accent colour only: orange-red (sun wedge + MAKE.FUN + SAMOYZ tab)

Same joke as v1: "WAITED 13 YEARS FOR GTA 6" / "MY AGENT PAID FOR IT ON
MAKE.FUN". Output meme-dbwd.png, 1024x1024, readable at 480x480.
Does NOT overwrite meme.png (v1 stays the current entry until Firham
approves v2 and posts it; the last entry before the deadline counts).

Reproducible: re-running this script in a fresh session regenerates the
identical image, so that session's transcript covers authorship.
"""
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1024, 1024

DENIM = (36, 35, 43)          # charcoal denim
DENIM_DARK = (22, 21, 27)     # ground / palm cut-outs
DENIM_MID = (62, 60, 72)      # lighter denim thread
DENIM_FADED = (112, 118, 132)  # faded denim grey wedge
CREAM = (238, 230, 210)       # bone off-white
CREAM_DIM = (216, 206, 182)
GOLD = (212, 164, 74)
GOLD_DARK = (178, 132, 52)
ACCENT = (214, 69, 40)        # the ONE orange-red accent
STITCH = (245, 240, 225)      # white thread
INK = (30, 28, 34)            # charcoal print on the cream patch
DIM_CREAM = (170, 162, 142)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
MARK = "/home/hatch/workspace/makefun/gta6-meme-x-01-presskit/press-kit/make-fun-press-kit/mark-1024.png"


def denim_texture(w, h, base, seed=11):
    """Charcoal denim: woven horizontal/vertical threads + speckle."""
    img = Image.new("RGB", (w, h), base)
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    # weave: faint alternating thread lines
    for y in range(0, h, 3):
        a = 10 if (y // 3) % 2 == 0 else 6
        d.line([(0, y), (w, y)], fill=(255, 255, 255, a), width=1)
    for x in range(0, w, 3):
        a = 9 if (x // 3) % 2 == 0 else 5
        d.line([(x, 0), (x, h)], fill=(0, 0, 0, a), width=1)
    # mottling: large soft lighter/darker blotches
    rnd = random.Random(seed)
    for _ in range(14):
        x, y = rnd.randint(0, w), rnd.randint(0, h)
        r = rnd.randint(90, 260)
        tone = (255, 255, 255, 7) if rnd.random() < 0.5 else (0, 0, 0, 9)
        d.ellipse([x - r, y - r, x + r, y + r], fill=tone)
    ov = ov.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
    # speckle
    d = ImageDraw.Draw(img, "RGBA")
    rnd = random.Random(seed + 1)
    for _ in range(3500):
        x, y = rnd.randint(0, w - 1), rnd.randint(0, h - 1)
        a = rnd.randint(8, 26)
        c = (255, 255, 255, a) if rnd.random() < 0.5 else (0, 0, 0, a)
        d.point((x, y), fill=c)
    return img


def dashed_line(draw, p0, p1, fill, width=3, dash=12, gap=9):
    x0, y0 = p0
    x1, y1 = p1
    length = math.hypot(x1 - x0, y1 - y0)
    if length == 0:
        return
    dx, dy = (x1 - x0) / length, (y1 - y0) / length
    t = 0.0
    while t < length:
        t2 = min(t + dash, length)
        draw.line([(x0 + dx * t, y0 + dy * t),
                   (x0 + dx * t2, y0 + dy * t2)], fill=fill, width=width)
        t += dash + gap


def dashed_circle(draw, cx, cy, r, fill, width=3, dash=12, gap=9):
    n = int(2 * math.pi * r / (dash + gap))
    for i in range(n):
        a0 = 2 * math.pi * i / n
        a1 = a0 + 2 * math.pi * dash / (dash + gap) / n
        draw.arc([cx - r, cy - r, cx + r, cy + r],
                 math.degrees(a0), math.degrees(a1), fill=fill, width=width)


def stitch_x(draw, cx, cy, s, fill, width=4):
    draw.line([(cx - s, cy - s), (cx + s, cy + s)], fill=fill, width=width)
    draw.line([(cx + s, cy - s), (cx - s, cy + s)], fill=fill, width=width)


def text_center(draw, cx, y, text, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - w / 2 - bbox[0], y - bbox[1]), text, font=font, fill=fill)
    return h


def spaced_text_center(draw, cx, y, text, font, fill, tracking=7):
    """Monospace text with wide letter spacing, centred; returns height.

    Characters are drawn at their natural baseline position (via the
    font's advance width), NOT shifted by each glyph's own bbox: shifting
    by bbox top lifts small glyphs like "." to the top of the line.
    """
    total = sum(font.getlength(ch) for ch in text) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += font.getlength(ch) + tracking
    b = draw.textbbox((0, 0), "M", font=font)
    return b[3] - b[1]


def ghost_masks(size):
    """Ghost body + outline masks from the press-kit mark.

    The mark is RGBA: transparent corners must be excluded (converting to
    RGB turns them black and would paint a black square). White pixels are
    the ghost body (plus its star and dot); black pixels are the outline
    (plus sparkle eyes and badge rings). The mark's thick black outer ring
    around the magenta disc is dropped with a radial cutoff so it does not
    draw a big circle on the patch.
    """
    mark = Image.open(MARK).convert("RGBA").resize((size, size), Image.LANCZOS)
    body = Image.new("L", (size, size), 0)
    outl = Image.new("L", (size, size), 0)
    px = mark.load()
    bp, op = body.load(), outl.load()
    cx = cy = size / 2
    cutoff = size * 0.41
    for y in range(size):
        for x in range(size):
            r, g, b, a = px[x, y]
            if a < 128:
                continue
            if math.hypot(x - cx, y - cy) > cutoff:
                continue
            if r > 200 and g > 200 and b > 200:
                bp[x, y] = 255
            elif r < 70 and g < 70 and b < 70:
                op[x, y] = 255
    return body, outl


def palm_tree(draw, base_x, base_y, height, lean=0.0, flip=False):
    top_x = base_x + lean
    top_y = base_y - height
    pts = []
    n = 12
    for i in range(n + 1):
        t = i / n
        x = base_x + (top_x - base_x) * t + math.sin(t * math.pi * 0.5) * lean * 0.25
        y = base_y + (top_y - base_y) * t
        pts.append((x, y))
    draw.line(pts, fill=DENIM_DARK, width=16, joint="curve")
    for k in range(7):
        ang = math.radians(-160 + k * 26)
        if flip:
            ang = math.radians(180) - ang
        length = height * 0.42 * (0.75 + 0.25 * math.cos(k * 1.3))
        blade = []
        steps = 10
        for i in range(steps + 1):
            t = i / steps
            x = top_x + math.cos(ang) * length * t
            y = top_y + math.sin(ang) * length * t + (length * 0.45) * t * t
            blade.append((x, y))
        for i in range(steps, -1, -1):
            t = i / steps
            x = top_x + math.cos(ang) * length * t
            y = top_y + math.sin(ang) * length * t + (length * 0.45) * t * t + 10
            blade.append((x, y))
        draw.polygon(blade, fill=DENIM_DARK)
    draw.ellipse([top_x - 12, top_y + 2, top_x + 2, top_y + 16], fill=DENIM_DARK)
    draw.ellipse([top_x + 2, top_y + 4, top_x + 16, top_y + 18], fill=DENIM_DARK)


def main():
    img = denim_texture(W, H, DENIM)
    draw = ImageDraw.Draw(img, "RGBA")

    # --- title: serif capitals, cream ---
    f_title = ImageFont.truetype(SERIF, 80)
    y = 46
    y += text_center(draw, 512, y, "WAITED 13 YEARS", f_title, CREAM)
    y += 4
    y += text_center(draw, 512, y, "FOR GTA 6", f_title, CREAM)
    # stitched rule under the title
    dashed_line(draw, (212, y + 22), (812, y + 22), STITCH, width=3, dash=10, gap=8)

    # --- patchwork sun (bigger than the patch, so its wedges show) ---
    cx, cy, r = 512, 505, 240
    wedges = [GOLD, CREAM_DIM, DENIM_FADED, GOLD, CREAM, DENIM_FADED,
              GOLD, CREAM_DIM, DENIM_FADED, GOLD, CREAM, DENIM_FADED]
    wedges[2] = ACCENT  # the single orange-red wedge, upper right
    sun = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sun)
    n = len(wedges)
    for i, col in enumerate(wedges):
        a0 = -90 + 360 * i / n
        a1 = -90 + 360 * (i + 1) / n
        sd.pieslice([cx - r, cy - r, cx + r, cy + r], a0, a1, fill=col + (255,))
    img = Image.alpha_composite(img.convert("RGBA"), sun)
    draw = ImageDraw.Draw(img, "RGBA")
    # stitch seams along every wedge boundary + dashed ring
    for i in range(n):
        a = math.radians(-90 + 360 * i / n)
        dashed_line(draw, (cx, cy),
                    (cx + math.cos(a) * r, cy + math.sin(a) * r),
                    STITCH, width=3, dash=9, gap=7)
    dashed_circle(draw, cx, cy, r, STITCH, width=4, dash=13, gap=9)
    draw.ellipse([cx - r - 5, cy - r - 5, cx + r + 5, cy + r + 5],
                 outline=INK, width=5)

    # --- ghost cream patch, sewn over the sun's lower half ---
    # Smaller than the sun, sitting low, so the patchwork shows above it.
    patch = Image.new("RGBA", (380, 380), (0, 0, 0, 0))
    pd = ImageDraw.Draw(patch)
    # frayed edge: short, sparse cream strokes sticking out of the border
    rnd = random.Random(4)
    for side in range(4):
        for t in range(0, 380, 12):
            ln = rnd.randint(3, 6)
            if side == 0:
                pd.line([(t, 18), (t + rnd.randint(-2, 2), 18 - ln)],
                        fill=CREAM_DIM + (255,), width=2)
            elif side == 1:
                pd.line([(362, t), (362 + ln, t + rnd.randint(-2, 2))],
                        fill=CREAM_DIM + (255,), width=2)
            elif side == 2:
                pd.line([(t, 362), (t + rnd.randint(-2, 2), 362 + ln)],
                        fill=CREAM_DIM + (255,), width=2)
            else:
                pd.line([(18, t), (18 - ln, t + rnd.randint(-2, 2))],
                        fill=CREAM_DIM + (255,), width=2)
    pd.rounded_rectangle([18, 18, 362, 362], radius=26, fill=CREAM + (255,),
                         outline=INK + (255,), width=4)
    # dashed stitch border, inset from the edge
    pd.rounded_rectangle([34, 34, 346, 346], radius=18, outline=(90, 84, 70, 255), width=3)
    for t in range(40, 340, 16):  # hand-stitched dashes along the border
        pd.line([(t, 34), (t + 8, 34)], fill=(90, 84, 70, 255), width=3)
        pd.line([(t, 346), (t + 8, 346)], fill=(90, 84, 70, 255), width=3)
        pd.line([(34, t), (34, t + 8)], fill=(90, 84, 70, 255), width=3)
        pd.line([(346, t), (346, t + 8)], fill=(90, 84, 70, 255), width=3)
    # ghost printed tone-on-tone: body a touch darker than the patch,
    # outline in charcoal, so it reads as line work, not a black blob
    gbody, gout = ghost_masks(300)
    body_layer = Image.new("RGBA", (300, 300), CREAM_DIM + (255,))
    patch.paste(body_layer, (40, 30), gbody)
    ink_layer = Image.new("RGBA", (300, 300), INK + (255,))
    patch.paste(ink_layer, (40, 30), gout)
    # white sashiko X stitches at the four corners, straddling the edge
    for (sx, sy) in [(18, 18), (362, 18), (18, 362), (362, 362)]:
        stitch_x(pd, sx, sy, 13, STITCH + (255,), width=5)
    # woven SAMOYZ tab on the patch's lower edge (accent, same one colour)
    f_tab = ImageFont.truetype(MONO, 24)
    tab = Image.new("RGBA", (150, 44), (0, 0, 0, 0))
    td = ImageDraw.Draw(tab)
    td.rounded_rectangle([0, 0, 149, 43], radius=6, fill=ACCENT + (255,))
    td.text((75, 21), "SAMOYZ", font=f_tab, fill=CREAM + (255,), anchor="mm")
    patch.alpha_composite(tab, (115, 318))
    patch = patch.rotate(-4, expand=True, resample=Image.BICUBIC)
    img.paste(patch, (512 - patch.width // 2, 585 - patch.height // 2), patch)
    draw = ImageDraw.Draw(img, "RGBA")

    # --- ground: dark denim below a stitched seam ---
    draw.rectangle([0, 800, W, H], fill=DENIM_DARK)
    dashed_line(draw, (0, 800), (W, 800), STITCH, width=4, dash=14, gap=10)
    palm_tree(draw, 150, H + 8, 340, lean=-28)
    palm_tree(draw, 880, H + 8, 320, lean=26, flip=True)

    # --- bottom label: wide-spaced monospace, like a sewn label ---
    f_mono = ImageFont.truetype(MONO, 52)
    f_small = ImageFont.truetype(MONO, 26)
    y = 824
    y += spaced_text_center(draw, 512, y, "MY AGENT PAID FOR IT", f_mono, CREAM, tracking=7)
    y += 12
    # "ON " cream + "MAKE.FUN" in the single accent (natural baseline
    # positioning, so the "." sits on the baseline, not raised)
    parts = [("ON ", CREAM), ("MAKE.FUN", ACCENT)]
    total = 0
    for text, _ in parts:
        total += sum(f_mono.getlength(ch) for ch in text) + 7 * (len(text) - 1)
    x = 512 - total / 2
    for (text, fill) in parts:
        for ch in text:
            draw.text((x, y), ch, font=f_mono, fill=fill)
            x += f_mono.getlength(ch) + 7
        x -= 7
    # micro label: waited since 2013
    spaced_text_center(draw, 512, 962, "EST. 2013 - STILL WAITING",
                       f_small, DIM_CREAM, tracking=5)

    out = img.convert("RGB")
    out.save("meme-dbwd.png")
    print("saved meme-dbwd.png", out.size)


if __name__ == "__main__":
    main()
