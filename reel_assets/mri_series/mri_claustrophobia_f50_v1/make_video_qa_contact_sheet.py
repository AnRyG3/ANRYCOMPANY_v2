from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BASE = Path(__file__).resolve().parent
QA_DIR = BASE / "_video_work" / "qa_frames"
OUT = BASE / "_video_work" / "video_qa_contact_sheet.jpg"


def main() -> None:
    files = sorted(QA_DIR.glob("qa_*.jpg"))
    cols = 5
    label_h = 28
    pad = 18
    cell_w = 270
    cell_h = 480 + label_h
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell_w + pad * 2, rows * cell_h + pad * 2), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for i, path in enumerate(files):
        img = Image.open(path).convert("RGB")
        col = i % cols
        row = i // cols
        x = pad + col * cell_w
        y = pad + row * cell_h
        sheet.paste(img, (x, y))
        draw.text((x + 8, y + 486), path.stem, fill=(20, 20, 20), font=font)
    sheet.save(OUT, quality=92)
    print(OUT)


if __name__ == "__main__":
    main()
