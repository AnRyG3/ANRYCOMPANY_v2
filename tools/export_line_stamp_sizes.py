from pathlib import Path

from PIL import Image


SRC = Path(
    r"C:\Users\maruk\OneDrive\デスクトップ\Anry campany\02_LINEスタンプ\LINEスタンプ\Codex_image2_試作_20260516\01_otsukaresama_transparent.png"
)


def fit_to_canvas(crop: Image.Image, canvas_size: tuple[int, int], name: str) -> None:
    out_dir = SRC.parent
    canvas_w, canvas_h = canvas_size
    margin = 10
    scale = min(
        (canvas_w - margin * 2) / crop.width,
        (canvas_h - margin * 2) / crop.height,
    )
    new_w = max(1, int(crop.width * scale))
    new_h = max(1, int(crop.height * scale))
    resized = crop.resize((new_w, new_h), Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    canvas.alpha_composite(resized, ((canvas_w - new_w) // 2, (canvas_h - new_h) // 2))
    canvas.save(out_dir / name)


def main() -> None:
    image = Image.open(SRC).convert("RGBA")
    bbox = image.getbbox()
    if bbox is None:
        raise RuntimeError("The source image is fully transparent.")
    crop = image.crop(bbox)

    fit_to_canvas(crop, (370, 320), "01_otsukaresama_LINE_370x320.png")
    fit_to_canvas(crop, (240, 240), "main_240x240.png")
    fit_to_canvas(crop, (96, 74), "tab_96x74.png")


if __name__ == "__main__":
    main()
