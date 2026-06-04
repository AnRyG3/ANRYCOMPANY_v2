from __future__ import annotations

from pathlib import Path

from PIL import Image


ROOT = Path(r"F:\ANRYCAMPANY")
SRC = ROOT / r"LINEスタンプ_透過済み\02.png"
OUT_DIR = ROOT / "LINEスタンプ_透過済み"


def trim_alpha(img: Image.Image) -> Image.Image:
    bbox = img.getbbox()
    if bbox is None:
        raise RuntimeError("empty image")
    return img.crop(bbox)


def fit_canvas(img: Image.Image, size: tuple[int, int], margin: int) -> Image.Image:
    img = trim_alpha(img.convert("RGBA"))
    cw, ch = size
    scale = min((cw - margin * 2) / img.width, (ch - margin * 2) / img.height)
    resized = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    canvas.alpha_composite(resized, ((cw - resized.width) // 2, (ch - resized.height) // 2))
    return canvas


def main() -> None:
    source = Image.open(SRC).convert("RGBA")
    main_img = fit_canvas(source, (240, 240), margin=8)
    tab_img = fit_canvas(source, (96, 74), margin=2)
    main_img.save(OUT_DIR / "main_240x240.png")
    tab_img.save(OUT_DIR / "tab_96x74.png")
    # LINE Creators Market common filenames.
    main_img.save(OUT_DIR / "main.png")
    tab_img.save(OUT_DIR / "tab.png")
    print(OUT_DIR / "main.png")
    print(OUT_DIR / "tab.png")


if __name__ == "__main__":
    main()
