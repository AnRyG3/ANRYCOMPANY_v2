from pathlib import Path
import shutil

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(r"F:\ANRYCAMPANY")
REF = Path(r"C:\Users\maruk\OneDrive\デスクトップ\参考資料")
GEN = Path(r"C:\Users\maruk\.codex\generated_images\019f3715-1d9b-7320-9857-d0caff7a82cb")
OUT = ROOT / "reel_assets" / "ct_longform_youtube_samples" / "production_bg_sample5"
FONT = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"
W, H = 1920, 1080


def fit(src, centering=(0.5, 0.5)):
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    return ImageOps.fit(im, (W, H), Image.Resampling.LANCZOS, centering=centering)


def blur_except_ct():
    base = fit(REF / "CT2.JPG", (0.55, 0.45))
    blurred = base.filter(ImageFilter.GaussianBlur(16))
    # Keep the main CT gantry and table sharp, blur the walls, shelves, floor, and peripheral clutter.
    mask = Image.new("L", (W, H), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((460, 95, 1785, 1015), fill=255)
    draw.polygon([(0, 610), (900, 610), (1140, 1080), (0, 1080)], fill=255)
    draw.rectangle((500, 130, 1760, 1040), outline=255, width=80)
    mask = mask.filter(ImageFilter.GaussianBlur(36))
    out = Image.composite(base, blurred, mask)
    out.save(OUT / "bg_01_ct_opening_device_focus.jpg", quality=95)

    gantry_blurred = out.filter(ImageFilter.GaussianBlur(18))
    gantry_mask = Image.new("L", (W, H), 0)
    gantry_draw = ImageDraw.Draw(gantry_mask)
    # Blur only the inside of the gantry, where background items are visible.
    gantry_draw.ellipse((820, 360, 1225, 750), fill=255)
    gantry_mask = gantry_mask.filter(ImageFilter.GaussianBlur(10))
    gantry_out = Image.composite(gantry_blurred, out, gantry_mask)
    gantry_out.save(OUT / "bg_01_ct_opening_device_focus_gantry_blur.jpg", quality=95)


def copy_latest_metal_check():
    latest = max(GEN.glob("*.png"), key=lambda p: p.stat().st_mtime)
    shutil.copy2(latest, OUT / "bg_05_metal_check_tray.png")


def contact_sheet():
    files = [
        OUT / "bg_01_ct_opening_device_focus_gantry_blur.jpg",
        OUT / "bg_02_waiting_room.png",
        OUT / "bg_03_reception.png",
        OUT / "bg_04_radiology_waiting.png",
        OUT / "bg_05_metal_check_tray.png",
    ]
    labels = ["01 CT装置だけ鮮明", "02 待合・不安", "03 受付", "04 放射線科待合", "05 金属確認"]
    tw, th = 384, 216
    sheet = Image.new("RGB", (tw * 5, 270), (238, 242, 242))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(str(FONT), 24)
    for i, path in enumerate(files):
        im = ImageOps.fit(Image.open(path).convert("RGB"), (tw, th), Image.Resampling.LANCZOS)
        x = i * tw
        sheet.paste(im, (x, 0))
        draw.text((x + 16, 226), labels[i], font=font, fill=(20, 45, 68))
    sheet.save(OUT / "contact_sheet_production_bg_01_05_v2.png", quality=95)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    blur_except_ct()
    copy_latest_metal_check()
    contact_sheet()
