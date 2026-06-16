from pathlib import Path

from PIL import Image, ImageDraw


SRC = Path(r"C:\Users\maruk\.codex\generated_images\019ea037-7ee9-7760-bab4-9e55b9a839d4")
OUT = Path(
    r"F:\ANRYCAMPANY\reel_assets\bone_density_series\03_dxa_lumbar_femur_reason\generated_candidates_contact_sheet.png"
)


def main():
    files = sorted(SRC.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)[:8]
    thumb_w, thumb_h, label_h = 240, 360, 44
    cols = 4
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (thumb_w * cols, (thumb_h + label_h) * rows), "white")
    draw = ImageDraw.Draw(sheet)

    for idx, path in enumerate(files):
        im = Image.open(path).convert("RGB")
        im.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (idx % cols) * thumb_w
        y = (idx // cols) * (thumb_h + label_h)
        sheet.paste(im, (x + (thumb_w - im.width) // 2, y))
        draw.text((x + 8, y + thumb_h + 8), f"{idx + 1}: {path.name[:20]}", fill=(0, 0, 0))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT, quality=95)
    print(OUT)


if __name__ == "__main__":
    main()
