from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BASE = Path(__file__).resolve().parent
TEL_OP = BASE / "telop_frames"
OUT = BASE / "telop_contact_sheet.jpg"


def main() -> None:
    files = sorted(TEL_OP.glob("telop_*.png"))
    thumbs = []
    for path in files:
        img = Image.open(path).convert("RGB")
        img.thumbnail((270, 480))
        thumbs.append((path, img.copy()))

    cols = 5
    rows = (len(thumbs) + cols - 1) // cols
    label_h = 34
    pad = 18
    cell_w = 270
    cell_h = 480 + label_h
    sheet = Image.new("RGB", (cols * cell_w + pad * 2, rows * cell_h + pad * 2), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()

    for i, (path, img) in enumerate(thumbs):
        col = i % cols
        row = i // cols
        x = pad + col * cell_w
        y = pad + row * cell_h
        sheet.paste(img, (x + (cell_w - img.width) // 2, y))
        draw.text((x + 8, y + 486), path.stem, fill=(20, 20, 20), font=font)

    sheet.save(OUT, quality=92)
    print(OUT)


if __name__ == "__main__":
    main()
