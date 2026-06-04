from __future__ import annotations

from collections import deque
from pathlib import Path

from PIL import Image


ROOT = Path(r"F:\ANRYCAMPANY")
IN_PATH = ROOT / r"02_LINEスタンプ\あんりぃ_LINEスタンプ制作工場\04_完成画像\夏を感じるスタンプ_あんりぃ40\04_提出用候補_16-20\submission_quality_preview_16_20_sheet.png"
OUT_DIR = ROOT / r"02_LINEスタンプ\あんりぃ_LINEスタンプ制作工場\04_完成画像\夏を感じるスタンプ_あんりぃ40\04_提出用候補_16-20\個別PNG"
PREVIEW = OUT_DIR / "preview_submission_16_20_individual.png"

ITEMS = [
    ("16_hiyake_shita_submission_candidate.png", (25, 20, 540, 485)),
    ("17_mushiyoke_kanryou_submission_candidate.png", (590, 20, 1115, 485)),
    ("18_kayui_submission_candidate.png", (1135, 15, 1635, 485)),
    ("19_yuusuzumi_submission_candidate.png", (285, 490, 830, 925)),
    ("20_ii_tenki_submission_candidate.png", (865, 500, 1375, 925)),
]


def is_outer_bg(r: int, g: int, b: int, a: int) -> bool:
    return a < 10 or (r > 236 and g > 232 and b > 226)


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
        if is_outer_bg(r, g, b, a):
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


def trim_alpha(img: Image.Image) -> Image.Image:
    bbox = img.getbbox()
    if bbox is None:
        raise RuntimeError("empty crop")
    pad = 10
    x0, y0, x1, y1 = bbox
    return img.crop((max(0, x0 - pad), max(0, y0 - pad), min(img.width, x1 + pad), min(img.height, y1 + pad)))


def fit_line_canvas(img: Image.Image, size: tuple[int, int] = (370, 320)) -> Image.Image:
    img = trim_alpha(img)
    cw, ch = size
    margin = 8
    scale = min((cw - margin * 2) / img.width, (ch - margin * 2) / img.height)
    img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    canvas.alpha_composite(img, ((cw - img.width) // 2, (ch - img.height) // 2))
    return canvas


def make_preview(paths: list[Path]) -> None:
    cell_w, cell_h = 270, 245
    sheet = Image.new("RGB", (cell_w * 3, cell_h * 2), (246, 246, 246))
    for i, path in enumerate(paths):
        img = Image.open(path).convert("RGBA")
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        bg.alpha_composite(img)
        bg.thumbnail((245, 220), Image.Resampling.LANCZOS)
        x = (i % 3) * cell_w + (cell_w - bg.width) // 2
        y = (i // 3) * cell_h + (cell_h - bg.height) // 2
        sheet.paste(bg.convert("RGB"), (x, y))
    sheet.save(PREVIEW, quality=94)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sheet = Image.open(IN_PATH).convert("RGBA")
    out_paths: list[Path] = []
    for name, box in ITEMS:
        final = fit_line_canvas(flood_transparent_outer_bg(sheet.crop(box)))
        out_path = OUT_DIR / name
        final.save(out_path)
        out_paths.append(out_path)
    make_preview(out_paths)
    print(PREVIEW)
    for path in out_paths:
        print(path)


if __name__ == "__main__":
    main()
