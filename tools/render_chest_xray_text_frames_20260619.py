from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(r"F:\ANRYCAMPANY")
SRC = ROOT / "reel_assets" / "chest_xray_series" / "draft_frames_20260619"
OUT = ROOT / "reel_assets" / "chest_xray_series" / "text_frames_20260619"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1920

TEXTS = [
    ["お腹が痛いのに", "なんで胸のレントゲンを", "撮るんだろう…"],
    ["説明がないと", "不思議に思うのは", "当然です"],
    ["実は、ちゃんと", "理由があります"],
    ["消化管に穴が開くと", "空気がお腹の中に", "漏れることがあります"],
    ["その空気は", "胸部X線で確認しやすい", "場合があります"],
    ["手術前に胸を撮る", "こともあります"],
    ["念のためだけでなく", "あなたの安全のために", "撮っています"],
    ["胸部X線では", "肺・心臓・横隔膜まわりを", "確認できます"],
    ["理由がわかると", "ちゃんと診てもらっていると", "感じませんか？"],
    ["検査には", "一つひとつ", "理由があります"],
    ["検査前の不安を", "安心に変える情報を", "発信中"],
    ["あとで見返せるように", "保存しておいてください"],
]

FONT_CANDIDATES = [
    Path(r"C:\Windows\Fonts\meiryob.ttc"),
    Path(r"C:\Windows\Fonts\YuGothB.ttc"),
    Path(r"C:\Windows\Fonts\meiryo.ttc"),
]


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def fit_cover(im: Image.Image) -> Image.Image:
    im = im.convert("RGB")
    sw, sh = im.size
    scale = max(W / sw, H / sh)
    nw, nh = round(sw * scale), round(sh * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - W) // 2
    top = (nh - H) // 2
    return im.crop((left, top, left + W, top + H))


def fit_font(lines: list[str], max_width: int, start: int, minimum: int) -> ImageFont.FreeTypeFont:
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    for size in range(start, minimum - 1, -2):
        f = load_font(size)
        if all(probe.textlength(line, font=f) <= max_width for line in lines):
            return f
    return load_font(minimum)


def draw_text_block(base: Image.Image, lines: list[str], frame_no: int) -> Image.Image:
    im = fit_cover(base)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    is_cta = frame_no >= 11
    max_width = 900 if not is_cta else 860
    font = fit_font(lines, max_width, 72 if not is_cta else 76, 46 if not is_cta else 52)

    bbox = [draw.textbbox((0, 0), line, font=font) for line in lines]
    widths = [b[2] - b[0] for b in bbox]
    heights = [b[3] - b[1] for b in bbox]
    line_h = max(heights) + (26 if not is_cta else 30)
    pad_x = 48 if not is_cta else 56
    pad_y = 38 if not is_cta else 48
    box_w = int(max(widths) + pad_x * 2)
    box_h = int(line_h * len(lines) + pad_y * 2)
    x0 = (W - box_w) // 2

    if is_cta:
        y0 = 700
    elif frame_no in {1, 2, 3, 9, 10}:
        y0 = 180
    elif frame_no in {4, 6}:
        y0 = 150
    else:
        y0 = 175

    y0 = max(120, min(y0, H - box_h - 180))
    radius = 28

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle(
        (x0 + 8, y0 + 10, x0 + box_w + 8, y0 + box_h + 10),
        radius=radius,
        fill=(0, 0, 0, 95),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
    overlay = Image.alpha_composite(overlay, shadow)
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle(
        (x0, y0, x0 + box_w, y0 + box_h),
        radius=radius,
        fill=(255, 255, 255, 226 if not is_cta else 238),
    )

    y = y0 + pad_y
    for line in lines:
        tw = draw.textlength(line, font=font)
        draw.text(((W - tw) / 2, y), line, font=font, fill=(25, 37, 45))
        y += line_h

    return Image.alpha_composite(im.convert("RGBA"), overlay).convert("RGB")


def cta_background() -> Image.Image:
    source = Image.open(SRC / "frame_09_draft.png")
    bg = fit_cover(source).filter(ImageFilter.GaussianBlur(10)).convert("RGBA")
    wash = Image.new("RGBA", (W, H), (245, 250, 252, 142))
    return Image.alpha_composite(bg, wash).convert("RGB")


def main() -> None:
    for i in range(1, 11):
        base = Image.open(SRC / f"frame_{i:02d}_draft.png")
        out = draw_text_block(base, TEXTS[i - 1], i)
        out.save(OUT / f"frame_{i:02d}_text.png", quality=95)

    bg = cta_background()
    for i in range(11, 13):
        out = draw_text_block(bg, TEXTS[i - 1], i)
        out.save(OUT / f"frame_{i:02d}_text.png", quality=95)

    print(OUT)


if __name__ == "__main__":
    main()
