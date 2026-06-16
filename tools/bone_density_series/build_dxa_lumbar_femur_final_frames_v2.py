from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "bone_density_series" / "03_dxa_lumbar_femur_reason"
BG_DIR = ASSET_DIR / "background_frames"
GEN_DIR = ASSET_DIR / "generated_backgrounds"
OUT_DIR = ASSET_DIR / "final_text_frames_v2"
SIZE = (1080, 1920)

FRAMES = [
    (1, 1, ["DXA法って", "どんな検査？"]),
    (2, 2, ["骨密度検査には", "いくつか種類がある"]),
    (3, 2, ["2種類のX線で", "骨密度を測る検査"]),
    (4, 6, ["骨粗しょう症の診断で", "よく使われる"]),
    (5, 1, ["よく見る場所は", "腰の骨"]),
    (6, 1, ["もう1つは", "太ももの付け根"]),
    (7, 6, ["なぜそこ？", "骨折すると生活への影響が", "大きい場所だから"]),
    (8, 7, ["かかとの検査と", "優劣ではない"]),
    (9, 8, ["目的によって", "見る場所が違う"]),
    (10, 8, ["数字で結果が出るので", "経過観察にも使いやすい"]),
    (11, 10, ["検査の不安を減らす投稿を", "続けています"]),
]

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\YuGothB.ttc",
    r"C:\Windows\Fonts\meiryob.ttc",
    r"C:\Windows\Fonts\YuGothM.ttc",
    r"C:\Windows\Fonts\meiryo.ttc",
]


def choose_font(size):
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def fit_font(draw, lines, max_width, start_size, min_size):
    size = start_size
    while size >= min_size:
        font = choose_font(size)
        widths = [draw.textbbox((0, 0), line, font=font, stroke_width=3)[2] for line in lines]
        if max(widths) <= max_width:
            return font
        size -= 3
    return choose_font(min_size)


def label_y(frame_number):
    if frame_number in {4, 7, 10, 11}:
        return 330
    return 310


def draw_soft_ellipse(draw, box, color, outline, width=8):
    x1, y1, x2, y2 = box
    for expand, alpha in [(44, 28), (28, 42), (14, 58)]:
        draw.ellipse(
            (x1 - expand, y1 - expand, x2 + expand, y2 + expand),
            fill=(*color[:3], alpha),
        )
    draw.ellipse(box, outline=outline, width=width)


def add_dxa_beams(frame):
    im = frame.convert("RGBA")
    overlay = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    beam_origin = (758, 914)
    draw.polygon(
        [beam_origin, (560, 1228), (624, 1248)],
        fill=(73, 171, 190, 74),
    )
    draw.polygon(
        [(beam_origin[0] + 10, beam_origin[1] + 2), (618, 1246), (690, 1260)],
        fill=(180, 140, 216, 66),
    )
    draw.line([beam_origin, (592, 1238)], fill=(38, 128, 150, 152), width=7)
    draw.line([(beam_origin[0] + 10, beam_origin[1] + 2), (654, 1254)], fill=(126, 90, 180, 138), width=7)
    draw.ellipse((520, 1188, 708, 1308), outline=(34, 129, 149, 215), width=8)
    im.alpha_composite(overlay)
    return im.convert("RGB")


def add_lumbar_highlight(frame):
    im = frame.convert("RGBA")
    overlay = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    draw_soft_ellipse(
        draw,
        (570, 1118, 748, 1276),
        color=(67, 171, 188, 255),
        outline=(24, 118, 142, 232),
        width=9,
    )
    spine_x = 660
    for i in range(5):
        y = 1162 + i * 20
        draw.rounded_rectangle(
            (spine_x - 18, y, spine_x + 18, y + 14),
            radius=6,
            fill=(255, 255, 255, 210),
            outline=(24, 118, 142, 225),
            width=3,
        )
    draw.line((spine_x, 1158, spine_x, 1262), fill=(24, 118, 142, 220), width=5)
    im.alpha_composite(overlay)
    return im.convert("RGB")


def add_hip_highlight(frame):
    im = frame.convert("RGBA")
    overlay = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    draw_soft_ellipse(
        draw,
        (505, 1218, 680, 1392),
        color=(83, 180, 166, 255),
        outline=(22, 124, 137, 232),
        width=9,
    )
    draw.ellipse((556, 1270, 620, 1334), fill=(255, 255, 255, 210), outline=(22, 124, 137, 225), width=5)
    draw.line((590, 1324, 660, 1404), fill=(22, 124, 137, 220), width=9)
    draw.line((564, 1316, 514, 1378), fill=(22, 124, 137, 150), width=6)
    im.alpha_composite(overlay)
    return im.convert("RGB")


def cover_to_size(path):
    img = Image.open(path).convert("RGB")
    iw, ih = img.size
    scale = max(SIZE[0] / iw, SIZE[1] / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - SIZE[0]) // 2
    top = (nh - SIZE[1]) // 2
    return img.crop((left, top, left + SIZE[0], top + SIZE[1]))


def frame_source(frame_number, bg_number):
    if frame_number == 5:
        return cover_to_size(GEN_DIR / "slide05_lumbar_spine_approved.png")
    if frame_number == 6:
        return cover_to_size(GEN_DIR / "slide06_proximal_femur_approved.png")
    return Image.open(BG_DIR / f"bg_{bg_number:02d}.png").convert("RGB")


def enhance_frame(frame, frame_number):
    if frame_number == 3:
        return add_dxa_beams(frame)
    return frame


def draw_label(frame, lines, frame_number):
    im = frame.convert("RGBA")
    draw = ImageDraw.Draw(im, "RGBA")
    font = fit_font(draw, lines, max_width=910, start_size=86, min_size=46)
    gap = 20
    metrics = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=4)
        metrics.append((bbox[2] - bbox[0], bbox[3] - bbox[1]))

    total_h = sum(h for _, h in metrics) + gap * (len(lines) - 1)
    y = label_y(frame_number) - total_h // 2
    text_w = max(w for w, _ in metrics)
    pad_x = 52
    pad_y = 36
    box = (
        (SIZE[0] - text_w) // 2 - pad_x,
        y - pad_y,
        (SIZE[0] + text_w) // 2 + pad_x,
        y + total_h + pad_y,
    )
    draw.rounded_rectangle(box, radius=30, fill=(255, 255, 255, 232))

    yy = y
    for line, (_, height) in zip(lines, metrics):
        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=4)
        x = (SIZE[0] - (bbox[2] - bbox[0])) // 2
        draw.text(
            (x, yy),
            line,
            font=font,
            fill=(16, 58, 88, 255),
            stroke_width=3,
            stroke_fill=(255, 255, 255, 255),
        )
        yy += height + gap

    draw.rounded_rectangle((44, 48, 182, 98), radius=22, fill=(18, 84, 110, 210))
    draw.text((76, 60), f"{frame_number:02d}", font=choose_font(28), fill=(255, 255, 255, 255))
    return im.convert("RGB")


def make_contact_sheet(paths):
    thumb_w, thumb_h = 270, 480
    label_h = 32
    cols = 6
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (thumb_w * cols, (thumb_h + label_h) * rows), (245, 247, 250))
    font = ImageFont.load_default()
    draw = ImageDraw.Draw(sheet)
    for idx, path in enumerate(paths):
        im = Image.open(path).convert("RGB")
        im = im.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (idx % cols) * thumb_w
        y = (idx // cols) * (thumb_h + label_h)
        sheet.paste(im, (x, y))
        draw.text((x + 8, y + thumb_h + 9), Path(path).name, fill=(0, 0, 0), font=font)
    sheet.save(ASSET_DIR / "_contact_sheet_final_text_frames_v2.png", quality=95)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    for frame_number, bg_number, lines in FRAMES:
        frame = frame_source(frame_number, bg_number)
        frame = enhance_frame(frame, frame_number)
        out = OUT_DIR / f"frame_{frame_number:02d}.png"
        draw_label(frame, lines, frame_number).save(out, quality=95)
        outputs.append(out)

    make_contact_sheet(outputs)
    manifest = {
        "title": "DXA法って何？なぜ腰と太ももの付け根で測るの？",
        "asset_dir": str(ASSET_DIR),
        "background_dir": str(BG_DIR),
        "final_text_frames": [str(path) for path in outputs],
        "contact_sheet": str(ASSET_DIR / "_contact_sheet_final_text_frames_v2.png"),
        "size": {"width": SIZE[0], "height": SIZE[1]},
        "note": "承認済み台本に合わせた11枚構成。音声・動画生成は未実施。",
    }
    (OUT_DIR / "frame_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(ASSET_DIR / "_contact_sheet_final_text_frames_v2.png")


if __name__ == "__main__":
    main()
