from pathlib import Path
from shutil import copy2

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
BASE = ROOT / "02_LINEスタンプ" / "あんりぃ_LINEスタンプ制作工場" / "04_完成画像" / "敬語・仕事返信スタンプ_あんりぃ40"
OUT = BASE / "08_再設計40確認"
FONT = Path(r"C:\Windows\Fonts\meiryob.ttc")
CANVAS = (370, 320)

SOURCES = [
    BASE / "03_再設計試作3個",
    BASE / "04_再設計09-16",
    BASE / "05_再設計17-24",
    BASE / "06_再設計25-32",
    BASE / "07_再設計33-40",
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for n in range(1, 41):
        name = f"{n:02d}.png"
        for src_dir in SOURCES:
            src = src_dir / name
            if src.exists():
                copy2(src, OUT / name)
                break

    files = [OUT / f"{n:02d}.png" for n in range(1, 41)]
    missing = [f.name for f in files if not f.exists()]
    if missing:
        raise SystemExit(f"missing: {missing}")

    columns = 5
    rows = 8
    preview = Image.new("RGBA", (CANVAS[0] * columns, CANVAS[1] * rows), (246, 244, 241, 255))
    draw = ImageDraw.Draw(preview)
    font = ImageFont.truetype(str(FONT), 22)
    for idx, path in enumerate(files):
        image = Image.open(path).convert("RGBA")
        x = (idx % columns) * CANVAS[0]
        y = (idx // columns) * CANVAS[1]
        preview.alpha_composite(image, (x, y))
        draw.text((x + 8, y + 7), path.stem, font=font, fill=(95, 92, 88, 255))
    preview.convert("RGB").save(OUT / "preview_keigo_redesign_all_40.png", quality=95)
    print("created=40")
    print(OUT)


if __name__ == "__main__":
    main()

