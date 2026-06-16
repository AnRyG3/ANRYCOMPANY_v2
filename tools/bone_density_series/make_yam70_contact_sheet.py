from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "bone_density_series" / "06_yam70_meaning"
BG_DIR = ASSET_DIR / "generated_backgrounds"
OUT = ASSET_DIR / "_contact_sheet_generated_backgrounds.png"


def font(size):
    for path in (r"C:\Windows\Fonts\meiryob.ttc", r"C:\Windows\Fonts\meiryo.ttc"):
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def main():
    files = sorted(BG_DIR.glob("bg_*_no_text.png"))
    thumb_w, thumb_h, label_h = 270, 480, 34
    cols = 4
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (thumb_w * cols, (thumb_h + label_h) * rows), (245, 247, 250))
    draw = ImageDraw.Draw(sheet)
    label_font = font(20)
    for idx, path in enumerate(files):
        image = Image.open(path).convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (idx % cols) * thumb_w
        y = (idx // cols) * (thumb_h + label_h)
        sheet.paste(image, (x, y))
        draw.text((x + 8, y + thumb_h + 7), path.name, fill=(30, 40, 50), font=label_font)
    sheet.save(OUT, quality=95)
    print(OUT)


if __name__ == "__main__":
    main()
