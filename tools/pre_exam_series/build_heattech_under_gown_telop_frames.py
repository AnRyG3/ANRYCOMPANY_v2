from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
INPUT_DIR = ROOT / "reel_assets" / "pre_exam_series" / "21_heattech_under_gown_v1_images"
OUTPUT_DIR = ROOT / "reel_assets" / "pre_exam_series" / "21_heattech_under_gown_v1_telop"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"
CONTACT_SHEET = OUTPUT_DIR / "contact_sheet_telop.jpg"
MANIFEST = OUTPUT_DIR / "telop_manifest.json"
TEXTS = OUTPUT_DIR / "telop_texts.txt"

W, H = 1080, 1920
NAVY = (16, 36, 55, 255)
BLUE = (0, 104, 150, 255)
PANEL = (255, 255, 255, 179)  # 70% opacity
SHADOW = (8, 18, 32, 46)


FRAMES = [
    {
        "src": "frame_01_gown_thermal_inner.png",
        "out": "frame_01_question_telop.png",
        "segments": [[("ヒートテック", "blue")], ["着たままでいい？"]],
        "position": "center",
    },
    {
        "src": "frame_02_before_asking.png",
        "out": "frame_02_cold_day_telop.png",
        "segments": [["寒い日に着た"], [("ヒートテック", "blue")]],
        "position": "center",
    },
    {
        "src": "frame_03_ask_before_changing.png",
        "out": "frame_03_ask_before_changing_telop.png",
        "segments": [["着替える前に"], [("ひと声", "blue"), "で大丈夫"]],
        "position": "center",
    },
    {
        "src": "frame_04_thermal_inner_check.png",
        "out": "frame_04_material_check_telop.png",
        "segments": [["素材によっては"], [("確認", "blue"), "が必要"]],
        "position": "center",
    },
    {
        "src": "frame_05_exam_type_guidance.png",
        "out": "frame_05_exam_type_telop.png",
        "segments": [[("検査", "blue"), "・撮影部位で"], ["対応が変わります"]],
        "position": "center",
    },
    {
        "src": "frame_06_put_thermal_inner_away.png",
        "out": "frame_06_mri_telop.png",
        "segments": [[("MRI", "blue"), "では"], ["脱ぐのが基本"]],
        "position": "center",
    },
    {
        "src": "frame_07_reassured_after_preparation.png",
        "out": "frame_07_reassurance_telop.png",
        "segments": [["着てきても"], [("大丈夫", "blue")]],
        "position": "center",
    },
    {
        "src": "frame_08_show_and_confirm.png",
        "out": "frame_08_show_and_confirm_telop.png",
        "segments": [["見せて"], [("確認", "blue"), "すれば大丈夫"]],
        "position": "center",
    },
    {
        "src": "frame_09_staff_reassurance.png",
        "out": "frame_09_asking_is_welcome_telop.png",
        "segments": [[("確認", "blue"), "は"], ["遠慮しなくて大丈夫"]],
        "position": "center",
    },
    {
        "src": "frame_10_cta_background.png",
        "out": "frame_10_save_cta_telop.png",
        "segments": [["検査前日に"], [("保存", "blue"), "しておいてください"]],
        "position": "center",
    },
]


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size=size)


def cover_resize(image: Image.Image) -> Image.Image:
    image = image.convert("RGB")
    scale = max(W / image.width, H / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = (resized.width - W) // 2
    top = (resized.height - H) // 2
    return resized.crop((left, top, left + W, top + H))


def plain_text(part: str | tuple[str, str]) -> str:
    return part[0] if isinstance(part, tuple) else part


def text_width(draw: ImageDraw.ImageDraw, text: str, current_font: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=current_font)
    return box[2] - box[0]


def line_width(draw: ImageDraw.ImageDraw, line: list[str | tuple[str, str]], current_font: ImageFont.FreeTypeFont) -> int:
    return sum(text_width(draw, plain_text(part), current_font) for part in line)


def fit_font(draw: ImageDraw.ImageDraw, lines: list[list[str | tuple[str, str]]]) -> tuple[ImageFont.FreeTypeFont, int]:
    for size in range(76, 40, -2):
        current_font = font(size)
        line_height = round(size * 1.2)
        if max(line_width(draw, line, current_font) for line in lines) <= 790:
            return current_font, line_height
    return font(40), 48


def add_telop(image: Image.Image, frame: dict) -> Image.Image:
    base = cover_resize(image).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    lines = frame["segments"]
    current_font, line_height = fit_font(draw, lines)
    pad_x, pad_y = 58, 38
    box_width = min(900, max(line_width(draw, line, current_font) for line in lines) + pad_x * 2)
    box_height = line_height * len(lines) + pad_y * 2
    x1 = (W - box_width) // 2

    if frame["position"] == "top":
        y1 = 190
    elif frame["position"] == "bottom":
        y1 = 1260
    else:
        y1 = (H - box_height) // 2
    x2, y2 = x1 + box_width, y1 + box_height

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((x1 + 6, y1 + 8, x2 + 6, y2 + 8), radius=30, fill=SHADOW)
    overlay.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(9)))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle((x1, y1, x2, y2), radius=30, fill=PANEL)

    first_y = y1 + pad_y
    for row, line in enumerate(lines):
        width = line_width(draw, line, current_font)
        x = (W - width) // 2
        y = first_y + row * line_height
        for part in line:
            text = plain_text(part)
            color = BLUE if isinstance(part, tuple) and part[1] == "blue" else NAVY
            draw.text((x, y), text, font=current_font, fill=color)
            x += text_width(draw, text, current_font)

    base.alpha_composite(overlay)
    return base.convert("RGB")


def make_contact_sheet(paths: list[Path]) -> None:
    columns = 5
    thumb_w, thumb_h, label_h = 216, 384, 42
    rows = math.ceil(len(paths) / columns)
    sheet = Image.new("RGB", (columns * thumb_w, rows * (thumb_h + label_h)), (244, 246, 248))
    draw = ImageDraw.Draw(sheet)
    label_font = font(20)
    for index, path in enumerate(paths):
        thumb = Image.open(path).convert("RGB")
        thumb.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (index % columns) * thumb_w
        y = (index // columns) * (thumb_h + label_h)
        sheet.paste(thumb, (x + (thumb_w - thumb.width) // 2, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill=(255, 255, 255))
        draw.text((x + 8, y + thumb_h + 8), f"{index + 1:02d}", font=label_font, fill=NAVY)
    sheet.save(CONTACT_SHEET, quality=94)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_paths: list[Path] = []
    manifest_frames = []
    text_lines = []

    for index, frame in enumerate(FRAMES, start=1):
        source = INPUT_DIR / frame["src"]
        output = OUTPUT_DIR / frame["out"]
        if not source.exists():
            raise FileNotFoundError(source)
        add_telop(Image.open(source), frame).save(output, quality=95)
        output_paths.append(output)
        telop = ["".join(plain_text(part) for part in line) for line in frame["segments"]]
        text_lines.append(f"{index:02d}. {' / '.join(telop)} [{frame['position']}]")
        manifest_frames.append(
            {
                "source": str(source.relative_to(ROOT)),
                "output": str(output.relative_to(ROOT)),
                "telop": telop,
                "position": frame["position"],
                "highlighted_terms": [part[0] for line in frame["segments"] for part in line if isinstance(part, tuple)],
            }
        )

    make_contact_sheet(output_paths)
    TEXTS.write_text("\n".join(text_lines) + "\n", encoding="utf-8-sig")
    MANIFEST.write_text(
        json.dumps(
            {
                "title": "検査着の下にヒートテックは着ていていい？",
                "style": "要点だけ、1画面1メッセージ、X軸中央、全フレーム中央配置、重要語のみ青強調",
                "font": str(FONT_PATH),
                "canvas": {"width": W, "height": H},
                "frames": manifest_frames,
                "contact_sheet": str(CONTACT_SHEET.relative_to(ROOT)),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8-sig",
    )
    print(f"created {len(output_paths)} telop frames")
    print(OUTPUT_DIR)


if __name__ == "__main__":
    main()
