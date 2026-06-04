from __future__ import annotations

from collections import deque
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
SRC_DIR = ROOT / "LINEスタンプ"
OUT_DIR = ROOT / "LINEスタンプ_透過済み"
ZIP_PATH = ROOT / "LINEスタンプ_透過済み.zip"
PREVIEW_PATH = OUT_DIR / "preview_transparent_40.png"
FONT_PATH = Path(r"C:\Windows\Fonts\BIZ-UDGothicB.ttc")


def is_outer_background(r: int, g: int, b: int, a: int) -> bool:
    if a < 8:
        return True
    # Remove only the warm off-white sheet/background reachable from borders.
    # Sticker white outlines remain protected because flood fill does not cross
    # darker shadow/color edges around the sticker.
    return r >= 238 and g >= 235 and b >= 230


def flood_transparent_outer_bg(img: Image.Image) -> Image.Image:
    img = img.convert("RGBA")
    w, h = img.size
    px = img.load()
    seen = bytearray(w * h)
    q: deque[tuple[int, int]] = deque()

    def push(x: int, y: int) -> None:
        if x < 0 or y < 0 or x >= w or y >= h:
            return
        idx = y * w + x
        if seen[idx]:
            return
        r, g, b, a = px[x, y]
        if is_outer_background(r, g, b, a):
            seen[idx] = 1
            q.append((x, y))

    for x in range(w):
        push(x, 0)
        push(x, h - 1)
    for y in range(h):
        push(0, y)
        push(w - 1, y)

    while q:
        x, y = q.popleft()
        push(x + 1, y)
        push(x - 1, y)
        push(x, y + 1)
        push(x, y - 1)

    for y in range(h):
        for x in range(w):
            if seen[y * w + x]:
                r, g, b, _ = px[x, y]
                px[x, y] = (r, g, b, 0)
    return img


def make_preview(paths: list[Path]) -> None:
    cols = 8
    rows = 5
    cell_w, cell_h = 190, 178
    checker_a = (240, 240, 240)
    checker_b = (220, 220, 220)
    sheet = Image.new("RGB", (cell_w * cols, cell_h * rows), (246, 246, 246))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(str(FONT_PATH), 18) if FONT_PATH.exists() else ImageFont.load_default()

    for idx, path in enumerate(paths):
        image = Image.open(path).convert("RGBA")
        image.thumbnail((170, 150), Image.Resampling.LANCZOS)
        bg = Image.new("RGB", image.size, checker_a)
        bg_draw = ImageDraw.Draw(bg)
        block = 12
        for yy in range(0, bg.height, block):
            for xx in range(0, bg.width, block):
                if ((xx // block) + (yy // block)) % 2:
                    bg_draw.rectangle((xx, yy, xx + block - 1, yy + block - 1), fill=checker_b)
        bg = bg.convert("RGBA")
        bg.alpha_composite(image)

        col = idx % cols
        row = idx // cols
        x = col * cell_w + (cell_w - bg.width) // 2
        y = row * cell_h + 22
        sheet.paste(bg.convert("RGB"), (x, y))
        draw.text((col * cell_w + 8, row * cell_h + 4), f"{idx + 1:02d}", fill=(70, 70, 70), font=font)
    sheet.save(PREVIEW_PATH, quality=94)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    output_paths: list[Path] = []
    for i in range(1, 41):
        src = SRC_DIR / f"{i}.png"
        if not src.exists():
            raise FileNotFoundError(src)
        out = OUT_DIR / f"{i:02d}.png"
        result = flood_transparent_outer_bg(Image.open(src))
        if result.size != (370, 320):
            raise RuntimeError(f"{src.name} is {result.size}, expected 370x320")
        result.save(out)
        output_paths.append(out)

    make_preview(output_paths)

    with ZipFile(ZIP_PATH, "w", compression=ZIP_DEFLATED) as zf:
        for path in output_paths:
            zf.write(path, arcname=path.name)
        for extra_name in ("main.png", "tab.png"):
            extra = OUT_DIR / extra_name
            if extra.exists():
                zf.write(extra, arcname=extra.name)

    print(OUT_DIR)
    print(PREVIEW_PATH)
    print(ZIP_PATH)


if __name__ == "__main__":
    main()
