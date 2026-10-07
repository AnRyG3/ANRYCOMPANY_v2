from __future__ import annotations

import json
import math
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
UNIT = ROOT / "reel_assets" / "pre_exam_series" / "22_barium_morning_smoking_v1"
INPUT_DIR = UNIT / "images"
OUTPUT_DIR = UNIT / "telop"
PRODUCTION_MANIFEST = UNIT / "production_manifest.md"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (12, 34, 64, 255)
BLUE = (0, 112, 185, 255)
PANEL = (255, 255, 255, 179)  # 70% opacity
PANEL_EDGE = (255, 255, 255, 220)
SHADOW = (8, 18, 32, 58)
BOXES = {
    "top": (82, 252, 998, 488),
    "center": (82, 842, 998, 1078),
    "bottom": (82, 1248, 998, 1484),
}

FRAMES = [
    ("01_hook_smoking_morning_v2.png", "telop_01_hook_smoking_morning.png", [["いつもの癖で"], [("タバコ", "blue"), "吸っちゃった…"]], "center"),
    ("02_check_instruction.png", "telop_02_check_instruction.png", [["まずは"], [("案内書", "blue"), "を確認"]], "center"),
    ("03_facility_guidance.png", "telop_03_facility_guidance.png", [["制限は"], [("施設ごと", "blue"), "に違います"]], "center"),
    ("04_record_intake.png", "telop_04_record_intake.png", [[("内容", "blue"), "・", ("時刻", "blue"), "・", ("量", "blue"), "を"], ["伝えてください"]], "center"),
    ("05_facility_judgment.png", "telop_05_facility_judgment.png", [["受けられるかは"], [("施設", "blue"), "が判断します"]], "center"),
    ("06_medicine_check.png", "telop_06_medicine_check.png", [[("薬", "blue"), "は"], [("自己判断", "blue"), "でやめない"]], "bottom"),
    ("07_call_before_departure.png", "telop_07_call_before_departure.png", [["検査前に分かれば"], [("予約先", "blue"), "へ連絡"]], "center"),
    ("08_tell_as_is.png", "telop_08_tell_as_is.png", [["そのまま"], [("伝えて", "blue"), "ください"]], "center"),
    ("09_follow_guidance.png", "telop_09_follow_guidance.png", [["一人で決めず"], [("施設", "blue"), "の案内に任せる"]], "center"),
    ("10_save_night_before.png", "telop_10_save_night_before.png", [["検査前日の夜に"], [("保存", "blue"), "して見返す"]], "center"),
    ("11_four_item_cta.png", "telop_11_four_item_cta.png", [["確認する", ("4つ", "blue")], ["食事・水分・喫煙・薬"]], "center"),
]


def get_font(size: int) -> ImageFont.FreeTypeFont:
    if not FONT_PATH.exists():
        raise FileNotFoundError(f"Required telop font not found: {FONT_PATH}")
    return ImageFont.truetype(str(FONT_PATH), size=size)


def cover_resize(image: Image.Image) -> Image.Image:
    image = image.convert("RGB")
    scale = max(W / image.width, H / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    left, top = (resized.width - W) // 2, (resized.height - H) // 2
    return resized.crop((left, top, left + W, top + H))


def text_of(segment: str | tuple[str, str]) -> str:
    return segment[0] if isinstance(segment, tuple) else segment


def width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def height(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=font)
    return box[3] - box[1]


def line_width(draw: ImageDraw.ImageDraw, line: list, font: ImageFont.FreeTypeFont) -> int:
    return sum(width(draw, text_of(segment), font) for segment in line)


def line_height(draw: ImageDraw.ImageDraw, line: list, font: ImageFont.FreeTypeFont) -> int:
    return max(height(draw, text_of(segment), font) for segment in line)


def fit_font(draw: ImageDraw.ImageDraw, lines: list[list], max_w: int, max_h: int) -> tuple[ImageFont.FreeTypeFont, int]:
    for size in range(74, 41, -2):
        font = get_font(size)
        spacing = max(12, round(size * 0.22))
        total_h = sum(line_height(draw, line, font) for line in lines) + spacing * (len(lines) - 1)
        if max(line_width(draw, line, font) for line in lines) <= max_w and total_h <= max_h:
            return font, spacing
    return get_font(42), 10


def draw_panel(image: Image.Image, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((x0 + 8, y0 + 10, x1 + 8, y1 + 10), radius=34, fill=SHADOW)
    image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(12)))
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rounded_rectangle(box, radius=34, fill=PANEL)
    draw.rounded_rectangle((x0 + 7, y0 + 7, x1 - 7, y1 - 7), radius=28, outline=PANEL_EDGE, width=4)


def draw_telop(image: Image.Image, lines: list[list], position: str) -> None:
    x0, y0, x1, y1 = BOXES[position]
    draw_panel(image, (x0, y0, x1, y1))
    draw = ImageDraw.Draw(image, "RGBA")
    font, spacing = fit_font(draw, lines, (x1 - x0) - 84, (y1 - y0) - 64)
    heights = [line_height(draw, line, font) for line in lines]
    y = y0 + ((y1 - y0) - sum(heights) - spacing * (len(lines) - 1)) // 2 - 4
    for line, line_h in zip(lines, heights):
        x = x0 + ((x1 - x0) - line_width(draw, line, font)) // 2
        for segment in line:
            text, color = segment if isinstance(segment, tuple) else (segment, NAVY)
            draw.text((x, y), text, font=font, fill=BLUE if color == "blue" else NAVY)
            x += width(draw, text, font)
        y += line_h + spacing


def assert_source_lock() -> None:
    if not PRODUCTION_MANIFEST.exists():
        raise FileNotFoundError(PRODUCTION_MANIFEST)
    manifest_paths = [
        path
        for path in re.findall(r"`([A-Za-z]:\\[^`]+\.png)`", PRODUCTION_MANIFEST.read_text(encoding="utf-8"))
        if "\\images\\" in path
    ]
    expected = [str(INPUT_DIR / frame[0]) for frame in FRAMES]
    if manifest_paths != expected:
        raise RuntimeError("Production manifest image paths do not match the telop cut order.")
    if not all(Path(path).exists() for path in expected):
        raise RuntimeError("An approved input image listed in the production manifest is missing.")


def make_contact_sheet(paths: list[Path]) -> Path:
    cols, thumb_w, thumb_h, label_h = 3, 270, 480, 42
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (244, 246, 248))
    draw, label_font = ImageDraw.Draw(sheet), get_font(20)
    for index, path in enumerate(paths):
        thumb = Image.open(path).convert("RGB")
        thumb.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x, y = (index % cols) * thumb_w, (index // cols) * (thumb_h + label_h)
        sheet.paste(thumb, (x + (thumb_w - thumb.width) // 2, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill=(255, 255, 255))
        draw.text((x + 8, y + thumb_h + 8), f"{index + 1:02d} {path.stem[:20]}", font=label_font, fill=NAVY)
    output = OUTPUT_DIR / "_qa_contact_sheet_telop.png"
    sheet.save(output, quality=94)
    return output


def main() -> None:
    assert_source_lock()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs, records = [], []
    for source_name, output_name, lines, position in FRAMES:
        source, output = INPUT_DIR / source_name, OUTPUT_DIR / output_name
        image = cover_resize(Image.open(source)).convert("RGBA")
        draw_telop(image, lines, position)
        image.convert("RGB").save(output, quality=95)
        outputs.append(output)
        records.append({
            "source": str(source),
            "output": str(output),
            "telop": ["".join(text_of(segment) for segment in line) for line in lines],
            "position": position,
            "box": BOXES[position],
        })
    contact_sheet = make_contact_sheet(outputs)
    (OUTPUT_DIR / "telop_manifest.json").write_text(
        json.dumps({"font": str(FONT_PATH), "panel_opacity": "70%", "frames": records, "contact_sheet": str(contact_sheet)}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8-sig",
    )
    print(f"created {len(outputs)} telop frames")
    print(contact_sheet)


if __name__ == "__main__":
    main()
