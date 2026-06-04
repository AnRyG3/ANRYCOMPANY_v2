from pathlib import Path
import json
import shutil

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "mammography_series" / "01_compression_reason"
BG_DIR = ASSET_DIR / "generated_backgrounds"
OUT_DIR = ASSET_DIR / "final_text_frames"
CTA = ROOT / "reel_assets" / "common" / "reel_end_card_save.png"

SIZE = (1080, 1920)

TEXTS = [
    ["マンモで", "どうして圧迫するの？"],
    ["痛そうで", "不安になりますよね"],
    ["圧迫には", "大切な理由があります"],
    ["乳房を薄く広げると"],
    ["乳腺の重なりが", "少なくなります"],
    ["小さな変化を", "見つけやすくするためです"],
    ["動きを抑えて", "画像のぶれも減らします"],
    ["被ばくを減らすことにも", "つながります"],
    ["つらいときは", "我慢せず伝えてください"],
    ["理由を知ると", "少し安心につながります"],
    ["検査前の不安を", "安心に変える情報を発信中"],
]

BG_FILES = [
    BG_DIR / "01_exam_room.png",
    BG_DIR / "02_explanation_v2.png",
    BG_DIR / "01_exam_room.png",
    BG_DIR / "03_less_overlap.png",
    BG_DIR / "03_less_overlap.png",
    BG_DIR / "04_less_blur.png",
    BG_DIR / "04_less_blur.png",
    BG_DIR / "05_lower_exposure.png",
    BG_DIR / "02_explanation_v2.png",
    BG_DIR / "06_reassurance_v2.png",
    BG_DIR / "06_reassurance_v2.png",
]

FONT_BOLD = [
    r"C:\Windows\Fonts\YuGothB.ttc",
    r"C:\Windows\Fonts\YuGothM.ttc",
    r"C:\Windows\Fonts\meiryob.ttc",
    r"C:\Windows\Fonts\meiryo.ttc",
]


def choose_font(size):
    for path in FONT_BOLD:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def cover_image(path):
    im = Image.open(path).convert("RGB")
    scale = max(SIZE[0] / im.width, SIZE[1] / im.height)
    new_size = (round(im.width * scale), round(im.height * scale))
    im = im.resize(new_size, Image.Resampling.LANCZOS)
    left = (im.width - SIZE[0]) // 2
    top = (im.height - SIZE[1]) // 2
    return im.crop((left, top, left + SIZE[0], top + SIZE[1]))


def fit_font(draw, lines, max_width, start_size=88, min_size=50):
    for size in range(start_size, min_size - 1, -2):
        font = choose_font(size)
        widths = [
            draw.textbbox((0, 0), line, font=font, stroke_width=3)[2]
            for line in lines
        ]
        if max(widths) <= max_width:
            return font
    return choose_font(min_size)


def draw_center_text(im, lines, index):
    draw = ImageDraw.Draw(im, "RGBA")
    max_width = 940
    y_center = 490
    start_size = 88
    line_gap = 22

    if index in (4, 6, 7, 8, 11):
        start_size = 76
    if index in (4, 5, 6, 7, 8):
        y_center = 390

    font = fit_font(draw, lines, max_width, start_size=start_size)
    bboxes = [draw.textbbox((0, 0), line, font=font, stroke_width=3) for line in lines]
    heights = [box[3] - box[1] for box in bboxes]
    widths = [box[2] - box[0] for box in bboxes]
    total_h = sum(heights) + line_gap * (len(lines) - 1)
    y = y_center - total_h // 2
    text_w = max(widths)
    pad_x, pad_y = 54, 42
    box = (
        (SIZE[0] - text_w) // 2 - pad_x,
        y - pad_y,
        (SIZE[0] + text_w) // 2 + pad_x,
        y + total_h + pad_y,
    )

    shadow = (box[0] + 8, box[1] + 10, box[2] + 8, box[3] + 10)
    draw.rounded_rectangle(shadow, radius=34, fill=(8, 35, 56, 92))
    draw.rounded_rectangle(box, radius=34, fill=(255, 255, 255, 232))

    yy = y
    for line, height, bbox in zip(lines, heights, bboxes):
        x = (SIZE[0] - (bbox[2] - bbox[0])) // 2
        draw.text(
            (x, yy),
            line,
            font=font,
            fill=(18, 58, 88, 255),
            stroke_width=2,
            stroke_fill=(255, 255, 255, 255),
        )
        yy += height + line_gap
    return im


def make_contact_sheet(paths, out_path):
    thumb_w, thumb_h = 270, 480
    label_h = 32
    cols = 6
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (thumb_w * cols, (thumb_h + label_h) * rows), (245, 247, 250))
    font = ImageFont.load_default()
    for idx, path in enumerate(paths):
        im = Image.open(path).convert("RGB")
        im.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), "white")
        tile.paste(im, ((thumb_w - im.width) // 2, 0))
        ImageDraw.Draw(tile).text((8, thumb_h + 9), Path(path).name, fill=(0, 0, 0), font=font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
    sheet.save(out_path)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    for i, (lines, bg_file) in enumerate(zip(TEXTS, BG_FILES), start=1):
        frame = draw_center_text(cover_image(bg_file), lines, i)
        out = OUT_DIR / f"frame_{i:02d}.png"
        frame.save(out)
        outputs.append(out)

    cta_out = OUT_DIR / "frame_12.png"
    shutil.copy2(CTA, cta_out)
    outputs.append(cta_out)

    contact_sheet = ASSET_DIR / "_contact_sheet_final_text_frames.png"
    make_contact_sheet(outputs, contact_sheet)
    make_contact_sheet(sorted(BG_DIR.glob("*.png")), ASSET_DIR / "_contact_sheet_generated_backgrounds.png")

    manifest = {
        "title": "マンモでどうして圧迫するの？",
        "asset_dir": str(ASSET_DIR),
        "final_text_frames": [str(path) for path in outputs],
        "contact_sheet": str(contact_sheet),
        "size": {"width": SIZE[0], "height": SIZE[1]},
        "note": "12-frame reel images. Six generated backgrounds plus common save CTA.",
    }
    (OUT_DIR / "frame_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(contact_sheet)


if __name__ == "__main__":
    main()
