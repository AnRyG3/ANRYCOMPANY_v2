from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
OUT = ROOT / "reel_assets" / "companion_waiting_role_07_telop"
FONT = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"


def main():
    files = sorted(OUT.glob("frame*_telop.png"))
    thumbs = []
    for path in files:
        img = Image.open(path).convert("RGB")
        img.thumbnail((220, 392), Image.Resampling.LANCZOS)
        thumbs.append((path.name, img.copy()))

    cols = 4
    rows = (len(thumbs) + cols - 1) // cols
    cell_w, cell_h = 250, 450
    sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(str(FONT), 18)

    for idx, (name, img) in enumerate(thumbs):
        col = idx % cols
        row = idx // cols
        x = col * cell_w + (cell_w - img.width) // 2
        y = row * cell_h + 28
        sheet.paste(img, (x, y))
        draw.text((col * cell_w + 12, row * cell_h + 6), name, fill=(22, 42, 67), font=font)

    sheet.save(OUT / "_contact_sheet_telop.png", quality=95)


if __name__ == "__main__":
    main()
