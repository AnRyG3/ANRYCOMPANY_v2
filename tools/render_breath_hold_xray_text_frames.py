from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter


SRC_DIR = Path(r"C:\Users\maruk\.codex\generated_images\019ee502-875b-7903-9063-c40797d15ac4")
OUT_DIR = Path(r"F:\ANRYCAMPANY\reel_assets\breath_hold_xray_series\text_frames")
BASE_DIR = Path(r"F:\ANRYCAMPANY\reel_assets\breath_hold_xray_series\base_images")
CONTACT = Path(r"F:\ANRYCAMPANY\reel_assets\breath_hold_xray_series\contact_text_frames.jpg")

FRAME_SOURCES = {
    1: "ig_0b30be1a716bbebf016a36906b1b948191a9e49de1a7992131.png",
    2: "ig_0b30be1a716bbebf016a3695bd749c819181b0e23c3c109520.png",
    3: "ig_0b30be1a716bbebf016a36910a97c48191b17b7d48eb172fdd.png",
    4: "ig_0b30be1a716bbebf016a3698728f90819182490151cae9a906.png",
    5: "ig_0b30be1a716bbebf016a3696981c388191a781ed9b81784d59.png",
    6: "ig_0b30be1a716bbebf016a3696e4611881918f8247a451fbb185.png",
    7: "ig_0b30be1a716bbebf016a36927860cc8191838bbfce361932eb.png",
    8: "ig_0b30be1a716bbebf016a3697566ad48191940b62dc57459321.png",
    9: "ig_0b30be1a716bbebf016a3693154bfc8191a3cf0105109e914d.png",
    10: "ig_0b30be1a716bbebf016a3697a055748191907a7d1e1545924c.png",
}

TEXTS = {
    1: 'ちゃんと\n止められていたかな…',
    2: '不安に感じる方は\n多いです',
    3: 'ブレが少ない\nタイミングを見ています',
    4: '「吸って」は\n肺を広げるため',
    5: '呼吸の動きも\n見ています',
    6: '声かけで\nタイミングを調整',
    7: '少しズレても\n問題ないことが多いです',
    8: 'リラックスのほうが\nきれいに撮れます',
    9: 'ちゃんと見て\n撮っています',
    10: '吸って、\n合図に合わせるだけで大丈夫',
    11: '検査前の不安を\n安心に変える情報を発信中',
    12: '保存して、\n検査前に見返してください',
}


def font_path():
    candidates = [
        r"C:\Windows\Fonts\YuGothB.ttc",
        r"C:\Windows\Fonts\YuGothM.ttc",
        r"C:\Windows\Fonts\meiryo.ttc",
        r"C:\Windows\Fonts\msgothic.ttc",
    ]
    for item in candidates:
        if Path(item).exists():
            return item
    raise FileNotFoundError("Japanese font not found")


FONT_PATH = font_path()


def cover(im, size=(1080, 1920)):
    im = im.convert("RGB")
    sw, sh = im.size
    tw, th = size
    scale = max(tw / sw, th / sh)
    nw, nh = int(sw * scale), int(sh * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return im.crop((left, top, left + tw, top + th))


def fit_font(draw, text, max_w, max_h, start=58, min_size=34):
    size = start
    while size >= min_size:
        font = ImageFont.truetype(FONT_PATH, size)
        bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=int(size * 0.35), align="center")
        if bbox[2] - bbox[0] <= max_w and bbox[3] - bbox[1] <= max_h:
            return font, int(size * 0.35), bbox
        size -= 2
    font = ImageFont.truetype(FONT_PATH, min_size)
    bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=int(min_size * 0.35), align="center")
    return font, int(min_size * 0.35), bbox


def draw_text_panel(im, text, y_center=640):
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    x1, x2 = 92, 988
    max_w = x2 - x1 - 90
    max_h = 360
    font, spacing, bbox = fit_font(d, text, max_w, max_h, start=64, min_size=40)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 46, 38
    panel_w = min(x2 - x1, tw + pad_x * 2)
    panel_h = th + pad_y * 2
    px1 = (1080 - panel_w) // 2
    py1 = int(y_center - panel_h / 2)
    px2 = px1 + panel_w
    py2 = py1 + panel_h
    d.rounded_rectangle((px1, py1, px2, py2), radius=28, fill=(255, 255, 255, 224))
    d.rounded_rectangle((px1, py1, px2, py2), radius=28, outline=(255, 255, 255, 245), width=3)
    tx = 540
    ty = py1 + pad_y - bbox[1]
    shadow = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.multiline_text((tx + 2, ty + 2), text, font=font, spacing=spacing, align="center", anchor="ma", fill=(255, 255, 255, 120))
    overlay = Image.alpha_composite(shadow, overlay)
    d = ImageDraw.Draw(overlay)
    d.multiline_text((tx, ty), text, font=font, spacing=spacing, align="center", anchor="ma", fill=(22, 48, 92, 255))
    return Image.alpha_composite(im.convert("RGBA"), overlay).convert("RGB")


def make_cta(bg, text, frame_no):
    im = bg.filter(ImageFilter.GaussianBlur(8))
    tint = Image.new("RGBA", im.size, (255, 255, 255, 70))
    im = Image.alpha_composite(im.convert("RGBA"), tint).convert("RGB")
    return draw_text_panel(im, text, y_center=900 if frame_no == 11 else 890)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    frames = {}
    for no, name in FRAME_SOURCES.items():
        src = SRC_DIR / name
        im = cover(Image.open(src))
        frames[no] = im
        im.save(BASE_DIR / f"frame_{no:02d}_base.png", quality=95)
        with_text = draw_text_panel(im, TEXTS[no], y_center=1460)
        with_text.save(OUT_DIR / f"frame_{no:02d}_text.png", quality=95)

    cta_bg = frames[10]
    for no in (11, 12):
        cta = make_cta(cta_bg, TEXTS[no], no)
        cta.save(OUT_DIR / f"frame_{no:02d}_text.png", quality=95)

    thumbs = []
    for no in range(1, 13):
        im = Image.open(OUT_DIR / f"frame_{no:02d}_text.png").resize((216, 384), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (216, 420), "white")
        canvas.paste(im, (0, 0))
        d = ImageDraw.Draw(canvas)
        label_font = ImageFont.truetype(FONT_PATH, 22)
        d.text((10, 390), f"{no:02d}", fill=(0, 0, 0), font=label_font)
        thumbs.append(canvas)

    sheet = Image.new("RGB", (216 * 4, 420 * 3), (240, 240, 240))
    for idx, thumb in enumerate(thumbs):
        x = (idx % 4) * 216
        y = (idx // 4) * 420
        sheet.paste(thumb, (x, y))
    sheet.save(CONTACT, quality=92)
    print(OUT_DIR)
    print(CONTACT)


if __name__ == "__main__":
    main()
