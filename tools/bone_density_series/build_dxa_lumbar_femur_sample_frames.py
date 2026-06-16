from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "bone_density_series" / "03_dxa_lumbar_femur_reason"
BG_DIR = ASSET_DIR / "background_frames"
OUT_DIR = ASSET_DIR / "sample_review_frames"
SIZE = (1080, 1920)

SAMPLES = [
    (1, ["DXA法って", "どんな検査？"]),
    (2, ["2種類のX線で", "骨密度を測る検査"]),
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


def draw_label(frame, lines, sample_number):
    im = frame.convert("RGBA")
    draw = ImageDraw.Draw(im, "RGBA")
    font = fit_font(draw, lines, max_width=890, start_size=88, min_size=48)
    gap = 22
    metrics = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=4)
        metrics.append((bbox[2] - bbox[0], bbox[3] - bbox[1]))

    total_h = sum(h for _, h in metrics) + gap * (len(lines) - 1)
    y = 310 - total_h // 2
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
    draw.text((76, 60), f"{sample_number:02d}", font=choose_font(28), fill=(255, 255, 255, 255))
    return im.convert("RGB")


def make_contact_sheet(paths):
    thumb_w, thumb_h = 270, 480
    sheet = Image.new("RGB", (thumb_w * len(paths), thumb_h), (245, 247, 250))
    for idx, path in enumerate(paths):
        im = Image.open(path).convert("RGB")
        im = im.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        sheet.paste(im, (idx * thumb_w, 0))
    sheet.save(OUT_DIR / "_contact_sheet_sample_review.png", quality=95)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    for sample_number, lines in SAMPLES:
        bg_path = BG_DIR / f"bg_{sample_number:02d}.png"
        frame = Image.open(bg_path).convert("RGB")
        out = OUT_DIR / f"sample_{sample_number:02d}.png"
        draw_label(frame, lines, sample_number).save(out, quality=95)
        outputs.append(out)

    make_contact_sheet(outputs)
    manifest = {
        "purpose": "DXA法シリーズ確認用サンプル。既存完成候補は上書きしない。",
        "samples": [str(path) for path in outputs],
        "contact_sheet": str(OUT_DIR / "_contact_sheet_sample_review.png"),
        "size": {"width": SIZE[0], "height": SIZE[1]},
    }
    (OUT_DIR / "sample_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(OUT_DIR / "_contact_sheet_sample_review.png")


if __name__ == "__main__":
    main()
