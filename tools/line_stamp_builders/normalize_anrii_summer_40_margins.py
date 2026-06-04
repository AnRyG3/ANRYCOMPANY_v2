from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
BASE = ROOT / r"02_LINEスタンプ\あんりぃ_LINEスタンプ制作工場\04_完成画像\夏を感じるスタンプ_あんりぃ40"
SRC_DIR = BASE / "03_40個完成"
OUT_DIR = BASE / "04_LINE提出用_余白調整済み"
PREVIEW = OUT_DIR / "preview_all_40_margin_normalized.png"
FONT = Path(r"C:\Windows\Fonts\BIZ-UDGothicB.ttc")


def trim_alpha(img: Image.Image) -> Image.Image:
    bbox = img.getbbox()
    if bbox is None:
        raise RuntimeError("empty image")
    return img.crop(bbox)


def normalize(img: Image.Image, canvas_size: tuple[int, int] = (370, 320)) -> Image.Image:
    img = trim_alpha(img.convert("RGBA"))
    cw, ch = canvas_size
    # A slightly conservative box makes left/right/top/bottom safety margins
    # consistent and prevents text outlines from touching the canvas edge.
    max_w = 326
    max_h = 282
    scale = min(max_w / img.width, max_h / img.height)
    new_size = (max(1, int(img.width * scale)), max(1, int(img.height * scale)))
    resized = img.resize(new_size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    canvas.alpha_composite(resized, ((cw - resized.width) // 2, (ch - resized.height) // 2))
    return canvas


def make_preview(paths: list[Path]) -> None:
    cols = 8
    rows = 5
    cell_w, cell_h = 190, 178
    sheet = Image.new("RGB", (cell_w * cols, cell_h * rows), (246, 246, 246))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(str(FONT), 18) if FONT.exists() else ImageFont.load_default()
    for idx, path in enumerate(paths):
        img = Image.open(path).convert("RGBA")
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        bg.alpha_composite(img)
        bg.thumbnail((170, 150), Image.Resampling.LANCZOS)
        col = idx % cols
        row = idx // cols
        x = col * cell_w + (cell_w - bg.width) // 2
        y = row * cell_h + 22
        sheet.paste(bg.convert("RGB"), (x, y))
        draw.text((col * cell_w + 8, row * cell_h + 4), f"{idx + 1:02d}", fill=(80, 80, 80), font=font)
    sheet.save(PREVIEW, quality=94)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_paths: list[Path] = []
    for index in range(1, 41):
        src = SRC_DIR / f"{index:02d}.png"
        if not src.exists():
            raise FileNotFoundError(src)
        out = OUT_DIR / f"{index:02d}.png"
        normalized = normalize(Image.open(src))
        normalized.save(out)
        out_paths.append(out)
    make_preview(out_paths)
    # Keep the previous assembled preview nearby for comparison.
    old_preview = SRC_DIR / "preview_all_40_submission_candidates.png"
    if old_preview.exists():
        shutil.copy2(old_preview, OUT_DIR / "preview_before_margin_normalization.png")
    print(PREVIEW)
    print(OUT_DIR)


if __name__ == "__main__":
    main()
