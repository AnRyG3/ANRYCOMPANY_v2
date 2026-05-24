from pathlib import Path

from PIL import Image


PROJECT = Path(
    r"F:\ANRYCAMPANY"
    r"\02_LINE繧ｹ繧ｿ繝ｳ繝予LINE繧ｹ繧ｿ繝ｳ繝予菴ｿ縺・ｄ縺吶＞繧ｭ繝｣繝ｩ迚ｹ髮・縺ゅｓ繧翫＜40_2026"
)
SRC = PROJECT / "06_謾ｹ險ら沿_transparent"
OUT = PROJECT / "09_繝｡繧､繝ｳ_繧ｿ繝也判蜒・


def fit_alpha_image(src_path: Path, size: tuple[int, int], padding: int) -> Image.Image:
    image = Image.open(src_path).convert("RGBA")
    bbox = image.getbbox()
    if bbox is None:
        raise ValueError(f"No visible pixels: {src_path}")

    subject = image.crop(bbox)
    target_w = size[0] - padding * 2
    target_h = size[1] - padding * 2
    scale = min(target_w / subject.width, target_h / subject.height)
    resized = subject.resize(
        (max(1, round(subject.width * scale)), max(1, round(subject.height * scale))),
        Image.Resampling.LANCZOS,
    )

    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    x = (size[0] - resized.width) // 2
    y = (size[1] - resized.height) // 2
    canvas.alpha_composite(resized, (x, y))
    return canvas


def main() -> None:
    OUT.mkdir(exist_ok=True)

    main_image = fit_alpha_image(SRC / "27_yattaa_rev_transparent.png", (240, 240), 10)
    tab_image = fit_alpha_image(SRC / "40_matane_rev_transparent.png", (96, 74), 2)

    main_image.save(OUT / "main_240x240.png")
    tab_image.save(OUT / "tab_96x74.png")


if __name__ == "__main__":
    main()


