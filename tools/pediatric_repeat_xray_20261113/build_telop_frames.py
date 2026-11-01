"""Render text frames from the approved, manifest-locked images only."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
UNIT = ROOT / "reel_assets" / "pediatric_repeat_xray_20261113"
MANIFEST = UNIT / "production_manifest.md"
OUT = UNIT / "telop_frames"
FONT = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"
SIZE = (1080, 1920)
FONT_SIZE = 64
X_CENTER = 540
Y_CENTER = 960
Y_LOWER = 1400
NAVY = (16, 36, 55, 255)
BLUE = (0, 104, 150, 255)
WHITE_70 = (255, 255, 255, 179)

EXPECTED = [
    "sample_01_consultation_hook_shoes.png",
    "cut_02_parent_concern.png",
    "cut_03_doctor_explains.png",
    "cut_04_prior_image_purpose.png",
    "cut_05_medical_necessity.png",
    "cut_06_tell_previous_xray.png",
    "cut_07_xray_preparation_v2.png",
    "cut_08_share_concern.png",
    "cut_09_question_example.png",
    "cut_10_save_for_visit.png",
]

# Each row is one message. Two lines appear only where needed for meaning.
# The centered box would cover the child's face in every approved source image.
TELOPS = [
    {"lines": ["またレントゲン？", "理由は医師に聞けます"], "highlight": "医師", "position": "lower"},
    {"lines": ["また撮ると聞くと心配"], "highlight": "心配", "position": "lower"},
    {"lines": ["診断／経過を見る"], "highlight": "経過", "position": "lower"},
    {"lines": ["撮る目的が違うことも"], "highlight": "目的", "position": "lower"},
    {"lines": ["必要性は医師が判断"], "highlight": "医師", "position": "lower"},
    {"lines": ["前に撮ったことを伝える"], "highlight": "前", "position": "lower"},
    {"lines": ["体格に合わせて調整"], "highlight": "体格", "position": "lower"},
    {"lines": ["心配なら目的を聞けます"], "highlight": "目的", "position": "lower"},
    {"lines": ["前にも撮りましたが", "今回は何のためですか？"], "highlight": "今回", "position": "lower"},
    {"lines": ["診察前に見返せるよう保存"], "highlight": "保存", "position": "lower"},
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def locked_sources() -> list[Path]:
    found = []
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\|\s*(\d{2})\s*\|\s*`([^`]+)`\s*\|", line)
        if match:
            found.append((int(match.group(1)), Path(match.group(2))))
    expected = [(i, UNIT / name) for i, name in enumerate(EXPECTED, 1)]
    if found != expected:
        raise RuntimeError(f"Manifest source lock mismatch: {found!r}")
    if len({str(path).lower() for _, path in found}) != len(expected):
        raise RuntimeError("Duplicate source path")
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


def text_width(draw: ImageDraw.ImageDraw, value: str, font: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), value, font=font)
    return box[2] - box[0]


def render(source: Path, telop: dict, target: Path, font: ImageFont.FreeTypeFont) -> dict:
    lines = telop["lines"]
    message = "".join(lines)
    if not 1 <= len(lines) <= 2 or len(message) > 20:
        raise ValueError(f"Line or character limit exceeded: {message}")
    highlight = telop["highlight"]
    if highlight and (message.count(highlight) != 1 or len(highlight) > 5):
        raise ValueError(f"Highlight is not a single short term: {highlight}")
    if telop["position"] != "lower":
        raise ValueError("Position must use the shared lower center for these images")

    with Image.open(source) as raw:
        original_size = raw.size
        base = cover(raw)
    layer = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    line_widths = [text_width(draw, line, font) for line in lines]
    max_width = max(line_widths)
    if max_width > 830:
        raise ValueError(f"64px text exceeds width: {message}: {max_width}px")
    box_w = max_width + 96
    box_h = len(lines) * 82 + 38
    left = X_CENTER - box_w // 2
    top = Y_LOWER - box_h // 2
    right, bottom = left + box_w, top + box_h
    if left < 70 or right > 1010 or bottom > 1600:
        raise ValueError(f"Outside telop safe area: {message}")

    shadow = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        (left + 4, top + 7, right + 4, bottom + 7), radius=24, fill=(0, 0, 0, 45)
    )
    layer.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(8)))
    draw.rounded_rectangle((left, top, right, bottom), radius=24, fill=WHITE_70)

    for i, line in enumerate(lines):
        x = X_CENTER - line_widths[i] // 2
        y = top + 19 + i * 82
        before, found, after = line.partition(highlight) if highlight in line else (line, "", "")
        for part, color in ((before, NAVY), (found, BLUE), (after, NAVY)):
            if not part:
                continue
            draw.text((x + 1, y + 2), part, font=font, fill=(0, 0, 0, 42))
            draw.text((x, y), part, font=font, fill=color)
            x += text_width(draw, part, font)

    base.alpha_composite(layer)
    target.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(target, "PNG")
    return {
        "source": str(source),
        "source_sha256": sha256(source),
        "source_size": original_size,
        "output": str(target),
        "output_size": SIZE,
        "text": message,
        "characters": len(message),
        "lines": len(lines),
        "position": "lower_center",
        "center_x": X_CENTER,
        "center_y": Y_LOWER,
        "font_px": FONT_SIZE,
        "max_line_width_px": max_width,
        "box": [left, top, right, bottom],
    }


def main() -> None:
    sources = locked_sources()
    if len(sources) != len(TELOPS):
        raise RuntimeError("Telop count does not match source count")
    font = ImageFont.truetype(str(FONT), FONT_SIZE)
    before = [sha256(path) for path in sources]
    records = []
    thumbs = []
    for i, (source, telop) in enumerate(zip(sources, TELOPS), 1):
        target = OUT / f"telop_{i:02d}.png"
        records.append(render(source, telop, target, font))
        with Image.open(target) as image:
            thumbs.append(image.resize((270, 480), Image.Resampling.LANCZOS))
    if before != [sha256(path) for path in sources]:
        raise RuntimeError("Approved source image changed during rendering")
    sheet = Image.new("RGB", (270 * 5, 480 * 2), "white")
    for i, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((i % 5) * 270, (i // 5) * 480))
    sheet.save(OUT / "contact_sheet.png")
    (OUT / "qa_report.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    rows = [
        "# テロップ案（確認用）",
        "",
        "全10カット。原画像は変更せず、文字入り画像だけ1080×1920に拡大。M PLUS Rounded 1c Bold 64pxを全カットに使用。X=540固定。中央Y=960では子どもの頭・顔に重なるため、全カットで共通の下中央Y=1400を使用。白70%の角丸背景、濃紺文字、重要語のみ青。",
        "",
        "| カット | 表示文 | 文字数 | 行数 | 位置 | 青強調 |",
        "|---|---|---:|---:|---|---|",
    ]
    for i, (telop, record) in enumerate(zip(TELOPS, records), 1):
        rows.append(
            f"| {i:02d} | {'<br>'.join(telop['lines'])} | {record['characters']} | {record['lines']} | 下中央 | {telop['highlight']} |"
        )
    rows += [
        "",
        "09は医師に撮影の目的を尋ねる自然な言い方に修正。前回撮影と今回の目的の両方を20文字で残す。",
        "",
        "画像全体の承認後のテロップ確認段階。音声・動画は未制作。",
    ]
    (UNIT / "telop_plan.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    for i, record in enumerate(records, 1):
        print(f"{i:02d}: {record['characters']} chars, {record['lines']} lines, "
              f"X={record['center_x']} Y={record['center_y']} size={record['font_px']}px "
              f"width={record['max_line_width_px']}px")


if __name__ == "__main__":
    main()
