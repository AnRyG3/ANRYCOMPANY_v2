from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
BASE_DIR = ROOT / "reel_assets" / "xray_ct_difference_series" / "base_images"
OUT_DIR = ROOT / "reel_assets" / "xray_ct_difference_series" / "text_frames_v1"
CONTACT = ROOT / "reel_assets" / "xray_ct_difference_series" / "contact_text_frames_v1.jpg"

W, H = 1080, 1920

TEXTS = {
    1: "レントゲンで異常なしなのに\nなんでCTも撮るの？",
    2: "同じ「撮影」なのに\n違いがわかりにくいですよね",
    3: "レントゲンとCTは\n「役割」が違います",
    4: "レントゲンは\n撮影範囲を平面的に見渡す検査",
    5: "診療放射線技師や医師は\n1枚から多くを確認します",
    6: "重なって見えにくい部分も\nあります",
    7: "そんなときにCTで\n詳しく確認します",
    8: "レントゲンは広く見る\nCTは深く見る検査",
    9: "段階を踏んでいるとわかると\n少し安心できます",
    10: "その1枚にも\nたくさんの情報があります",
    11: "検査前の不安を\n安心に変える情報を発信中",
    12: "保存して\nあとで見返してください",
}

PANEL_Y = {
    1: 310,
    2: 1450,
    3: 1450,
    4: 1460,
    5: 340,
    6: 1420,
    7: 1450,
    8: 340,
    9: 1450,
    10: 1450,
    11: 900,
    12: 900,
}

FONT_CANDIDATES = [
    Path(r"C:\Windows\Fonts\YuGothB.ttc"),
    Path(r"C:\Windows\Fonts\meiryob.ttc"),
    Path(r"C:\Windows\Fonts\YuGothM.ttc"),
    Path(r"C:\Windows\Fonts\meiryo.ttc"),
]


def font_path() -> Path:
    for path in FONT_CANDIDATES:
        if path.exists():
            return path
    raise FileNotFoundError("Japanese font not found")


FONT_PATH = font_path()


def load_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size)


def cover(image: Image.Image) -> Image.Image:
    image = image.convert("RGB")
    sw, sh = image.size
    scale = max(W / sw, H / sh)
    nw, nh = round(sw * scale), round(sh * scale)
    image = image.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - W) // 2
    top = (nh - H) // 2
    return image.crop((left, top, left + W, top + H))


def fit_font(draw: ImageDraw.ImageDraw, text: str, max_w: int, max_h: int, start: int, minimum: int):
    size = start
    while size >= minimum:
        font = load_font(size)
        spacing = int(size * 0.32)
        box = draw.multiline_textbbox((0, 0), text, font=font, spacing=spacing, align="center")
        if box[2] - box[0] <= max_w and box[3] - box[1] <= max_h:
            return font, spacing, box
        size -= 2
    font = load_font(minimum)
    spacing = int(minimum * 0.32)
    box = draw.multiline_textbbox((0, 0), text, font=font, spacing=spacing, align="center")
    return font, spacing, box


def draw_panel(image: Image.Image, text: str, frame_no: int) -> Image.Image:
    image = cover(image)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    is_cta = frame_no >= 11
    max_w = 890 if not is_cta else 860
    max_h = 310 if not is_cta else 380
    font, spacing, box = fit_font(
        draw,
        text,
        max_w=max_w,
        max_h=max_h,
        start=66 if not is_cta else 68,
        minimum=40,
    )

    text_w = box[2] - box[0]
    text_h = box[3] - box[1]
    pad_x = 56 if not is_cta else 62
    pad_y = 40 if not is_cta else 48
    panel_w = min(960, text_w + pad_x * 2)
    panel_h = text_h + pad_y * 2
    x1 = (W - panel_w) // 2
    y1 = int(PANEL_Y[frame_no] - panel_h / 2)
    y1 = max(130, min(y1, H - panel_h - 180))
    x2 = x1 + panel_w
    y2 = y1 + panel_h

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x1 + 8, y1 + 10, x2 + 8, y2 + 10), radius=28, fill=(0, 0, 0, 92))
    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
    overlay = Image.alpha_composite(overlay, shadow)

    draw = ImageDraw.Draw(overlay)
    fill = (255, 255, 255, 226 if not is_cta else 238)
    draw.rounded_rectangle((x1, y1, x2, y2), radius=28, fill=fill)
    draw.rounded_rectangle((x1, y1, x2, y2), radius=28, outline=(255, 255, 255, 245), width=3)

    tx = W // 2
    ty = y1 + pad_y - box[1]
    draw.multiline_text(
        (tx, ty),
        text,
        font=font,
        spacing=spacing,
        align="center",
        anchor="ma",
        fill=(22, 48, 76, 255),
    )

    return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")


def cta_background() -> Image.Image:
    source = cover(Image.open(BASE_DIR / "frame_10_base_no_text.png"))
    blurred = source.filter(ImageFilter.GaussianBlur(9)).convert("RGBA")
    wash = Image.new("RGBA", (W, H), (245, 250, 252, 135))
    return Image.alpha_composite(blurred, wash).convert("RGB")


def build_contact_sheet() -> None:
    thumbs = []
    label_font = load_font(24)
    for frame_no in range(1, 13):
        image = Image.open(OUT_DIR / f"frame_{frame_no:02d}_text.png")
        thumb = image.resize((216, 384), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (216, 420), "white")
        canvas.paste(thumb, (0, 0))
        draw = ImageDraw.Draw(canvas)
        draw.text((12, 390), f"{frame_no:02d}", font=label_font, fill=(0, 0, 0))
        thumbs.append(canvas)

    sheet = Image.new("RGB", (216 * 4, 420 * 3), (238, 238, 238))
    for index, thumb in enumerate(thumbs):
        x = (index % 4) * 216
        y = (index // 4) * 420
        sheet.paste(thumb, (x, y))
    sheet.save(CONTACT, quality=92)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for frame_no in range(1, 11):
        source = Image.open(BASE_DIR / f"frame_{frame_no:02d}_base_no_text.png")
        frame = draw_panel(source, TEXTS[frame_no], frame_no)
        frame.save(OUT_DIR / f"frame_{frame_no:02d}_text.png", quality=95)

    background = cta_background()
    for frame_no in (11, 12):
        frame = draw_panel(background, TEXTS[frame_no], frame_no)
        frame.save(OUT_DIR / f"frame_{frame_no:02d}_text.png", quality=95)

    build_contact_sheet()
    print(OUT_DIR)
    print(CONTACT)


if __name__ == "__main__":
    main()

