from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(r"F:\ANRYCAMPANY")
OUT = ROOT / "reel_assets" / "ct_longform_youtube_samples" / "production_bg_sample5"
FONT = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"
W, H = 1920, 1080


def fit(src, dst, centering=(0.5, 0.5)):
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    im = ImageOps.fit(im, (W, H), Image.Resampling.LANCZOS, centering=centering)
    im.save(dst, quality=95)


def contact_sheet():
    files = [
        OUT / "bg_01_ct_opening_16x9.jpg",
        OUT / "bg_02_waiting_room.png",
        OUT / "bg_03_reception.png",
        OUT / "bg_04_radiology_waiting.png",
        OUT / "bg_05_metal_clothing_16x9.jpg",
    ]
    labels = ["01 CT装置", "02 待合・不安", "03 受付", "04 放射線科待合", "05 服装・金属"]
    tw, th = 384, 216
    sheet = Image.new("RGB", (tw * 5, 270), (238, 242, 242))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(str(FONT), 24)
    for i, path in enumerate(files):
        im = ImageOps.fit(Image.open(path).convert("RGB"), (tw, th), Image.Resampling.LANCZOS)
        x = i * tw
        sheet.paste(im, (x, 0))
        draw.text((x + 18, 226), labels[i], font=font, fill=(20, 45, 68))
    sheet.save(OUT / "contact_sheet_production_bg_01_05.png", quality=95)


if __name__ == "__main__":
    fit(
        r"C:\Users\maruk\OneDrive\デスクトップ\参考資料\CT2.JPG",
        OUT / "bg_01_ct_opening_16x9.jpg",
        (0.55, 0.45),
    )
    fit(
        ROOT / "reel_assets" / "xray_clothing_wrinkles_buttons_v1" / "frame_07_metal_buttons_clothing_v1.png",
        OUT / "bg_05_metal_clothing_16x9.jpg",
        (0.5, 0.48),
    )
    contact_sheet()
