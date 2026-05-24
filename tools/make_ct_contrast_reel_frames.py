from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(r"F:\ANRYCAMPANY")
BG = ROOT / "reel_assets" / "ct_contrast_v1" / "generated_backgrounds"
OUT = ROOT / "reel_assets" / "ct_contrast_v1" / "frames_05_short_120ten"

W, H = 1080, 1920
NAVY = (5, 28, 76, 245)
WHITE = (255, 255, 255, 255)
DISCLAIMER = "窶ｻ蛟句挨縺ｮ蛻､譁ｭ縺ｯ蛹ｻ逋よｩ滄未縺ｧ縺皮嶌隲・￥縺縺輔＞"
SAFE_TOP_SHIFT = 80
DISCLAIMER_Y = H - 205

FONT_BOLD = r"C:\Windows\Fonts\YuGothB.ttc"
FONT_REG = r"C:\Windows\Fonts\YuGothM.ttc"


def font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def cover_resize(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")
    scale = max(W / img.width, H / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - W) // 2
    top = (nh - H) // 2
    return img.crop((left, top, left + W, top + H))


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont):
    box = draw.multiline_textbbox((0, 0), text, font=fnt, spacing=16, align="center")
    return box[2] - box[0], box[3] - box[1]


def fit_font(draw: ImageDraw.ImageDraw, text: str, max_w: int, start: int, min_size: int = 44):
    size = start
    while size >= min_size:
        fnt = font(size, True)
        tw, _ = text_size(draw, text, fnt)
        if tw <= max_w:
            return fnt
        size -= 2
    return font(min_size, True)


def rounded_text_box(base: Image.Image, lines, y: int, width: int = 820, pad_y: int = 40):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    text = "\n".join(lines)
    fnt = fit_font(draw, text, width - 90, 70)
    tw, th = text_size(draw, text, fnt)
    box_h = th + pad_y * 2
    x = (W - width) // 2
    radius = 44
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x, y + 8, x + width, y + box_h + 8), radius=radius, fill=(0, 0, 0, 70))
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    base.alpha_composite(shadow)
    draw.rounded_rectangle((x, y, x + width, y + box_h), radius=radius, fill=NAVY)
    draw.multiline_text((W // 2, y + pad_y - 6), text, font=fnt, fill=WHITE, anchor="ma", align="center", spacing=16)
    base.alpha_composite(overlay)


def bottom_disclaimer(base: Image.Image):
    draw = ImageDraw.Draw(base)
    fnt = font(30, False)
    x, y = W // 2, DISCLAIMER_Y
    for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
        draw.text((x + dx, y + dy), DISCLAIMER, font=fnt, fill=(0, 0, 0, 160), anchor="mm")
    draw.text((x, y), DISCLAIMER, font=fnt, fill=(255, 255, 255, 235), anchor="mm")


def subtle_vignette(base: Image.Image):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, W, 360), fill=(255, 255, 255, 18))
    draw.rectangle((0, H - 280, W, H), fill=(0, 0, 0, 45))
    base.alpha_composite(overlay)


frames = [
    ("bg_01_waiting_family.png", ["螳ｶ譌上′騾蠖ｱCT繧貞女縺代ｋ蜑阪↓", "縺薙ｌ縺縺醍｢ｺ隱・], 145 + SAFE_TOP_SHIFT),
    ("bg_05_reception_family.png", ["蜈医↓莨昴∴繧九□縺代〒", "豕ｨ諢上＠繧・☆縺上↑繧・], 130 + SAFE_TOP_SHIFT),
    ("bg_06_contrast_syringe.png", ["騾蠖ｱ蜑､縺ｯ", "隕九∴繧・☆縺上☆繧玖脈"], 145 + SAFE_TOP_SHIFT),
    ("bg_03_scan_review.png", ["蠢・ｦ√↑蝣ｴ髱｢縺ｧ縺ｯ", "險ｺ譁ｭ縺ｮ蜉ｩ縺代↓"], 135 + SAFE_TOP_SHIFT),
    ("bg_04_questionnaire.png", ["讀懈渊蜑阪↓莨昴∴繧九％縺ｨ", "3縺､"], 145 + SAFE_TOP_SHIFT),
    ("bg_04_questionnaire.png", ["1. 騾蠖ｱ蜑､縺ｧ", "豌怜・縺梧が縺上↑縺｣縺・], 140 + SAFE_TOP_SHIFT),
    ("bg_04_questionnaire.png", ["2. 縺懊ｓ縺昴￥", "蠑ｷ縺・い繝ｬ繝ｫ繧ｮ繝ｼ"], 140 + SAFE_TOP_SHIFT),
    ("bg_04_questionnaire.png", ["3. 閻取ｩ溯・繧・, "謖・遭縺輔ｌ縺・], 140 + SAFE_TOP_SHIFT),
    ("bg_05_reception_family.png", ["譛ｬ莠ｺ縺悟ｿ倥ｌ縺ｦ縺・◆繧・, "螳ｶ譌上°繧我ｼ昴∴縺ｦOK"], 135 + SAFE_TOP_SHIFT),
    ("bg_01_waiting_family.png", ["荳榊ｮ峨・", "謌第・縺励↑縺上※螟ｧ荳亥､ｫ"], 145 + SAFE_TOP_SHIFT),
    ("bg_05_reception_family.png", ["縺薙・3縺､縺縺・, "蜈医↓莨昴∴縺ｦ"], 145 + SAFE_TOP_SHIFT),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for idx, (bg_name, lines, y) in enumerate(frames, 1):
        img = cover_resize(Image.open(BG / bg_name)).convert("RGBA")
        subtle_vignette(img)
        rounded_text_box(img, lines, y)
        bottom_disclaimer(img)
        img.convert("RGB").save(OUT / f"cut_{idx:02d}.png", quality=95)


if __name__ == "__main__":
    main()


