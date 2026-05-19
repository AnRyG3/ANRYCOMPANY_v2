from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(
    r"C:\Users\maruk\OneDrive\デスクトップ\Anry campany\02_LINEスタンプ\LINEスタンプ\使いやすいキャラ特集_あんりぃ40_2026"
)
SRC_DIR = ROOT / "05_改訂版_chroma"
TRANSPARENT_DIR = ROOT / "06_改訂版_transparent"
TEXT_DIR = ROOT / "07_改訂版_文字入り_原寸"
LINE_DIR = ROOT / "08_改訂版_LINE提出サイズ_370x320"
PREVIEW_PATH = ROOT / "preview_revised_01_08_text.jpg"

FONT_PATH = Path(r"C:\Windows\Fonts\BIZ-UDGothicB.ttc")
ITEMS = [
    ("01_ohayou_rev_chroma.png", "01_ohayou_rev_text.png", "おはよう"),
    ("02_otsukaresama_rev_chroma.png", "02_otsukaresama_rev_text.png", "おつかれさま"),
    ("03_arigatou_rev_chroma.png", "03_arigatou_rev_text.png", "ありがとう"),
    ("04_ryoukai_rev_chroma.png", "04_ryoukai_rev_text.png", "了解です"),
    ("05_yoroshiku_rev_chroma.png", "05_yoroshiku_rev_text.png", "よろしく"),
    ("06_oyasumi_rev_chroma.png", "06_oyasumi_rev_text.png", "おやすみ"),
    ("07_gomenne_rev_chroma.png", "07_gomenne_rev_text.png", "ごめんね"),
    ("08_haai_rev_chroma.png", "08_haai_rev_text.png", "はーい"),
    ("09_ok_rev_chroma.png", "09_ok_rev_text.png", "OK"),
    ("10_unun_rev_chroma.png", "10_unun_rev_text.png", "うんうん"),
    ("11_sorena_rev_chroma.png", "11_sorena_rev_text.png", "それな"),
    ("12_wakaru_rev_chroma.png", "12_wakaru_rev_text.png", "わかる"),
    ("13_tashikani_rev_chroma.png", "13_tashikani_rev_text.png", "たしかに"),
    ("14_iine_rev_chroma.png", "14_iine_rev_text.png", "いいね"),
    ("15_sugoi_rev_chroma.png", "15_sugoi_rev_text.png", "すごい"),
    ("16_kawaii_rev_chroma.png", "16_kawaii_rev_text.png", "かわいい"),
    ("17_tasukaru_rev_chroma.png", "17_tasukaru_rev_text.png", "助かる"),
    ("18_arigatoo_rev_chroma.png", "18_arigatoo_rev_text.png", "ありがとー"),
    ("19_itsumo_arigatou_rev_chroma.png", "19_itsumo_arigatou_rev_text.png", "いつもありがとう"),
    ("20_murishinaidene_rev_chroma.png", "20_murishinaidene_rev_text.png", "無理しないでね"),
    ("21_daijoubu_rev_chroma.png", "21_daijoubu_rev_text.png", "大丈夫？"),
    ("22_yukkuri_yasundene_rev_chroma.png", "22_yukkuri_yasundene_rev_text.png", "ゆっくり休んでね"),
    ("23_ganbatte_rev_chroma.png", "23_ganbatte_rev_text.png", "がんばって"),
    ("24_ouenshiteru_rev_chroma.png", "24_ouenshiteru_rev_text.png", "応援してる"),
    ("25_fight_rev_chroma.png", "25_fight_rev_text.png", "ファイト"),
    ("26_omedetou_rev_chroma.png", "26_omedetou_rev_text.png", "おめでとう"),
    ("27_yattaa_rev_chroma.png", "27_yattaa_rev_text.png", "やったー"),
    ("28_ureshii_rev_chroma.png", "28_ureshii_rev_text.png", "うれしい"),
    ("29_ehehe_rev_chroma.png", "29_ehehe_rev_text.png", "えへへ"),
    ("30_chira_rev_chroma.png", "30_chira_rev_text.png", "ちらっ"),
    ("31_jii_rev_chroma.png", "31_jii_rev_text.png", "じー"),
    ("32_mattemasu_rev_chroma.png", "32_mattemasu_rev_text.png", "まってます"),
    ("33_ittekimasu_rev_chroma.png", "33_ittekimasu_rev_text.png", "いってきます"),
    ("34_itterasshai_rev_chroma.png", "34_itterasshai_rev_text.png", "いってらっしゃい"),
    ("35_tadaima_rev_chroma.png", "35_tadaima_rev_text.png", "ただいま"),
    ("36_okaeri_rev_chroma.png", "36_okaeri_rev_text.png", "おかえり"),
    ("37_gohan_rev_chroma.png", "37_gohan_rev_text.png", "ごはん？"),
    ("38_nemui_rev_chroma.png", "38_nemui_rev_text.png", "ねむい"),
    ("39_hp0_rev_chroma.png", "39_hp0_rev_text.png", "HP0です"),
    ("40_matane_rev_chroma.png", "40_matane_rev_text.png", "またね"),
]


def remove_green_background(image: Image.Image) -> Image.Image:
    image = image.convert("RGBA")
    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, a = pixels[x, y]
            if g > 160 and r < 110 and b < 130:
                pixels[x, y] = (r, g, b, 0)
    return image


def crop_to_content(image: Image.Image) -> Image.Image:
    bbox = image.getbbox()
    if bbox is None:
        raise RuntimeError("Image is empty after transparency processing.")
    return image.crop(bbox)


def fit_subject(subject: Image.Image, canvas_size: tuple[int, int], top_reserved: int) -> Image.Image:
    canvas_w, canvas_h = canvas_size
    side_margin = 8
    bottom_margin = 8
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
    for size in range(56, 20, -2):
        font = ImageFont.truetype(str(FONT_PATH), size)
        bbox = draw.textbbox((0, 0), text, font=font, stroke_width=5)
        if bbox[2] - bbox[0] <= max_width and bbox[3] - bbox[1] <= max_height:
            return font
    return ImageFont.truetype(str(FONT_PATH), 22)


def add_text(image: Image.Image, text: str) -> Image.Image:
    out = image.copy()
    draw = ImageDraw.Draw(out)
    font = fit_font(draw, text, max_width=340, max_height=58)
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
    cols = 4
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
        transparent = remove_green_background(Image.open(SRC_DIR / src_name))
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
