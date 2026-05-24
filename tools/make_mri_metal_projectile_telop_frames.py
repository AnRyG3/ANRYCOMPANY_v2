from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(r"F:\ANRYCAMPANY")
BG = ROOT / "reel_assets" / "mri_metal_projectile_v1" / "generated_backgrounds"
OUT = ROOT / "reel_assets" / "mri_metal_projectile_v1" / "telop_frames"

W, H = 1080, 1920
NAVY = (5, 28, 76, 246)
RED = (210, 34, 50, 246)
WHITE = (255, 255, 255, 255)
YELLOW = (255, 218, 80, 255)
DISCLAIMER = "窶ｻ蛟句挨縺ｮ蛻､譁ｭ縺ｯ蛹ｻ逋よｩ滄未縺ｧ縺皮嶌隲・￥縺縺輔＞"
DISCLAIMER_Y = H - 430

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


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, spacing: int = 14):
    box = draw.multiline_textbbox((0, 0), text, font=fnt, spacing=spacing, align="center")
    return box[2] - box[0], box[3] - box[1]


def fit_font(draw: ImageDraw.ImageDraw, text: str, max_w: int, start: int, min_size: int = 42):
    size = start
    while size >= min_size:
        fnt = font(size, True)
        tw, _ = text_size(draw, text, fnt)
        if tw <= max_w:
            return fnt
        size -= 2
    return font(min_size, True)


def subtle_vignette(base: Image.Image, top_light: bool = True):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    if top_light:
        draw.rectangle((0, 0, W, 420), fill=(255, 255, 255, 24))
    draw.rectangle((0, H - 300, W, H), fill=(0, 0, 0, 50))
    base.alpha_composite(overlay)


def rounded_text_box(
    base: Image.Image,
    lines,
    y: int,
    width: int = 790,
    pad_x: int = 48,
    pad_y: int = 34,
    fill=NAVY,
    accent_line: int | None = None,
):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    text = "\n".join(lines)
    fnt = fit_font(draw, text, width - pad_x * 2, 66)
    _, th = text_size(draw, text, fnt)
    box_h = th + pad_y * 2
    x = (W - width) // 2
    radius = 42

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x, y + 10, x + width, y + box_h + 10), radius=radius, fill=(0, 0, 0, 72))
    shadow = shadow.filter(ImageFilter.GaussianBlur(9))
    base.alpha_composite(shadow)

    draw.rounded_rectangle((x, y, x + width, y + box_h), radius=radius, fill=fill)
    if accent_line is not None:
        draw.rounded_rectangle((x, y, x + 18, y + box_h), radius=9, fill=YELLOW)

    draw.multiline_text(
        (W // 2, y + pad_y - 8),
        text,
        font=fnt,
        fill=WHITE,
        anchor="ma",
        align="center",
        spacing=14,
    )
    base.alpha_composite(overlay)


def small_badge(base: Image.Image, text: str, y: int = 285, fill=RED):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    fnt = font(42, True)
    box = draw.textbbox((0, 0), text, font=fnt)
    tw, th = box[2] - box[0], box[3] - box[1]
    pad_x, pad_y = 34, 18
    x = (W - tw - pad_x * 2) // 2
    draw.rounded_rectangle((x, y, x + tw + pad_x * 2, y + th + pad_y * 2), radius=28, fill=fill)
    draw.text((W // 2, y + pad_y - 2), text, font=fnt, fill=WHITE, anchor="ma")
    base.alpha_composite(overlay)


def bottom_disclaimer(base: Image.Image):
    draw = ImageDraw.Draw(base)
    fnt = font(30, False)
    x, y = W // 2, DISCLAIMER_Y
    for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
        draw.text((x + dx, y + dy), DISCLAIMER, font=fnt, fill=(0, 0, 0, 170), anchor="mm")
    draw.text((x, y), DISCLAIMER, font=fnt, fill=(255, 255, 255, 240), anchor="mm")


frames = [
    {
        "src": "bg_01_mri_room_warning_entrance.png",
        "out": "cut_01_warning_entrance.png",
        "badge": "MRI螳牙・遒ｺ隱・,
        "lines": ["MRI螳､縺ｫ霆頑､・ｭ・, "謖√■霎ｼ繧縺ｨ・・],
        "y": 420,
        "fill": RED,
    },
    {
        "src": "bg_02_iv_pole_pulled_to_mri.png",
        "out": "cut_02_iv_pole_pulled.png",
        "lines": ["謖√■霎ｼ繧縺ｨ", "莠区腐縺ｫ縺ｪ繧翫∪縺・],
        "y": 340,
        "fill": NAVY,
    },
    {
        "src": "bg_03_wheelchair_safety_check.png",
        "out": "cut_03_wheelchair_check.png",
        "lines": ["霆頑､・ｭ舌・轤ｹ貊ｴ蜿ｰ", "驟ｸ邏繝懊Φ繝・],
        "y": 340,
        "fill": NAVY,
    },
    {
        "src": "bg_04_always_on_magnetic_field.png",
        "out": "cut_04_always_magnetic.png",
        "lines": ["諢丞､悶→遏･繧峨↑縺・, "MRI縺ｮ莠句ｮ・],
        "y": 340,
        "fill": NAVY,
        "accent": 1,
    },
    {
        "src": "bg_04_always_on_magnetic_field.png",
        "out": "cut_05_checklist_items.png",
        "lines": ["謦ｮ蠖ｱ縺励※縺・↑縺・凾繧・, "逎∝ｴ縺ｯ縺ゅｊ縺ｾ縺・],
        "y": 340,
        "fill": NAVY,
    },
    {
        "src": "bg_06_consult_staff_before_mri.png",
        "out": "cut_06_tell_staff_ok.png",
        "lines": ["閨槭°繧後◆縺薙→縺ｯ", "豁｣逶ｴ縺ｫ莨昴∴縺ｦ縺上□縺輔＞"],
        "y": 340,
        "fill": NAVY,
    },
    {
        "src": "bg_07_save_end_card_background.png",
        "out": "cut_07_save_end_card.png",
        "badge": "MRI蜑阪↓遏･縺｣縺ｦ縺翫″縺溘＞",
        "lines": ["莠区腐繧帝亟縺・, "螟ｧ蛻・↑螳牙・遒ｺ隱・],
        "y": 430,
        "fill": NAVY,
    },
    {
        "src": "bg_07_save_end_card_background.png",
        "out": "cut_08_save_share_cta.png",
        "badge": "螟ｧ蛻・↑莠ｺ縺勲RI繧貞女縺代ｋ蜑阪↓",
        "lines": ["縺薙・蜍慕判繧・, "隕九○縺ｦ縺ゅ￡縺ｦ縺上□縺輔＞"],
        "y": 430,
        "fill": NAVY,
    },
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for item in frames:
        img = cover_resize(Image.open(BG / item["src"])).convert("RGBA")
        subtle_vignette(img)
        if item.get("badge"):
            small_badge(img, item["badge"], y=285, fill=RED)
        rounded_text_box(
            img,
            item["lines"],
            item["y"],
            fill=item.get("fill", NAVY),
            accent_line=item.get("accent"),
        )
        bottom_disclaimer(img)
        img.convert("RGB").save(OUT / item["out"], quality=96)


if __name__ == "__main__":
    main()


