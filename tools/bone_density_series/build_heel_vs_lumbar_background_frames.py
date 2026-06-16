from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[2]
SERIES = ROOT / "reel_assets" / "bone_density_series"
SRC1 = SERIES / "01_heel_ultrasound_reason"
SRC2 = SERIES / "02_heel_vs_lumbar" / "preview_backgrounds"
COMMON = ROOT / "reel_assets" / "common"
OUT = SERIES / "02_heel_vs_lumbar" / "background_frames"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1920


def cover(path: Path, zoom=1.0, x_bias=0.5, y_bias=0.5) -> Image.Image:
    img = Image.open(path).convert("RGB")
    iw, ih = img.size
    scale = max(W / iw, H / ih) * zoom
    nw, nh = int(iw * scale), int(ih * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = int((nw - W) * x_bias)
    top = int((nh - H) * y_bias)
    left = max(0, min(left, nw - W))
    top = max(0, min(top, nh - H))
    return img.crop((left, top, left + W, top + H))


def fit(path: Path, bg=(248, 252, 250), max_w=980, max_h=1720) -> Image.Image:
    base = Image.new("RGB", (W, H), bg)
    img = Image.open(path).convert("RGB")
    iw, ih = img.size
    scale = min(max_w / iw, max_h / ih)
    img = img.resize((int(iw * scale), int(ih * scale)), Image.Resampling.LANCZOS)
    x = (W - img.width) // 2
    y = (H - img.height) // 2
    base.paste(img, (x, y))
    return base


def tint(img: Image.Image, alpha=22) -> Image.Image:
    overlay = Image.new("RGBA", (W, H), (255, 255, 255, alpha))
    out = img.convert("RGBA")
    out.alpha_composite(overlay)
    return out.convert("RGB")


def rounded_shadow(draw_base: Image.Image, box, radius=36):
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(shadow)
    x1, y1, x2, y2 = box
    d.rounded_rectangle((x1 + 0, y1 + 20, x2, y2 + 20), radius=radius, fill=(80, 100, 100, 45))
    shadow = shadow.filter(ImageFilter.GaussianBlur(22))
    draw_base.alpha_composite(shadow)


def split_compare(left_path: Path, right_path: Path, left_bias=0.5, right_bias=0.5) -> Image.Image:
    base = Image.new("RGBA", (W, H), (248, 252, 250, 255))
    d = ImageDraw.Draw(base)
    for y in range(H):
        c = int(250 - y * 8 / H)
        d.line((0, y, W, y), fill=(c, min(255, c + 3), min(255, c + 2), 255))

    card1 = (70, 755, 510, 1390)
    card2 = (570, 755, 1010, 1390)
    rounded_shadow(base, card1)
    rounded_shadow(base, card2)
    d.rounded_rectangle(card1, radius=42, fill=(255, 255, 255, 255))
    d.rounded_rectangle(card2, radius=42, fill=(255, 255, 255, 255))

    left = cover(left_path, zoom=1.23, x_bias=left_bias, y_bias=0.75).resize((420, 600), Image.Resampling.LANCZOS)
    right = cover(right_path, zoom=1.15, x_bias=right_bias, y_bias=0.74).resize((420, 600), Image.Resampling.LANCZOS)

    mask = Image.new("L", (420, 600), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((0, 0, 420, 600), radius=34, fill=255)
    base.paste(left.convert("RGBA"), (80, 772), mask)
    base.paste(right.convert("RGBA"), (580, 772), mask)

    d.line((540, 805, 540, 1365), fill=(204, 222, 221, 255), width=4)
    d.ellipse((506, 1054, 574, 1122), fill=(184, 215, 218, 255))
    d.line((524, 1088, 556, 1088), fill=(255, 255, 255, 255), width=6)
    d.line((540, 1072, 540, 1104), fill=(255, 255, 255, 255), width=6)
    return base.convert("RGB")


def save_frame(n: int, img: Image.Image):
    img.save(OUT / f"bg_{n:02d}.png", quality=95)


def main():
    heel_full = SRC2 / "preview_03_health_check_heel_ultrasound.png"
    heel_close = SRC2 / "preview_04_heel_ultrasound_closeup.png"
    dxa = SRC2 / "adopted_07_dxa_horizon_reference_no_window.png"

    save_frame(1, cover(heel_full, zoom=1.0, x_bias=0.50, y_bias=0.50))
    save_frame(2, tint(cover(SRC1 / "bg_04_result_explanation_no_logo.png", zoom=1.0, x_bias=0.50, y_bias=0.50), 10))
    save_frame(3, cover(heel_full, zoom=1.0, x_bias=0.50, y_bias=0.50))
    save_frame(4, cover(heel_close, zoom=1.0, x_bias=0.50, y_bias=0.50))
    save_frame(5, cover(SRC1 / "bg_07_followup_exam_consult_no_logo.png", zoom=1.0, x_bias=0.50, y_bias=0.50))
    save_frame(6, tint(cover(SRC1 / "bg_04_result_explanation_no_logo.png", zoom=1.03, x_bias=0.50, y_bias=0.55), 18))
    save_frame(7, cover(dxa, zoom=1.0, x_bias=0.50, y_bias=0.50))
    save_frame(8, cover(SRC1 / "bg_05_easy_to_measure_heel_no_logo.png", zoom=1.0, x_bias=0.50, y_bias=0.50))
    save_frame(9, cover(dxa, zoom=1.12, x_bias=0.50, y_bias=0.58))
    save_frame(10, split_compare(heel_close, dxa, left_bias=0.55, right_bias=0.45))
    save_frame(11, tint(cover(SRC1 / "bg_08_reassuring_save_cta_no_logo.png", zoom=1.0, x_bias=0.50, y_bias=0.50), 8))
    save_frame(12, tint(cover(SRC1 / "bg_08_reassuring_save_cta_no_logo.png", zoom=1.0, x_bias=0.50, y_bias=0.50), 8))

    sheet = Image.new("RGB", (W * 4, H * 3), (245, 248, 247))
    for i in range(1, 13):
        img = Image.open(OUT / f"bg_{i:02d}.png").convert("RGB")
        img = img.resize((W, H), Image.Resampling.LANCZOS)
        x = ((i - 1) % 4) * W
        y = ((i - 1) // 4) * H
        sheet.paste(img, (x, y))
    sheet = sheet.resize((1440, 1920), Image.Resampling.LANCZOS)
    sheet.save(OUT / "_contact_sheet_backgrounds.png", quality=95)


if __name__ == "__main__":
    main()
