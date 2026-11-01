"""Render approved, text-only-overlaid frames after manifest source-lock check."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
UNIT = ROOT / "reel_assets" / "xray_front_side_remake_20261111"
MANIFEST = UNIT / "production_manifest.md"
OUT = UNIT / "telop_frames_v2"
FONT = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"
SIZE = (1080, 1920)
FONT_SIZE = 64
BOX_CENTER_Y = 960
NAVY = (16, 36, 55, 255)
BLUE = (0, 104, 150, 255)
WHITE_70 = (255, 255, 255, 179)
SHADOW = (0, 0, 0, 45)

EXPECTED = [
    "sample_01_turning.png",
    "image_02_empathy.png",
    "image_03_room.png",
    "sample_04_side_position_v2.png",
    "image_05_purpose_v2.png",
    "image_06_turning.png",
    "image_07_side_summary.png",
    "image_08_question.png",
    "image_10_follow_background.png",
]

# One message per frame. Empty highlight means navy only. Every card is centered.
TELOPS = [
    {"lines": ["前回は正面だけ", "今日は横向きも"], "highlight": "横向き"},
    {"lines": ["前と違うと気になります"], "highlight": ""},
    {"lines": ["1方向では見えにくいことも"], "highlight": "1方向"},
    {"lines": ["横向きで撮ることも"], "highlight": "横向き"},
    {"lines": ["向き・枚数は", "部位や目的で変わる"], "highlight": "向き・枚数"},
    {"lines": ["姿勢を変えることも"], "highlight": "姿勢"},
    {"lines": ["別の向きからも確認"], "highlight": "別の向き"},
    {"lines": ["前回と向きが違うのは", "なぜですか？"], "highlight": "向き"},
    {"lines": ["フォローをお願いします"], "highlight": "フォロー"},
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def locked_sources() -> list[Path]:
    lines = MANIFEST.read_text(encoding="utf-8").splitlines()
    found = []
    for line in lines:
        match = re.match(r"^\|\s*(\d{2})\s*\|\s*`([^`]+)`\s*\|", line)
        if match:
            found.append((int(match.group(1)), Path(match.group(2))))
    expected = [(i, UNIT / name) for i, name in enumerate(EXPECTED, 1)]
    if found != expected:
        raise RuntimeError(f"Manifest source lock mismatch: {found!r}")
    if len({str(path).lower() for _, path in found}) != len(EXPECTED):
        raise RuntimeError("Manifest has duplicate source paths")
    for _, path in found:
        if not path.is_file():
            raise FileNotFoundError(path)
    return [path for _, path in found]


def cover(image: Image.Image) -> Image.Image:
    image = image.convert("RGB")
    scale = max(SIZE[0] / image.width, SIZE[1] / image.height)
    w, h = round(image.width * scale), round(image.height * scale)
    image = image.resize((w, h), Image.Resampling.LANCZOS)
    x, y = (w - SIZE[0]) // 2, (h - SIZE[1]) // 2
    return image.crop((x, y, x + SIZE[0], y + SIZE[1])).convert("RGBA")


def width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def render(source: Path, telop: dict, target: Path, font: ImageFont.FreeTypeFont) -> dict:
    lines = telop["lines"]
    if not 1 <= len(lines) <= 2:
        raise ValueError("Each frame needs one or two lines")
    message = "".join(lines)
    if len(message) > 20:
        raise ValueError(f"Over 20 characters: {message}")
    if telop["highlight"] and telop["highlight"] not in message:
        raise ValueError(f"Missing highlighted word: {message}")

    with Image.open(source) as raw:
        original_size = raw.size
        base = cover(raw)
    layer = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    max_text_width = max(width(draw, line, font) for line in lines)
    if max_text_width > 820:
        raise ValueError(f"64px text too wide ({max_text_width}px): {message}")
    line_height = 82
    box_w = max_text_width + 96
    box_h = len(lines) * line_height + 38
    left = (SIZE[0] - box_w) // 2
    top = BOX_CENTER_Y - box_h // 2
    right, bottom = left + box_w, top + box_h

    shade = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    ImageDraw.Draw(shade).rounded_rectangle(
        (left + 4, top + 7, right + 4, bottom + 7), radius=24, fill=SHADOW
    )
    layer.alpha_composite(shade.filter(ImageFilter.GaussianBlur(8)))
    draw.rounded_rectangle((left, top, right, bottom), radius=24, fill=WHITE_70)

    for i, line in enumerate(lines):
        line_w = width(draw, line, font)
        x = (SIZE[0] - line_w) // 2
        y = top + 19 + i * line_height
        highlight = telop["highlight"]
        parts = line.partition(highlight) if highlight and highlight in line else (line, "", "")
        for part, color in zip(parts, (NAVY, BLUE, NAVY)):
            if not part:
                continue
            # Subtle text shadow plus a high-contrast 70% white backing.
            draw.text((x + 1, y + 2), part, font=font, fill=(0, 0, 0, 42))
            draw.text((x, y), part, font=font, fill=color)
            x += width(draw, part, font)

    base.alpha_composite(layer)
    target.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(target, "PNG")
    return {
        "source": str(source),
        "source_size": original_size,
        "source_sha256": sha256(source),
        "output": str(target),
        "output_size": SIZE,
        "text": message,
        "characters": len(message),
        "lines": len(lines),
        "position": "center",
        "center_x": SIZE[0] // 2,
        "center_y": BOX_CENTER_Y,
        "font_px": FONT_SIZE,
        "max_line_width_px": max_text_width,
    }


def contact_sheet(paths: list[Path]) -> None:
    thumb_w, thumb_h = 270, 480
    sheet = Image.new("RGB", (thumb_w * 5, thumb_h * 2), "white")
    for i, path in enumerate(paths):
        with Image.open(path) as image:
            thumb = image.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        sheet.paste(thumb, ((i % 5) * thumb_w, (i // 5) * thumb_h))
    sheet.save(OUT / "contact_sheet.png")


def main() -> None:
    sources = locked_sources()
    if len(TELOPS) != len(sources):
        raise RuntimeError("Telop count does not match manifest")
    font = ImageFont.truetype(str(FONT), FONT_SIZE)
    before = [sha256(path) for path in sources]
    records = []
    outputs = []
    for i, (source, telop) in enumerate(zip(sources, TELOPS), 1):
        target = OUT / f"telop_{i:02d}.png"
        records.append(render(source, telop, target, font))
        outputs.append(target)
    if before != [sha256(path) for path in sources]:
        raise RuntimeError("An approved source image changed during rendering")
    contact_sheet(outputs)
    (OUT / "qa_report.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    rows = [
        "# テロップ案（確認用）",
        "",
        "次回予告を除いた承認済み画像9枚に対応。全カット1080×1920、M PLUS Rounded 1c Bold 64px、X=540・Y=960固定。白70%の角丸背景、濃紺文字、重要語のみ青。",
        "",
        "| カット | 表示文 | 文字数 | 行数 | 位置 |",
        "|---|---|---:|---:|---|",
    ]
    for i, (telop, record) in enumerate(zip(TELOPS, records), 1):
        rows.append(
            f"| {i:02d} | {'<br>'.join(telop['lines'])} | {record['characters']} | {record['lines']} | 中央 |"
        )
    rows += [
        "",
        "原画像は変更していません。次回予告の画像と台本行は不使用。文字入れ済み画像は確認用で、音声・動画は未制作です。",
    ]
    (UNIT / "telop_plan.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    for record in records:
        print(
            f"{Path(record['output']).name}: {record['characters']} chars, "
            f"{record['lines']} line(s), {record['max_line_width_px']}px"
        )


if __name__ == "__main__":
    main()
