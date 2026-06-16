from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[2]
SERIES = ROOT / "reel_assets" / "bone_density_series"
SRC1 = SERIES / "01_heel_ultrasound_reason"
SRC2 = SERIES / "02_heel_vs_lumbar" / "preview_backgrounds"
OUT = SERIES / "03_dxa_lumbar_femur_reason" / "background_frames"
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


def tint(img: Image.Image, alpha=18) -> Image.Image:
    overlay = Image.new("RGBA", (W, H), (255, 255, 255, alpha))
    out = img.convert("RGBA")
    out.alpha_composite(overlay)
    return out.convert("RGB")


def rounded_shadow(base: Image.Image, box, radius=38):
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(shadow)
    x1, y1, x2, y2 = box
    d.rounded_rectangle((x1, y1 + 18, x2, y2 + 18), radius=radius, fill=(55, 85, 95, 42))
    shadow = shadow.filter(ImageFilter.GaussianBlur(24))
    base.alpha_composite(shadow)


def anatomy_card() -> Image.Image:
    base = Image.new("RGBA", (W, H), (246, 251, 250, 255))
    d = ImageDraw.Draw(base)
    for y in range(H):
        c = int(250 - y * 10 / H)
        d.line((0, y, W, y), fill=(c, min(255, c + 4), min(255, c + 3), 255))

    card = (92, 725, 988, 1440)
    rounded_shadow(base, card)
    d.rounded_rectangle(card, radius=42, fill=(255, 255, 255, 255))

    spine_x = 405
    for i in range(6):
        y = 815 + i * 78
        d.rounded_rectangle((spine_x - 42, y, spine_x + 42, y + 56), radius=18, fill=(218, 232, 232, 255))
        d.line((spine_x - 82, y + 28, spine_x + 82, y + 28), fill=(140, 178, 184, 255), width=5)
    d.line((spine_x, 810, spine_x, 1325), fill=(122, 166, 174, 255), width=8)

    hip_y = 1230
    d.ellipse((600, hip_y - 90, 760, hip_y + 70), fill=(222, 235, 234, 255), outline=(134, 174, 181, 255), width=6)
    d.polygon([(668, hip_y + 50), (730, hip_y + 48), (800, 1390), (736, 1400)], fill=(210, 229, 229, 255), outline=(134, 174, 181, 255))
    d.arc((540, hip_y - 70, 710, hip_y + 120), start=285, end=80, fill=(134, 174, 181, 255), width=12)

    d.rounded_rectangle((205, 710, 500, 782), radius=24, fill=(31, 93, 116, 255))
    d.rounded_rectangle((575, 710, 875, 782), radius=24, fill=(31, 93, 116, 255))
    return base.convert("RGB")


def scan_room_with_focus(path: Path) -> Image.Image:
    img = cover(path, zoom=1.06, x_bias=0.50, y_bias=0.52).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle((135, 1220, 945, 1510), radius=44, fill=(255, 255, 255, 214))
    d.line((230, 1410, 850, 1410), fill=(34, 110, 130, 205), width=10)
    d.ellipse((278, 1325, 358, 1405), outline=(34, 110, 130, 230), width=8)
    d.ellipse((700, 1310, 820, 1430), outline=(34, 110, 130, 230), width=8)
    return img.convert("RGB")


def save_frame(n: int, img: Image.Image):
    img.save(OUT / f"bg_{n:02d}.png", quality=95)


def main():
    dxa = SRC2 / "adopted_07_dxa_horizon_reference_no_window.png"
    heel = SRC2 / "preview_03_health_check_heel_ultrasound.png"
    consult = SRC1 / "bg_07_followup_exam_consult_no_logo.png"
    result = SRC1 / "bg_04_result_explanation_no_logo.png"
    cta = SRC1 / "bg_08_reassuring_save_cta_no_logo.png"

    save_frame(1, cover(dxa, zoom=1.0, x_bias=0.50, y_bias=0.50))
    save_frame(2, tint(cover(dxa, zoom=1.06, x_bias=0.52, y_bias=0.56), 14))
    save_frame(3, scan_room_with_focus(dxa))
    save_frame(4, anatomy_card())
    save_frame(5, anatomy_card())
    save_frame(6, tint(cover(result, zoom=1.02, x_bias=0.50, y_bias=0.54), 18))
    save_frame(7, tint(cover(heel, zoom=1.0, x_bias=0.50, y_bias=0.50), 18))
    save_frame(8, tint(cover(consult, zoom=1.0, x_bias=0.50, y_bias=0.50), 10))
    save_frame(9, tint(cover(cta, zoom=1.0, x_bias=0.50, y_bias=0.50), 8))
    save_frame(10, tint(cover(cta, zoom=1.0, x_bias=0.50, y_bias=0.50), 8))

    thumb_w, thumb_h = 270, 480
    sheet = Image.new("RGB", (thumb_w * 5, thumb_h * 2), (245, 248, 247))
    for i in range(1, 11):
        img = Image.open(OUT / f"bg_{i:02d}.png").convert("RGB")
        img = img.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = ((i - 1) % 5) * thumb_w
        y = ((i - 1) // 5) * thumb_h
        sheet.paste(img, (x, y))
    sheet.save(OUT / "_contact_sheet_backgrounds.png", quality=95)
    print(OUT / "_contact_sheet_backgrounds.png")


if __name__ == "__main__":
    main()
