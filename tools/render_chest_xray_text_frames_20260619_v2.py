from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(r"F:\ANRYCAMPANY")
SRC = ROOT / "reel_assets" / "chest_xray_series" / "draft_frames_20260619"
OUT = ROOT / "reel_assets" / "chest_xray_series" / "text_frames_20260619_v2"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1920

TEXTS = [
    ["お腹が痛いのに", "なぜ胸のレントゲン？"],
    ["説明がないと", "不思議ですよね"],
    ["ちゃんと", "理由があります"],
    ["消化管に穴が開くと", "空気が漏れることも"],
    ["その空気は", "胸部X線で見えることも"],
    ["手術前にも", "胸を撮ることがあります"],
    ["安全のために", "確認しています"],
    ["肺・心臓・横隔膜を", "一度に確認できます"],
    ["理由がわかると", "少し安心できます"],
    ["疑問に思ったら", "遠慮なく聞いてください"],
    ["検査前の不安を", "安心に変える情報を", "発信中"],
    ["あとで見返せるように", "保存しておいてください"],
]

CENTER_FRAMES = {5, 8, 9, 11, 12}
FONT_CANDIDATES = [
    Path(r"C:\Windows\Fonts\meiryob.ttc"),
    Path(r"C:\Windows\Fonts\YuGothB.ttc"),
    Path(r"C:\Windows\Fonts\meiryo.ttc"),
]


def load_font(size: int):
    for path in FONT_CANDIDATES:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def fit_cover(image: Image.Image) -> Image.Image:
    image = image.convert("RGB")
    sw, sh = image.size
    scale = max(W / sw, H / sh)
    nw, nh = round(sw * scale), round(sh * scale)
    image = image.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - W) // 2
    top = (nh - H) // 2
    return image.crop((left, top, left + W, top + H))


def fit_font(lines, max_width, start=78, minimum=50):
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    for size in range(start, minimum - 1, -2):
        font = load_font(size)
        if all(probe.textlength(line, font=font) <= max_width for line in lines):
            return font
    return load_font(minimum)


def draw_text_block(base: Image.Image, lines, frame_no: int) -> Image.Image:
    image = fit_cover(base)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    is_cta = frame_no >= 11
    font = fit_font(lines, 880 if not is_cta else 860, 78 if not is_cta else 76, 50)
    boxes = [draw.textbbox((0, 0), line, font=font) for line in lines]
    widths = [box[2] - box[0] for box in boxes]
    heights = [box[3] - box[1] for box in boxes]
    line_h = max(heights) + (26 if not is_cta else 30)
    pad_x = 52
    pad_y = 42 if not is_cta else 50
    box_w = int(max(widths) + pad_x * 2)
    box_h = int(line_h * len(lines) + pad_y * 2)
    x0 = (W - box_w) // 2

    if frame_no in CENTER_FRAMES:
        y0 = (H - box_h) // 2
    else:
        y0 = 185
    y0 = max(120, min(y0, H - box_h - 170))

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(
        (x0 + 8, y0 + 10, x0 + box_w + 8, y0 + box_h + 10),
        radius=28,
        fill=(0, 0, 0, 90),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
    overlay = Image.alpha_composite(overlay, shadow)
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle(
        (x0, y0, x0 + box_w, y0 + box_h),
        radius=28,
        fill=(255, 255, 255, 228 if not is_cta else 240),
    )

    y = y0 + pad_y
    for line in lines:
        tw = draw.textlength(line, font=font)
        draw.text(((W - tw) / 2, y), line, font=font, fill=(24, 36, 44))
        y += line_h

    return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")


def cta_background() -> Image.Image:
    source = Image.open(SRC / "frame_09_draft.png")
    background = fit_cover(source).filter(ImageFilter.GaussianBlur(10)).convert("RGBA")
    wash = Image.new("RGBA", (W, H), (245, 250, 252, 145))
    return Image.alpha_composite(background, wash).convert("RGB")


def main() -> None:
    for i in range(1, 11):
        image = Image.open(SRC / f"frame_{i:02d}_draft.png")
        draw_text_block(image, TEXTS[i - 1], i).save(OUT / f"frame_{i:02d}_text.png", quality=95)

    background = cta_background()
    for i in range(11, 13):
        draw_text_block(background, TEXTS[i - 1], i).save(OUT / f"frame_{i:02d}_text.png", quality=95)

    print(OUT)


if __name__ == "__main__":
    main()
