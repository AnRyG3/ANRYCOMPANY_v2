from pathlib import Path
import shutil

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"C:\Users\maruk\OneDrive\デスクトップ\Anry campany")
BG = ROOT / "reel_assets" / "mri_noise_reason_v1" / "generated_backgrounds"
OUT = ROOT / "reel_assets" / "mri_noise_reason_v1" / "telop_frames"
COMMON_CTA = ROOT / "reel_assets" / "common" / "reel_end_card_share.png"

W, H = 1080, 1920
NAVY = (5, 28, 76, 244)
DEEP_TEAL = (4, 72, 92, 244)
RED = (204, 42, 58, 246)
WHITE = (255, 255, 255, 255)
YELLOW = (255, 220, 82, 255)
CYAN = (119, 230, 255, 255)
DISCLAIMER = "※個別の判断は医療機関でご相談ください"

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


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, spacing: int = 16):
    box = draw.multiline_textbbox((0, 0), text, font=fnt, spacing=spacing, align="center")
    return box[2] - box[0], box[3] - box[1]


def fit_font(draw: ImageDraw.ImageDraw, text: str, max_w: int, start: int, min_size: int = 38):
    size = start
    while size >= min_size:
        fnt = font(size, True)
        tw, _ = text_size(draw, text, fnt)
        if tw <= max_w:
            return fnt
        size -= 2
    return font(min_size, True)


def subtle_vignette(base: Image.Image):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, W, 380), fill=(255, 255, 255, 18))
    draw.rectangle((0, H - 360, W, H), fill=(0, 0, 0, 42))
    base.alpha_composite(overlay)


def badge(base: Image.Image, text: str, y: int = 230, fill=RED):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    fnt = font(40, True)
    box = draw.textbbox((0, 0), text, font=fnt)
    tw, th = box[2] - box[0], box[3] - box[1]
    pad_x, pad_y = 34, 18
    x = (W - tw - pad_x * 2) // 2
    draw.rounded_rectangle((x, y, x + tw + pad_x * 2, y + th + pad_y * 2), radius=30, fill=fill)
    draw.text((W // 2, y + pad_y - 2), text, font=fnt, fill=WHITE, anchor="ma")
    base.alpha_composite(overlay)


def rounded_box(
    base: Image.Image,
    lines,
    y: int,
    width: int = 850,
    fill=NAVY,
    start_size: int = 70,
    pad_x: int = 48,
    pad_y: int = 38,
    accent: bool = False,
):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    text = "\n".join(lines)
    fnt = fit_font(draw, text, width - pad_x * 2, start_size)
    _, th = text_size(draw, text, fnt)
    box_h = th + pad_y * 2
    x = (W - width) // 2
    radius = 42

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x, y + 10, x + width, y + box_h + 10), radius=radius, fill=(0, 0, 0, 74))
    shadow = shadow.filter(ImageFilter.GaussianBlur(9))
    base.alpha_composite(shadow)

    draw.rounded_rectangle((x, y, x + width, y + box_h), radius=radius, fill=fill)
    if accent:
        draw.rounded_rectangle((x, y, x + 18, y + box_h), radius=10, fill=YELLOW)
    draw.multiline_text(
        (W // 2, y + pad_y - 8),
        text,
        font=fnt,
        fill=WHITE,
        anchor="ma",
        align="center",
        spacing=16,
    )
    base.alpha_composite(overlay)


def bottom_note(base: Image.Image, text: str = DISCLAIMER, y: int = H - 155):
    draw = ImageDraw.Draw(base)
    fnt = font(30, False)
    for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
        draw.text((W // 2 + dx, y + dy), text, font=fnt, fill=(0, 0, 0, 165), anchor="mm")
    draw.text((W // 2, y), text, font=fnt, fill=(255, 255, 255, 240), anchor="mm")


def end_card_overlay(base: Image.Image):
    overlay = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle((95, 300, 985, 800), radius=48, fill=(255, 255, 255, 224))
    draw.rounded_rectangle((95, 300, 985, 800), radius=48, outline=(92, 201, 220, 230), width=4)
    base.alpha_composite(overlay)

    draw = ImageDraw.Draw(base)
    lead = "MRIの音は\n怖い音じゃない"
    fnt_lead = font(58, True)
    draw.multiline_text((W // 2, 385), lead, font=fnt_lead, fill=(5, 28, 76), anchor="ma", align="center", spacing=12)

    title = "検査前の不安が減る情報を\n発信しています。"
    fnt_title = font(42, True)
    draw.multiline_text((W // 2, 560), title, font=fnt_title, fill=(4, 72, 92), anchor="ma", align="center", spacing=10)

    body = "チャンネル登録しておくと、\n次の検査のときに役立ちます。"
    fnt_body = font(38, True)
    draw.multiline_text((W // 2, 675), body, font=fnt_body, fill=(4, 72, 92), anchor="ma", align="center", spacing=10)


frames = [
    {
        "src": "bg_01_hook_patient_worried.png",
        "out": "cut_01_hook.png",
        "badge": "MRI中に一番多い勘違い",
        "lines": ["あの大きな音", "壊れてる？"],
        "y": 360,
        "fill": RED,
        "start": 76,
    },
    {
        "src": "bg_02_loud_sound_scan.png",
        "out": "cut_02_sound_is_progress.png",
        "lines": ["いいえ。", "検査が進んでいる音です"],
        "y": 305,
        "fill": NAVY,
        "start": 66,
        "accent": True,
    },
    {
        "src": "bg_03_magnet_radio_waves.png",
        "out": "cut_03_magnet_radio.png",
        "lines": ["MRIは", "磁石と電波で", "体の中を見ています"],
        "y": 270,
        "fill": DEEP_TEAL,
        "start": 64,
    },
    {
        "src": "bg_04_internal_vibration.png",
        "out": "cut_04_vibration.png",
        "lines": ["磁石が切り替わるたびに", "装置が振動して", "あの音が出ます"],
        "y": 255,
        "fill": NAVY,
        "start": 58,
    },
    {
        "src": "bg_05_scan_progress_control_room.png",
        "out": "cut_05_sign_of_scan.png",
        "lines": ["音がしている間は", "ちゃんと撮影しているサイン"],
        "y": 285,
        "fill": NAVY,
        "start": 62,
        "accent": True,
    },
    {
        "src": "bg_06_reassurance_end.png",
        "out": "cut_06_fixed_message.png",
        "end": True,
    },
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for item in frames:
        img = cover_resize(Image.open(BG / item["src"])).convert("RGBA")
        subtle_vignette(img)
        if item.get("end"):
            end_card_overlay(img)
        else:
            if item.get("badge"):
                badge(img, item["badge"])
            rounded_box(
                img,
                item["lines"],
                item["y"],
                fill=item.get("fill", NAVY),
                start_size=item.get("start", 70),
                accent=item.get("accent", False),
            )
            bottom_note(img)
        img.convert("RGB").save(OUT / item["out"], quality=96)
    shutil.copy2(COMMON_CTA, OUT / "cut_07_common_share_cta.png")


if __name__ == "__main__":
    main()
