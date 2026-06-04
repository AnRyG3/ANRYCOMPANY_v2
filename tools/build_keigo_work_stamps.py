from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
BASE_DIR = ROOT / "02_LINEスタンプ" / "あんりぃ_LINEスタンプ制作工場" / "01_ベース画像" / "ベース画像_採用候補5枚"
POSE_DIR = ROOT / "02_LINEスタンプ" / "LINEスタンプ完成形" / "使いやすいキャラ特集_あんりぃ40_2026" / "02_キャラ絵_transparent"
OUT_DIR = ROOT / "02_LINEスタンプ" / "あんりぃ_LINEスタンプ制作工場" / "04_完成画像" / "敬語・仕事返信スタンプ_あんりぃ40" / "01_試作8個"
FONT_PATH = Path(r"C:\Windows\Fonts\meiryob.ttc")

CANVAS = (370, 320)
WHITE = (255, 255, 255, 255)
BROWN = (92, 60, 48, 255)


STAMPS = [
    ("01", "おつかれ\nさまです", "03_real_base_front_sit_necklace.png", (42, 102, 157, 255), "soft"),
    ("02", "ありがとう\nございます", "04_real_base_threequarter_tongue_necklace.png", (47, 120, 92, 255), "sparkle"),
    ("03", "承知しました", "05_real_base_standing_plain.png", (42, 91, 150, 255), "check"),
    ("05", "よろしく\nお願いします", "03_real_base_front_sit_necklace.png", (121, 82, 65, 255), "soft"),
    ("06", "確認します", "05_real_base_standing_plain.png", (44, 116, 92, 255), "document"),
    ("07", "少々お待ち\nください", "03_real_base_front_sit_necklace.png", (50, 99, 153, 255), "clock"),
    ("08", "助かります", "04_real_base_threequarter_tongue_necklace.png", (47, 120, 92, 255), "sparkle"),
    ("29", "申し訳\nありません", "03_real_base_front_sit_necklace.png", (117, 82, 119, 255), "sweat"),
]


def key_green_to_alpha(source: Image.Image) -> Image.Image:
    image = source.convert("RGBA")
    px = image.load()
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, _ = px[x, y]
            green_strength = g - max(r, b)
            if g > 170 and green_strength > 60:
                alpha = max(0, min(255, int((125 - green_strength) * 4)))
                px[x, y] = (r, min(g, max(r, b) + 18), b, alpha)
    return image


def trim_alpha(image: Image.Image) -> Image.Image:
    box = image.getbbox()
    return image.crop(box) if box else image


def fit(image: Image.Image, max_w: int, max_h: int) -> Image.Image:
    image = trim_alpha(image)
    ratio = min(max_w / image.width, max_h / image.height)
    return image.resize((max(1, int(image.width * ratio)), max(1, int(image.height * ratio))), Image.Resampling.LANCZOS)


def text_box(draw: ImageDraw.ImageDraw, lines: Iterable[str], max_width: int, max_height: int) -> tuple[ImageFont.FreeTypeFont, list[str], int]:
    lines = list(lines)
    for size in range(56, 23, -1):
        font = ImageFont.truetype(str(FONT_PATH), size=size)
        widths = [draw.textbbox((0, 0), line, font=font, stroke_width=0)[2] for line in lines]
        line_h = draw.textbbox((0, 0), "あ", font=font)[3] + 2
        if max(widths) <= max_width and line_h * len(lines) <= max_height:
            return font, lines, line_h
    font = ImageFont.truetype(str(FONT_PATH), size=24)
    return font, lines, 28


def draw_text_centered(draw: ImageDraw.ImageDraw, text: str, color: tuple[int, int, int, int]) -> int:
    lines = text.split("\n")
    font, lines, line_h = text_box(draw, lines, max_width=338, max_height=111)
    total_h = line_h * len(lines)
    top = 4 + max(0, (108 - total_h) // 2)
    for index, line in enumerate(lines):
        box = draw.textbbox((0, 0), line, font=font, stroke_width=0)
        width = box[2] - box[0]
        x = (CANVAS[0] - width) // 2
        y = top + index * line_h
        draw.text((x + 2, y + 3), line, font=font, fill=BROWN, stroke_width=7, stroke_fill=WHITE)
        draw.text((x, y), line, font=font, fill=color, stroke_width=4, stroke_fill=WHITE)
    return top + total_h


def star(draw: ImageDraw.ImageDraw, x: int, y: int, color=(242, 192, 64, 230)) -> None:
    draw.polygon([(x, y - 10), (x + 3, y - 3), (x + 10, y), (x + 3, y + 3), (x, y + 10), (x - 3, y + 3), (x - 10, y), (x - 3, y - 3)], fill=color)


def draw_accent(draw: ImageDraw.ImageDraw, accent: str) -> None:
    if accent == "sparkle":
        star(draw, 42, 122)
        star(draw, 325, 145, (255, 213, 94, 220))
        draw.ellipse((55, 142, 61, 148), fill=(247, 191, 79, 210))
    elif accent == "check":
        draw.ellipse((300, 120, 350, 170), fill=(222, 243, 235, 225), outline=(64, 142, 111, 255), width=3)
        draw.line((313, 145, 325, 156, 340, 134), fill=(50, 126, 95, 255), width=7, joint="curve")
    elif accent == "document":
        draw.rounded_rectangle((300, 118, 344, 169), radius=6, fill=(244, 249, 248, 235), outline=(65, 132, 110, 255), width=3)
        draw.line((309, 133, 335, 133), fill=(87, 145, 126, 255), width=3)
        draw.line((309, 143, 329, 143), fill=(87, 145, 126, 255), width=3)
        draw.line((309, 153, 334, 153), fill=(87, 145, 126, 255), width=3)
    elif accent == "clock":
        draw.ellipse((300, 120, 348, 168), fill=(240, 248, 255, 235), outline=(75, 130, 175, 255), width=3)
        draw.line((324, 145, 324, 130), fill=(75, 130, 175, 255), width=4)
        draw.line((324, 145, 336, 151), fill=(75, 130, 175, 255), width=4)
    elif accent == "sweat":
        draw.ellipse((305, 125, 324, 154), fill=(115, 185, 222, 230))
        draw.polygon([(305, 139), (315, 113), (324, 139)], fill=(115, 185, 222, 230))
    else:
        draw.ellipse((28, 125, 342, 298), fill=(233, 244, 248, 64))


def create_stamp(number: str, text: str, base_name: str, color: tuple[int, int, int, int], accent: str) -> Image.Image:
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    draw_text_centered(draw, text, color)
    draw_accent(draw, accent)

    base_path = POSE_DIR / base_name if base_name.startswith("pose:") else BASE_DIR / base_name
    if base_name.startswith("pose:"):
        base_path = POSE_DIR / base_name.removeprefix("pose:")
        dog_source = Image.open(base_path).convert("RGBA")
    else:
        dog_source = key_green_to_alpha(Image.open(base_path))
    dog = fit(dog_source, 278, 205)
    x = (CANVAS[0] - dog.width) // 2
    y = CANVAS[1] - dog.height - 5
    canvas.alpha_composite(dog, (x, y))
    return canvas


def create_preview(images: list[tuple[str, Image.Image]]) -> None:
    preview = Image.new("RGBA", (CANVAS[0] * 4, CANVAS[1] * 2), (246, 244, 241, 255))
    draw = ImageDraw.Draw(preview)
    font = ImageFont.truetype(str(FONT_PATH), size=22)
    for idx, (number, image) in enumerate(images):
        x = (idx % 4) * CANVAS[0]
        y = (idx // 4) * CANVAS[1]
        preview.alpha_composite(image, (x, y))
        draw.text((x + 9, y + 8), number, font=font, fill=(110, 104, 100, 255))
    preview.convert("RGB").save(OUT_DIR / "preview_keigo_work_trial_8.png", quality=95)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rendered: list[tuple[str, Image.Image]] = []
    for number, text, base_name, color, accent in STAMPS:
        image = create_stamp(number, text, base_name, color, accent)
        image.save(OUT_DIR / f"{number}.png")
        rendered.append((number, image))
    create_preview(rendered)
    print(f"created={len(rendered)}")
    print(OUT_DIR)


if __name__ == "__main__":
    main()
