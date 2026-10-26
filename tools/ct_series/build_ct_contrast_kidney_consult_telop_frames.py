from __future__ import annotations

import json
import math
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
UNIT = ROOT / "reel_assets" / "ct_series" / "ct_contrast_kidney_consult_v1_images"
MANIFEST = UNIT / "production_manifest.md"
OUT = UNIT / "telop_frames"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

SIZE = (1080, 1920)
FONT_SIZE = 52
NAVY = (16, 36, 55, 255)
BLUE = (0, 104, 150, 255)
PANEL = (255, 255, 255, 179)
X_CENTER = SIZE[0] // 2
Y_CENTERS = {"top": 380, "center": SIZE[1] // 2, "bottom": 1540}

# Text is intentionally shorter than the narration. The blue word is one word only.
FRAMES = [
    ("01_consultation.png", "造影CTなら腎臓のことも医師へ", "腎臓"),
    ("02_thoughtful_patient.png", "造影剤、使える？", "造影剤"),
    ("03_history_discussion.png", "腎臓について言われたことを伝えて", "腎臓"),
    ("04_blood_result_review.png", "採血結果で腎機能を確認", "採血結果"),
    ("05_facility_explanation.png", "結果の扱いは施設で異なります", "施設"),
    ("06_result_handover.png", "採血結果があれば医師へ", "採血結果"),
    ("07_doctor_judgment.png", "造影剤の使用は医師が判断", "医師"),
    ("08_patient_speaks.png", "数値が分からなくても伝えて", "伝えて"),
    ("09_consult_without_result.png", "結果がなくても医師に相談", "医師"),
    ("10_example_question.png", "腎臓のことで\n確認することはありますか？", "確認"),
    ("11_save_before_consult.png", "診察前に見返せるよう保存", "保存"),
]


def locked_sources() -> list[Path]:
    if not MANIFEST.is_file():
        raise FileNotFoundError(MANIFEST)
    section = MANIFEST.read_text(encoding="utf-8-sig").split("## Approved Images", 1)[1]
    section = section.split("## Character Clothing Lock", 1)[0]
    entries = re.findall(r"^\|\s*(\d{2})\s*\|\s*`([^`]+)`\s*\|", section, re.M)
    if len(entries) != len(FRAMES):
        raise ValueError(f"Manifest has {len(entries)} images; expected {len(FRAMES)}")
    if [cut for cut, _ in entries] != [f"{i:02d}" for i in range(1, 12)]:
        raise ValueError("Manifest cut order differs from 01-11")
    sources = [Path(path) for _, path in entries]
    if any(not path.is_file() for path in sources):
        raise FileNotFoundError("A manifest input image is missing")
    if [path.name for path in sources] != [name for name, _, _ in FRAMES]:
        raise ValueError("Manifest source order or filename differs from telop plan")
    actual = sorted(UNIT.glob("[0-9][0-9]_*.png"))
    if {path.resolve() for path in actual} != {path.resolve() for path in sources}:
        raise ValueError("Approved image count or paths differ from manifest")
    return sources


def cover(source: Image.Image) -> Image.Image:
    source = source.convert("RGB")
    w, h = SIZE
    scale = max(w / source.width, h / source.height)
    scaled = source.resize(
        (round(source.width * scale), round(source.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = (scaled.width - w) // 2
    top = (scaled.height - h) // 2
    return scaled.crop((left, top, left + w, top + h)).convert("RGBA")


def draw_telop(
    source: Path, message: str, blue_word: str, position: str, font: ImageFont.FreeTypeFont
) -> Image.Image:
    base = cover(Image.open(source))
    overlay = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    lines = message.split("\n")
    text_width = max(draw.textlength(line, font=font) for line in lines)
    if text_width > 850:
        raise ValueError(f"Telop too wide at fixed font size: {message}")
    panel_w = round(text_width + 110)
    line_height = 64
    panel_h = 78 + line_height * len(lines)
    x0 = (SIZE[0] - panel_w) // 2
    y_center = Y_CENTERS[position]
    y0 = y_center - panel_h // 2
    draw.rounded_rectangle((x0, y0, x0 + panel_w, y0 + panel_h), radius=28, fill=PANEL)

    text_block_h = line_height * len(lines)
    first_baseline_y = y_center - text_block_h / 2
    for line_index, line in enumerate(lines):
        x = (SIZE[0] - draw.textlength(line, font=font)) / 2
        bbox = draw.textbbox((0, 0), line, font=font)
        y = first_baseline_y + line_index * line_height + (line_height - (bbox[3] - bbox[1])) / 2 - bbox[1]
        if blue_word in line:
            prefix, suffix = line.split(blue_word, 1)
            segments = ((prefix, NAVY), (blue_word, BLUE), (suffix, NAVY))
        else:
            segments = ((line, NAVY),)
        for part, color in segments:
            draw.text((x, y), part, font=font, fill=color)
            x += draw.textlength(part, font=font)
    base.alpha_composite(overlay)
    return base.convert("RGB")


def contact_sheet(paths: list[Path], font: ImageFont.FreeTypeFont) -> Path:
    tile_w, tile_h, label_h, columns = 270, 480, 38, 3
    rows = math.ceil(len(paths) / columns)
    sheet = Image.new("RGB", (tile_w * columns, (tile_h + label_h) * rows), (247, 249, 250))
    draw = ImageDraw.Draw(sheet)
    small_font = ImageFont.truetype(str(FONT_PATH), 22)
    for i, path in enumerate(paths):
        x = (i % columns) * tile_w
        y = (i // columns) * (tile_h + label_h)
        tile = Image.open(path).resize((tile_w, tile_h), Image.Resampling.LANCZOS)
        sheet.paste(tile, (x, y))
        draw.text((x + 10, y + tile_h + 4), f"CUT {i + 1:02d}", font=small_font, fill=NAVY)
    output = OUT / "contact_sheet.png"
    sheet.save(output)
    return output


def main() -> None:
    sources = locked_sources()
    if not FONT_PATH.is_file():
        raise FileNotFoundError(FONT_PATH)
    font = ImageFont.truetype(str(FONT_PATH), FONT_SIZE)
    OUT.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    records = []
    for index, (source, (_, message, blue_word)) in enumerate(zip(sources, FRAMES, strict=True), start=1):
        characters = len(message.replace("\n", ""))
        lines = message.split("\n")
        if not (1 <= characters <= 20 and 1 <= len(lines) <= 2):
            raise ValueError(f"Cut {index:02d} has {characters} characters and {len(lines)} lines")
        if message.count(blue_word) != 1:
            raise ValueError(f"Cut {index:02d} blue word is ambiguous")
        position = "top" if index == 10 else "center"
        output = OUT / f"telop_{index:02d}.png"
        draw_telop(source, message, blue_word, position, font).save(output)
        outputs.append(output)
        records.append({
            "cut": f"{index:02d}",
            "source": str(source),
            "output": str(output),
            "telop": message,
            "characters": characters,
            "lines": len(lines),
            "blue_word": blue_word,
            "position": position,
            "x_center": X_CENTER,
            "y_center": Y_CENTERS[position],
            "font": str(FONT_PATH),
            "font_size": FONT_SIZE,
            "panel_opacity": "70%",
        })
    (OUT / "telop_manifest.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8-sig"
    )
    contact_sheet(outputs, font)
    print(f"Created {len(outputs)} telop frames in {OUT}")


if __name__ == "__main__":
    main()
