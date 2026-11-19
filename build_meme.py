#!/usr/bin/env python3
"""Build the GTA 6 meme for make.fun bounty gta6-meme-x-01.

Concept: Vice City / Leonida sunset. The make.fun ghost mark IS the sun
in the sky (worked into the scene, not a sticker), with a dark skyline and
palm silhouettes. Text: "WAITED 13 YEARS FOR GTA 6" / "MY AGENT PAID FOR
IT ON MAKE.FUN". The joke: I waited 13 years; my agent earned/paid for
the game on make.fun. Output 1024x1024 PNG, readable at 480x480.
"""
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1024, 1024
BLACK = (20, 10, 18)          # near-black for silhouettes / ground
MAGENTA = (196, 28, 131)      # make.fun brand #C41C83
PINK = (255, 136, 196)        # light pink for MAKE.FUN on dark
WHITE = (255, 255, 255)
ORANGE = (247, 183, 51)

FONT_BLACK = "/usr/share/fonts/truetype/noto/NotoSansDisplay-Black.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
MARK = "press-kit/make-fun-press-kit/mark-1024.png"


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def sky_gradient(w, h):
    """Vertical sunset gradient through colour stops."""
    stops = [
        (0.00, (22, 10, 36)),    # deep purple
        (0.30, (74, 21, 80)),    # purple
        (0.55, (160, 30, 110)),  # magenta
        (0.75, (232, 93, 61)),   # orange-red
        (1.00, (247, 183, 51)),  # orange
    ]
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        t = y / (h - 1)
        for i in range(len(stops) - 1):
            t0, c0 = stops[i]
            t1, c1 = stops[i + 1]
            if t0 <= t <= t1:
                f = 0 if t1 == t0 else (t - t0) / (t1 - t0)
                col = lerp(c0, c1, f)
                break
        else:
            col = stops[-1][1]
        for x in range(w):
            px[x, y] = col
    return img


def draw_text_center(draw, cx, y, text, font, fill, stroke=0, stroke_fill=(0, 0, 0)):
    """Draw text centred on cx at top y; return the height used."""
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text((cx - w / 2 - bbox[0], y - bbox[1]), text, font=font,
              fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return h


def draw_two_tone_center(draw, cx, y, parts, font, stroke=0, stroke_fill=(0, 0, 0)):
    """Draw [(text, fill), ...] as one centred line."""
    widths = []
    total = 0
    heights = []
    for text, _ in parts:
        b = draw.textbbox((0, 0), text, font=font, stroke_width=stroke)
        widths.append(b[2] - b[0])
        heights.append(b[3] - b[1])
        total += b[2] - b[0]
    x = cx - total / 2
    h = max(heights)
    for (text, fill), w in zip(parts, widths):
        b = draw.textbbox((0, 0), text, font=font, stroke_width=stroke)
        draw.text((x - b[0], y - b[1]), text, font=font, fill=fill,
                  stroke_width=stroke, stroke_fill=stroke_fill)
        x += w
    return h


def palm_tree(draw, base_x, base_y, height, lean=0.0, flip=False):
    """Draw a palm silhouette: curved trunk + drooping fronds.
    lean is a horizontal offset in px of the crown from the base."""
    # trunk: a series of short thick segments curving with lean
    top_x = base_x + lean
    top_y = base_y - height
    pts = []
    n = 12
    for i in range(n + 1):
        t = i / n
        x = base_x + (top_x - base_x) * t + math.sin(t * math.pi * 0.5) * lean * 0.25
        y = base_y + (top_y - base_y) * t
        pts.append((x, y))
    draw.line(pts, fill=BLACK, width=14, joint="curve")
    # fronds: 7 curved blades radiating from the crown
    for k in range(7):
        ang = math.radians(-160 + k * 26)  # spread over the top
        if flip:
            ang = math.radians(180) - ang
        length = height * 0.42 * (0.75 + 0.25 * math.cos(k * 1.3))
        # blade as a filled polygon along a drooping curve
        blade = []
        steps = 10
        for i in range(steps + 1):
            t = i / steps
            # droop: y bends downward as t grows
            x = top_x + math.cos(ang) * length * t
            y = top_y + math.sin(ang) * length * t + (length * 0.45) * t * t
            blade.append((x, y))
        for i in range(steps, -1, -1):
            t = i / steps
            x = top_x + math.cos(ang) * length * t
            y = top_y + math.sin(ang) * length * t + (length * 0.45) * t * t + 9
            blade.append((x, y))
        draw.polygon(blade, fill=BLACK)
    # coconuts
    draw.ellipse([top_x - 12, top_y + 2, top_x + 2, top_y + 16], fill=BLACK)
    draw.ellipse([top_x + 2, top_y + 4, top_x + 16, top_y + 18], fill=BLACK)


def main():
    img = sky_gradient(W, H)
    draw = ImageDraw.Draw(img, "RGBA")

    # stars in the upper sky
    import random
    random.seed(6)
    for _ in range(60):
        x = random.randint(20, W - 20)
        y = random.randint(10, 240)
        r = random.choice([1, 1, 2])
        a = random.randint(90, 200)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, a))

    # glow behind the sun
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([512 - 300, 480 - 300, 512 + 300, 480 + 300], fill=(255, 120, 180, 90))
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    img = Image.alpha_composite(img.convert("RGBA"), glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # the sun IS the make.fun ghost mark
    mark = Image.open(MARK).convert("RGBA").resize((400, 400), Image.LANCZOS)
    img.paste(mark, (512 - 200, 480 - 200), mark)
    draw = ImageDraw.Draw(img, "RGBA")

    # distant skyline on the horizon (y 740-804)
    horizon = 804
    buildings = [
        (0, 40, 770), (60, 70, 752), (150, 55, 762), (230, 90, 742),
        (340, 60, 758), (420, 80, 746), (520, 50, 766), (590, 95, 740),
        (700, 65, 756), (780, 85, 744), (880, 55, 764), (950, 74, 750),
    ]
    for x, w, top in buildings:
        draw.rectangle([x, top, x + w, horizon], fill=BLACK)
    # a couple of antennae
    draw.line([(95, 752), (95, 726)], fill=BLACK, width=4)
    draw.line([(637, 740), (637, 712)], fill=BLACK, width=4)
    draw.ellipse([631, 706, 643, 718], fill=(255, 80, 80, 255))
    # lit windows in the skyline
    random.seed(19)
    for _ in range(40):
        x = random.randint(8, W - 14)
        y = random.randint(748, 798)
        if random.random() < 0.7:
            draw.rectangle([x, y, x + 4, y + 5], fill=(255, 200, 90, 220))

    # solid dark ground
    draw.rectangle([0, horizon, W, H], fill=BLACK)

    # palm silhouettes framing the scene (on the ground, fronds in the sky)
    palm_tree(draw, 130, H + 6, 360, lean=-30)
    palm_tree(draw, 900, H + 6, 330, lean=28, flip=True)

    # --- text ---
    f_big = ImageFont.truetype(FONT_BLACK, 96)
    f_mid = ImageFont.truetype(FONT_BLACK, 68)

    y = 46
    y += draw_text_center(draw, 512, y, "WAITED 13 YEARS", f_big, WHITE, stroke=7)
    y += 6
    y += draw_text_center(draw, 512, y, "FOR GTA 6", f_big, WHITE, stroke=7)

    y = 838
    y += draw_text_center(draw, 512, y, "MY AGENT PAID FOR IT", f_mid, WHITE, stroke=5)
    y += 10
    y += draw_two_tone_center(draw, 512, y,
                              [("ON ", WHITE), ("MAKE.FUN", PINK)],
                              f_mid, stroke=5)

    out = img.convert("RGB")
    out.save("meme.png")
    out.save("/home/hatch/workspace/makefun/gta6-meme-x-01-meme.png")
    print("saved meme.png", out.size)


if __name__ == "__main__":
    main()
