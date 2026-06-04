from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from build_keigo_work_stamps import CANVAS, WHITE, key_green_to_alpha, trim_alpha


ROOT = Path(r"F:\ANRYCAMPANY")
DIR = ROOT / "02_LINEスタンプ" / "あんりぃ_LINEスタンプ制作工場" / "04_完成画像" / "敬語・仕事返信スタンプ_あんりぃ40" / "07_再設計33-40"
ASSET_DIR = DIR / "生成素材"
FONT = Path(r"C:\Windows\Fonts\meiryob.ttc")
BROWN = (92, 60, 48, 255)

SAMPLES = [
    ("33", "無理しないで\nください", "33_murishinaide_chroma.png", (42, 91, 150, 255)),
    ("34", "ご自愛\nください", "34_jiai_chroma.png", (47, 120, 92, 255)),
    ("35", "応援して\nいます", "35_ouen_chroma.png", (47, 120, 92, 255)),
    ("36", "さすがです", "36_sasuga_chroma.png", (47, 120, 92, 255)),
    ("37", "素敵です", "37_suteki_chroma.png", (47, 120, 92, 255)),
    ("38", "いいですね", "38_iidesune_chroma.png", (47, 120, 92, 255)),
    ("39", "またお願い\nします", "39_mata_onegai_chroma.png", (121, 82, 65, 255)),
    ("40", "失礼します", "40_shitsurei_chroma.png", (121, 82, 65, 255)),
]


def draw_text(draw: ImageDraw.ImageDraw, text: str, color) -> None:
    lines = text.split("\n")
    for size in range(50, 23, -1):
        font = ImageFont.truetype(str(FONT), size)
        widths = [draw.textbbox((0, 0), line, font=font)[2] for line in lines]
        line_height = draw.textbbox((0, 0), "あ", font=font)[3] + 1
        if max(widths) <= 344 and line_height * len(lines) <= 103:
            break
    top = max(2, (105 - line_height * len(lines)) // 2)
    for index, line in enumerate(lines):
        width = draw.textbbox((0, 0), line, font=font)[2]
        x = (CANVAS[0] - width) // 2
        y = top + index * line_height
        draw.text((x + 2, y + 3), line, font=font, fill=BROWN, stroke_width=7, stroke_fill=WHITE)
        draw.text((x, y), line, font=font, fill=color, stroke_width=4, stroke_fill=WHITE)


def compose(text: str, source_name: str, color) -> Image.Image:
    source = trim_alpha(key_green_to_alpha(Image.open(ASSET_DIR / source_name)))
    ratio = min(350 / source.width, 210 / source.height)
    source = source.resize((int(source.width * ratio), int(source.height * ratio)), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw_text(ImageDraw.Draw(canvas), text, color)
    canvas.alpha_composite(source, ((CANVAS[0] - source.width) // 2, CANVAS[1] - source.height - 2))
    return canvas


def main() -> None:
    DIR.mkdir(parents=True, exist_ok=True)
    columns = 4
    rows = 2
    preview = Image.new("RGBA", (CANVAS[0] * columns, CANVAS[1] * rows), (246, 244, 241, 255))
    draw = ImageDraw.Draw(preview)
    label_font = ImageFont.truetype(str(FONT), 18)
    for index, (number, text, source_name, color) in enumerate(SAMPLES):
        image = compose(text, source_name, color)
        image.save(DIR / f"{number}.png")
        x = (index % columns) * CANVAS[0]
        y = (index // columns) * CANVAS[1]
        preview.alpha_composite(image, (x, y))
        draw.text((x + 8, y + 6), number, font=label_font, fill=(100, 96, 92, 255))
    preview.convert("RGB").save(DIR / "preview_keigo_redesign_33_40.png", quality=95)
    print("created=8")


if __name__ == "__main__":
    main()

