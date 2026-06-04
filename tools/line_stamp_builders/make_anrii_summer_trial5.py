from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
BASE_DIR = ROOT / r"02_LINEスタンプ\あんりぃ_LINEスタンプ制作工場\01_ベース画像\ベース画像_採用候補5枚"
OUT_DIR = ROOT / r"02_LINEスタンプ\あんりぃ_LINEスタンプ制作工場\04_完成画像\夏を感じるスタンプ_あんりぃ40\01_試作5個"
WORK_DIR = OUT_DIR / "work"
PREVIEW = OUT_DIR / "preview_trial5.png"

CANVAS = (370, 320)
FONT_BOLD = Path(r"C:\Windows\Fonts\BIZ-UDGothicB.ttc")
FONT_ROUND = Path(r"C:\Windows\Fonts\YuGothB.ttc")


def load_font(size: int) -> ImageFont.FreeTypeFont:
    path = FONT_ROUND if FONT_ROUND.exists() else FONT_BOLD
    return ImageFont.truetype(str(path), size)


def remove_green_background(img: Image.Image) -> Image.Image:
    img = img.convert("RGBA")
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if g > 150 and r < 120 and b < 140:
                px[x, y] = (r, g, b, 0)
    return img


def remove_white_and_hearts(img: Image.Image) -> Image.Image:
    img = img.convert("RGBA")
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            # Remove the white paper background and pale pastel speckles.
            if r > 238 and g > 235 and b > 230:
                px[x, y] = (r, g, b, 0)
                continue
            # Remove the large pink heart decorations while keeping the dog mostly intact.
            pink = r > 175 and g < 222 and b < 230 and r > g + 22 and r > b + 8
            if pink:
                px[x, y] = (r, g, b, 0)
    return soften_alpha(img)


def remove_white_background(img: Image.Image) -> Image.Image:
    img = img.convert("RGBA")
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if r > 238 and g > 235 and b > 230:
                px[x, y] = (r, g, b, 0)
    return soften_alpha(img)


def remove_lower_pink_props(img: Image.Image) -> Image.Image:
    img = img.convert("RGBA")
    px = img.load()
    limit_y = int(img.height * 0.58)
    for y in range(limit_y, img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            pink = r > 175 and g < 222 and b < 235 and r > g + 18 and r > b + 4
            if pink:
                px[x, y] = (r, g, b, 0)
    return soften_alpha(img)


def soften_alpha(img: Image.Image) -> Image.Image:
    img = img.convert("RGBA")
    r, g, b, a = img.split()
    a = a.filter(ImageFilter.GaussianBlur(0.35))
    return Image.merge("RGBA", (r, g, b, a))


def crop_content(img: Image.Image) -> Image.Image:
    bbox = img.getbbox()
    if bbox is None:
        raise RuntimeError("empty image")
    return img.crop(bbox)


def fit_subject(img: Image.Image, max_w: int, max_h: int) -> Image.Image:
    img = crop_content(img)
    scale = min(max_w / img.width, max_h / img.height)
    size = (max(1, int(img.width * scale)), max(1, int(img.height * scale)))
    return img.resize(size, Image.Resampling.LANCZOS)


def paste_center(canvas: Image.Image, subject: Image.Image, cx: int, cy: int) -> None:
    x = int(cx - subject.width / 2)
    y = int(cy - subject.height / 2)
    canvas.alpha_composite(subject, (x, y))


def shadow(subject: Image.Image, radius: int = 7, opacity: int = 80) -> Image.Image:
    alpha = subject.getchannel("A")
    sh = Image.new("RGBA", subject.size, (74, 45, 32, 0))
    sh.putalpha(alpha.point(lambda v: min(opacity, v)))
    return sh.filter(ImageFilter.GaussianBlur(radius))


def add_text(
    img: Image.Image,
    lines: list[str],
    fill: tuple[int, int, int],
    pos: tuple[int, int],
    max_width: int = 350,
    max_height: int = 84,
    align: str = "center",
) -> None:
    draw = ImageDraw.Draw(img)
    text = "\n".join(lines)
    for size in range(52, 21, -2):
        font = load_font(size)
        bbox = draw.multiline_textbbox((0, 0), text, font=font, stroke_width=5, spacing=-2, align=align)
        if bbox[2] - bbox[0] <= max_width and bbox[3] - bbox[1] <= max_height:
            break
    font = load_font(size)
    bbox = draw.multiline_textbbox((0, 0), text, font=font, stroke_width=5, spacing=-2, align=align)
    tw = bbox[2] - bbox[0]
    x, y = pos
    if align == "center":
        x = x - tw // 2
    draw.multiline_text(
        (x, y),
        text,
        font=font,
        fill=fill,
        stroke_width=5,
        stroke_fill=(255, 255, 255, 255),
        spacing=-2,
        align=align,
    )
    draw.multiline_text(
        (x + 2, y + 4),
        text,
        font=font,
        fill=(92, 54, 35, 80),
        stroke_width=0,
        spacing=-2,
        align=align,
    )


def draw_sun(draw: ImageDraw.ImageDraw, center: tuple[int, int], r: int) -> None:
    cx, cy = center
    for i in range(14):
        ang = math.tau * i / 14
        p1 = (cx + math.cos(ang) * (r + 3), cy + math.sin(ang) * (r + 3))
        p2 = (cx + math.cos(ang) * (r + 16), cy + math.sin(ang) * (r + 16))
        draw.line([p1, p2], fill=(249, 162, 43, 180), width=4)
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 214, 82, 240), outline=(238, 145, 37, 220), width=3)
    draw.ellipse((cx - r + 6, cy - r + 6, cx + r - 10, cy + r - 12), fill=(255, 237, 138, 115))


def draw_heat(draw: ImageDraw.ImageDraw) -> None:
    for x, y in [(52, 128), (86, 178), (303, 122), (329, 172)]:
        pts = []
        for i in range(22):
            yy = y + i * 3
            xx = x + math.sin(i * 0.7) * 5
            pts.append((xx, yy))
        draw.line(pts, fill=(245, 136, 50, 120), width=3)


def draw_sweat(draw: ImageDraw.ImageDraw, pts: list[tuple[int, int]], color=(89, 186, 231, 230)) -> None:
    for x, y in pts:
        draw.ellipse((x - 5, y + 5, x + 7, y + 19), fill=color, outline=(255, 255, 255, 220), width=2)
        draw.polygon([(x - 5, y + 10), (x + 1, y - 4), (x + 7, y + 10)], fill=color)


def draw_cloud(draw: ImageDraw.ImageDraw, x: int, y: int, scale: float = 1.0) -> None:
    col = (255, 255, 255, 235)
    edge = (108, 190, 225, 120)
    parts = [(0, 20, 46), (35, 4, 58), (78, 22, 42), (107, 30, 30)]
    for dx, dy, rr in parts:
        rr = int(rr * scale)
        draw.ellipse((x + dx - rr, y + dy - rr, x + dx + rr, y + dy + rr), fill=col, outline=edge, width=2)


def draw_summer_sky(draw: ImageDraw.ImageDraw) -> None:
    draw_cloud(draw, 58, 66, 0.55)
    draw_cloud(draw, 235, 58, 0.43)
    for x, y, rr in [(306, 94, 14), (334, 117, 9), (47, 115, 8)]:
        draw.ellipse((x - rr, y - rr, x + rr, y + rr), outline=(101, 188, 223, 150), width=2)
    for x, y in [(48, 206), (74, 218), (104, 211)]:
        draw.arc((x, y, x + 58, y + 18), 185, 350, fill=(70, 176, 215, 135), width=4)


def draw_straw_hat(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    draw.ellipse((x - 54, y + 10, x + 54, y + 32), fill=(214, 166, 80, 230), outline=(125, 88, 42, 170), width=3)
    draw.pieslice((x - 36, y - 25, x + 36, y + 35), 180, 360, fill=(235, 191, 101, 240), outline=(126, 90, 43, 150), width=3)
    draw.arc((x - 35, y - 17, x + 35, y + 43), 200, 340, fill=(174, 116, 58, 190), width=3)
    draw.line((x - 34, y + 13, x + 34, y + 13), fill=(104, 158, 117, 230), width=6)
    for off in [-28, -12, 4, 20]:
        draw.arc((x + off, y - 6, x + off + 28, y + 30), 200, 335, fill=(151, 103, 47, 90), width=2)


def draw_sparkles(draw: ImageDraw.ImageDraw, pts: list[tuple[int, int]], color=(255, 214, 85, 230)) -> None:
    for x, y in pts:
        draw.polygon([(x, y - 9), (x + 4, y - 2), (x + 11, y), (x + 4, y + 3), (x, y + 11), (x - 4, y + 3), (x - 11, y), (x - 4, y - 2)], fill=color)


def draw_splash(draw: ImageDraw.ImageDraw, pts: list[tuple[int, int]]) -> None:
    for x, y in pts:
        draw.ellipse((x - 9, y - 7, x + 9, y + 7), fill=(105, 202, 236, 145), outline=(255, 255, 255, 180), width=2)
    for x, y in [(35, 208), (58, 190), (325, 191), (338, 218)]:
        draw.arc((x, y, x + 55, y + 22), 190, 350, fill=(68, 179, 220, 170), width=5)


def draw_drink(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    draw.rounded_rectangle((x - 4, y - 4, x + 53, y + 86), radius=13, fill=(255, 255, 255, 170))
    draw.rounded_rectangle((x, y, x + 45, y + 76), radius=10, fill=(145, 221, 240, 230), outline=(255, 255, 255, 255), width=4)
    draw.rectangle((x + 5, y + 36, x + 40, y + 70), fill=(65, 178, 219, 230))
    draw.rectangle((x + 5, y + 54, x + 40, y + 70), fill=(68, 145, 220, 135))
    draw.ellipse((x + 8, y + 44, x + 19, y + 55), fill=(255, 255, 255, 185))
    draw.line((x + 28, y - 20, x + 39, y + 50), fill=(246, 128, 126, 220), width=4)
    draw.polygon([(x + 34, y + 7), (x + 61, y + 19), (x + 37, y + 29)], fill=(255, 218, 88, 230), outline=(255, 255, 255, 230))
    draw.ellipse((x + 5, y + 16, x + 40, y + 34), fill=(255, 255, 255, 120))


def draw_bottle(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    draw.rounded_rectangle((x - 5, y - 5, x + 67, y + 118), radius=22, fill=(255, 255, 255, 145))
    draw.rounded_rectangle((x + 15, y, x + 46, y + 20), radius=6, fill=(154, 215, 247, 245), outline=(255, 255, 255, 255), width=3)
    draw.rounded_rectangle((x, y + 18, x + 62, y + 112), radius=17, fill=(167, 222, 246, 215), outline=(255, 255, 255, 255), width=4)
    draw.rounded_rectangle((x + 7, y + 53, x + 55, y + 80), radius=8, fill=(86, 180, 224, 230))
    draw.text((x + 15, y + 54), "H2O", font=load_font(16), fill=(255, 255, 255, 245))
    for ox, oy in [(11, 28), (41, 33), (28, 92)]:
        draw.ellipse((x + ox, y + oy, x + ox + 8, y + oy + 8), fill=(255, 255, 255, 160))


def draw_wind(draw: ImageDraw.ImageDraw, start_x: int, color=(104, 195, 232, 170)) -> None:
    for i, y in enumerate([96, 132, 170, 208]):
        pts = []
        for t in range(80):
            x = start_x + t * 2
            yy = y + math.sin(t * 0.16 + i) * 8
            pts.append((x, yy))
        draw.line(pts, fill=color, width=5)
        draw.line(pts, fill=(255, 255, 255, 155), width=2)


def draw_fan(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    draw.ellipse((x, y, x + 76, y + 76), fill=(214, 245, 250, 225), outline=(84, 181, 212, 210), width=4)
    cx, cy = x + 38, y + 38
    for ang in [0, 120, 240]:
        rad = math.radians(ang)
        p1 = (cx + math.cos(rad) * 6, cy + math.sin(rad) * 6)
        p2 = (cx + math.cos(rad + 0.55) * 31, cy + math.sin(rad + 0.55) * 31)
        p3 = (cx + math.cos(rad - 0.55) * 31, cy + math.sin(rad - 0.55) * 31)
        draw.polygon([p1, p2, p3], fill=(116, 203, 230, 160))
    draw.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=(75, 170, 205, 220))
    draw.rounded_rectangle((x + 31, y + 76, x + 45, y + 126), radius=5, fill=(116, 203, 230, 210))
    draw.ellipse((x + 18, y + 118, x + 58, y + 132), fill=(116, 203, 230, 210))


def crop_upper_face(img: Image.Image) -> Image.Image:
    # The old heart-base art has a large prop in the lower body. For summer trial
    # stickers, keep the recognizable face and collar while removing the prop-heavy area.
    w, h = img.size
    return img.crop((0, 0, w, int(h * 0.72)))


def make_item(base_name: str, out_name: str, text_lines: list[str], subject_box: tuple[int, int], center: tuple[int, int], draw_extra, text_fill, text_pos, text_w=350, upper_face=False) -> Path:
    base = Image.open(BASE_DIR / base_name)
    if "real_base" in base_name:
        subject = remove_green_background(base)
    elif upper_face:
        # Avoid destructive pink removal on the old art. Crop around the face so
        # heart props fall outside the sticker instead.
        w, h = base.size
        base = base.crop((int(w * 0.16), 0, int(w * 0.89), int(h * 0.50)))
        subject = remove_lower_pink_props(remove_white_background(base))
    else:
        subject = remove_white_and_hearts(base)
    subject = fit_subject(subject, subject_box[0], subject_box[1])

    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    deco = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(deco)
    draw_extra(draw)
    canvas.alpha_composite(deco)

    sh = shadow(subject)
    paste_center(canvas, sh, center[0] + 3, center[1] + 5)
    paste_center(canvas, subject, center[0], center[1])
    add_text(canvas, text_lines, text_fill, text_pos, max_width=text_w)

    out = OUT_DIR / out_name
    canvas.save(out)
    return out


def make_preview(paths: list[Path]) -> None:
    cell = (260, 245)
    sheet = Image.new("RGB", (cell[0] * 3, cell[1] * 2), (248, 248, 248))
    for i, p in enumerate(paths):
        img = Image.open(p).convert("RGBA")
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        bg.alpha_composite(img)
        bg.thumbnail((235, 220), Image.Resampling.LANCZOS)
        x = (i % 3) * cell[0] + (cell[0] - bg.width) // 2
        y = (i // 3) * cell[1] + (cell[1] - bg.height) // 2
        sheet.paste(bg.convert("RGB"), (x, y))
    sheet.save(PREVIEW, quality=94)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(exist_ok=True)
    paths = []

    paths.append(
        make_item(
            "03_real_base_front_sit_necklace.png",
            "trial_01_atsui.png",
            ["あつい〜"],
            (260, 226),
            (190, 202),
            lambda d: (draw_sun(d, (302, 85), 31), draw_heat(d), draw_sweat(d, [(92, 112), (286, 143), (310, 174)])),
            (236, 111, 45, 255),
            (178, 14),
        )
    )
    paths.append(
        make_item(
            "05_real_base_standing_plain.png",
            "trial_02_natsudane.png",
            ["夏だね"],
            (215, 218),
            (191, 206),
            lambda d: (draw_summer_sky(d), draw_straw_hat(d, 245, 104)),
            (62, 166, 214, 255),
            (185, 12),
        )
    )
    paths.append(
        make_item(
            "04_real_base_threequarter_tongue_necklace.png",
            "trial_03_otsukare_summer.png",
            ["おつかれ", "サマー"],
            (218, 215),
            (178, 205),
            lambda d: (draw_drink(d, 292, 181), draw_splash(d, [(284, 176), (333, 166), (315, 246)]), draw_sparkles(d, [(279, 90), (326, 128), (305, 154), (262, 190)], (255, 212, 75, 230))),
            (64, 157, 211, 255),
            (171, 8),
            text_w=335,
        )
    )
    paths.append(
        make_item(
            "03_real_base_front_sit_necklace.png",
            "trial_04_suibun.png",
            ["水分", "とってね"],
            (238, 202),
            (178, 212),
            lambda d: (draw_bottle(d, 286, 169), draw_splash(d, [(48, 202), (88, 188), (316, 151)]), draw_wind(d, 25, (98, 196, 232, 130))),
            (57, 151, 214, 255),
            (167, 8),
            text_w=326,
        )
    )
    paths.append(
        make_item(
            "01_old_base_heart_black_necklace.png",
            "trial_05_suzundemasu.png",
            ["涼んでます"],
            (260, 206),
            (190, 212),
            lambda d: (draw_fan(d, 282, 170), draw_wind(d, 18, (91, 188, 222, 190)), draw_sparkles(d, [(62, 80), (315, 92), (319, 221), (67, 228)], (183, 236, 243, 210))),
            (63, 170, 207, 255),
            (185, 12),
            text_w=348,
            upper_face=True,
        )
    )
    make_preview(paths)
    print(str(PREVIEW))
    for p in paths:
        print(str(p))


if __name__ == "__main__":
    main()
