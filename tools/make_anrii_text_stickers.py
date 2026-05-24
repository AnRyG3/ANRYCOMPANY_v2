from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(
    r"F:\ANRYCAMPANY\02_LINE繧ｹ繧ｿ繝ｳ繝予LINE繧ｹ繧ｿ繝ｳ繝予菴ｿ縺・ｄ縺吶＞繧ｭ繝｣繝ｩ迚ｹ髮・縺ゅｓ繧翫＜40_2026"
)
SRC_DIR = ROOT / "01_繧ｭ繝｣繝ｩ邨ｵ_chroma"
TRANSPARENT_DIR = ROOT / "02_繧ｭ繝｣繝ｩ邨ｵ_transparent"
TEXT_DIR = ROOT / "03_譁・ｭ怜・繧垣蜴溷ｯｸ"
LINE_DIR = ROOT / "04_LINE謠仙・繧ｵ繧､繧ｺ_370x320"
PREVIEW_PATH = ROOT / "preview_first4_text.jpg"

FONT_PATH = Path(r"C:\Windows\Fonts\BIZ-UDGothicB.ttc")
ITEMS = [
    ("01_ohayou_chroma.png", "01_ohayou_text.png", "縺翫・繧医≧"),
    ("02_otsukaresama_chroma.png", "02_otsukaresama_text.png", "縺翫▽縺九ｌ縺輔∪"),
    ("03_arigatou_chroma.png", "03_arigatou_text.png", "縺ゅｊ縺後→縺・),
    ("04_ryoukai_chroma.png", "04_ryoukai_text.png", "莠・ｧ｣縺ｧ縺・),
    ("05_yoroshiku_chroma.png", "05_yoroshiku_text.png", "繧医ｍ縺励￥"),
    ("06_oyasumi_chroma.png", "06_oyasumi_text.png", "縺翫ｄ縺吶∩"),
    ("07_gomenne_chroma.png", "07_gomenne_text.png", "縺斐ａ繧薙・"),
    ("08_haai_chroma.png", "08_haai_text.png", "縺ｯ繝ｼ縺・),
    ("09_ok_chroma.png", "09_ok_text.png", "OK"),
    ("10_unun_chroma.png", "10_unun_text.png", "縺・ｓ縺・ｓ"),
    ("11_sorena_chroma.png", "11_sorena_text.png", "縺昴ｌ縺ｪ"),
    ("12_wakaru_chroma.png", "12_wakaru_text.png", "繧上°繧・),
    ("13_tashikani_chroma.png", "13_tashikani_text.png", "縺溘＠縺九↓"),
    ("14_iine_chroma.png", "14_iine_text.png", "縺・＞縺ｭ"),
    ("15_sugoi_chroma.png", "15_sugoi_text.png", "縺吶＃縺・),
    ("16_kawaii_chroma.png", "16_kawaii_text.png", "縺九ｏ縺・＞"),
    ("17_tasukaru_chroma.png", "17_tasukaru_text.png", "蜉ｩ縺九ｋ"),
    ("18_arigatoo_chroma.png", "18_arigatoo_text.png", "縺ゅｊ縺後→繝ｼ"),
    ("19_itsumo_arigatou_chroma.png", "19_itsumo_arigatou_text.png", "縺・▽繧ゅ≠繧翫′縺ｨ縺・),
    ("20_murishinaidene_chroma.png", "20_murishinaidene_text.png", "辟｡逅・＠縺ｪ縺・〒縺ｭ"),
]


def remove_green_background(image: Image.Image) -> Image.Image:
    image = image.convert("RGBA")
    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, a = pixels[x, y]
            # The generated chroma background has slight variation, so use a soft key.
            if g > 170 and r < 90 and b < 120:
                pixels[x, y] = (r, g, b, 0)
    return image


def crop_to_content(image: Image.Image) -> Image.Image:
    bbox = image.getbbox()
    if bbox is None:
        raise RuntimeError("Image is empty after transparency processing.")
    return image.crop(bbox)


def fit_subject(subject: Image.Image, canvas_size: tuple[int, int], top_reserved: int) -> Image.Image:
    canvas_w, canvas_h = canvas_size
    side_margin = 12
    bottom_margin = 10
    available_w = canvas_w - side_margin * 2
    available_h = canvas_h - top_reserved - bottom_margin
    scale = min(available_w / subject.width, available_h / subject.height)
    new_size = (max(1, int(subject.width * scale)), max(1, int(subject.height * scale)))
    resized = subject.resize(new_size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    x = (canvas_w - new_size[0]) // 2
    y = top_reserved + (available_h - new_size[1]) // 2
    canvas.alpha_composite(resized, (x, y))
    return canvas


def fit_font(draw: ImageDraw.ImageDraw, text: str, max_width: int, max_height: int) -> ImageFont.FreeTypeFont:
    for size in range(58, 20, -2):
        font = ImageFont.truetype(str(FONT_PATH), size)
        bbox = draw.textbbox((0, 0), text, font=font, stroke_width=4)
        if bbox[2] - bbox[0] <= max_width and bbox[3] - bbox[1] <= max_height:
            return font
    return ImageFont.truetype(str(FONT_PATH), 22)


def add_text(image: Image.Image, text: str) -> Image.Image:
    out = image.copy()
    draw = ImageDraw.Draw(out)
    font = fit_font(draw, text, max_width=330, max_height=58)
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=5)
    text_w = bbox[2] - bbox[0]
    x = (out.width - text_w) // 2
    y = 7
    draw.text(
        (x, y),
        text,
        font=font,
        fill=(94, 58, 38, 255),
        stroke_width=5,
        stroke_fill=(255, 255, 255, 255),
    )
    return out


def make_preview(paths: list[Path]) -> None:
    cell_w, cell_h = 330, 310
    cols = 4 if len(paths) > 4 else 2
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (cell_w * cols, cell_h * rows), "white")
    for i, path in enumerate(paths):
        image = Image.open(path).convert("RGBA")
        preview = Image.new("RGBA", image.size, (245, 245, 245, 255))
        preview.alpha_composite(image)
        preview = preview.convert("RGB")
        preview.thumbnail((300, 280))
        x = (i % cols) * cell_w + (cell_w - preview.width) // 2
        y = (i // cols) * cell_h + 10
        sheet.paste(preview, (x, y))
    sheet.save(PREVIEW_PATH, quality=92)


def main() -> None:
    TRANSPARENT_DIR.mkdir(exist_ok=True)
    TEXT_DIR.mkdir(exist_ok=True)
    LINE_DIR.mkdir(exist_ok=True)
    preview_paths = []

    for src_name, out_name, text in ITEMS:
        src = SRC_DIR / src_name
        chroma = Image.open(src)
        transparent = remove_green_background(chroma)
        transparent.save(TRANSPARENT_DIR / src_name.replace("_chroma", "_transparent"))

        subject = crop_to_content(transparent)
        canvas = fit_subject(subject, (370, 320), top_reserved=62)
        text_image = add_text(canvas, text)
        text_image.save(TEXT_DIR / out_name)
        text_image.save(LINE_DIR / out_name.replace("_text", "_LINE_370x320"))
        preview_paths.append(TEXT_DIR / out_name)

    make_preview(preview_paths)


if __name__ == "__main__":
    main()


