from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
UNIT = ROOT / "reel_assets" / "pre_exam_series" / "26_pet_period_contact_v1"
SOURCE_DIR = UNIT / "images"
OUT_DIR = UNIT / "telop"
MANIFEST = UNIT / "production_manifest.md"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

SIZE = (1080, 1920)
FONT_SIZE = 54
X_CENTER = SIZE[0] // 2
Y_CENTER = {"top": 310, "center": 960, "bottom": 1510}
MAX_PANEL_WIDTH = 840
PANEL_PADDING_X = 44
PANEL_PADDING_Y = 30
LINE_STEP = 72
NAVY = (16, 36, 55, 255)
BLUE = (0, 104, 150, 255)
PANEL = (255, 255, 255, 179)

FRAMES = [
    ("01_hook_schedule.png", [[("FDG-PET", "blue"), "の日に生理かも"], [("予約先", "blue"), "に相談"]], "top"),
    ("02_consider_booking.png", [["予約変更、迷いますよね"]], "top"),
    ("03_pet_ct_room.png", [[("検査薬", "blue"), "の集まり方を確認"]], "center"),
    ("04_normal_cycle_context.png", [[("周期", "blue"), "で集まり方に変化も"]], "center"),
    ("05_cycle_info_form.png", [[("周期", "blue"), "の情報は画像の参考"]], "center"),
    ("06_facility_contact.png", [["目的や", ("施設", "blue"), "で対応に違いも"]], "center"),
    ("07_prepare_to_call.png", [["検査前にひとこと伝える"]], "top"),
    ("08_phone_phrase.png", [[("生理", "blue"), "が重なりそう"], ["どうすればいいですか？"]], "top"),
    ("09_save_before_contact.png", [["連絡前に", ("保存", "blue"), "して見返す"]], "center"),
]


def text_of(segment: str | tuple[str, str]) -> str:
    return segment[0] if isinstance(segment, tuple) else segment


def line_text(line: list[str | tuple[str, str]]) -> str:
    return "".join(text_of(segment) for segment in line)


def image_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def approved_sources() -> list[Path]:
    pattern = re.compile(r"^\|\s*(\d{2})\s*\|\s*`([^`]+)`\s*\|")
    rows = []
    for line in MANIFEST.read_text(encoding="utf-8-sig").splitlines():
        match = pattern.match(line)
        if match:
            rows.append((int(match.group(1)), Path(match.group(2)).resolve()))
    expected = [(SOURCE_DIR / frame[0]).resolve() for frame in FRAMES]
    if [number for number, _ in rows] != list(range(1, len(FRAMES) + 1)):
        raise RuntimeError("Manifest cut count or sequence does not match the telop plan")
    if [path for _, path in rows] != expected:
        raise RuntimeError("Manifest source paths or order do not match the telop plan")
    actual = {path.resolve() for path in SOURCE_DIR.glob("*.png")}
    if actual != set(expected):
        raise RuntimeError("Input image folder differs from the approved source list")
    if not FONT_PATH.is_file():
        raise FileNotFoundError(FONT_PATH)
    return expected


def cover(path: Path) -> Image.Image:
    with Image.open(path) as source:
        image = source.convert("RGB")
    scale = max(SIZE[0] / image.width, SIZE[1] / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = (resized.width - SIZE[0]) // 2
    top = (resized.height - SIZE[1]) // 2
    return resized.crop((left, top, left + SIZE[0], top + SIZE[1]))


def width(draw: ImageDraw.ImageDraw, value: str, font: ImageFont.FreeTypeFont) -> int:
    bounds = draw.textbbox((0, 0), value, font=font)
    return bounds[2] - bounds[0]


def draw_frame(path: Path, lines: list[list], position: str) -> Image.Image:
    image = cover(path).convert("RGBA")
    layer = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    font = ImageFont.truetype(str(FONT_PATH), FONT_SIZE)
    texts = [line_text(line) for line in lines]
    if not 1 <= len(lines) <= 2:
        raise ValueError(f"Telop must have one or two lines: {path.name}")
    if sum(len(value) for value in texts) > 20:
        raise ValueError(f"Telop exceeds 20 characters: {path.name}: {texts}")
    max_text_width = max(width(draw, value, font) for value in texts)
    panel_width = max(430, max_text_width + PANEL_PADDING_X * 2)
    if panel_width > MAX_PANEL_WIDTH:
        raise ValueError(f"Telop is too wide; shorten the wording: {path.name}")
    panel_height = PANEL_PADDING_Y * 2 + FONT_SIZE + (len(lines) - 1) * LINE_STEP
    x0 = X_CENTER - panel_width // 2
    y0 = Y_CENTER[position] - panel_height // 2
    draw.rounded_rectangle(
        (x0, y0, x0 + panel_width, y0 + panel_height),
        radius=28,
        fill=PANEL,
    )
    for row, line in enumerate(lines):
        full_width = width(draw, texts[row], font)
        x = X_CENTER - full_width // 2
        y = y0 + PANEL_PADDING_Y + row * LINE_STEP - 4
        for segment in line:
            value = text_of(segment)
            color = BLUE if isinstance(segment, tuple) and segment[1] == "blue" else NAVY
            draw.text((x, y), value, font=font, fill=color)
            x += width(draw, value, font)
    image.alpha_composite(layer)
    return image.convert("RGB")


def make_contact_sheet(paths: list[Path]) -> None:
    thumb = (180, 320)
    columns = 3
    rows = math.ceil(len(paths) / columns)
    label_height = 28
    sheet = Image.new("RGB", (columns * thumb[0], rows * (thumb[1] + label_height)), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(str(FONT_PATH), 20)
    for index, path in enumerate(paths):
        with Image.open(path) as image:
            tile = image.resize(thumb, Image.Resampling.LANCZOS)
        x = (index % columns) * thumb[0]
        y = (index // columns) * (thumb[1] + label_height)
        sheet.paste(tile, (x, y))
        draw.text((x + 7, y + thumb[1] + 2), f"{index + 1:02d}", font=font, fill=NAVY)
    sheet.save(OUT_DIR / "contact_sheet_telop.png")


def main() -> None:
    sources = approved_sources()
    before = {source: image_hash(source) for source in sources}
    OUT_DIR.mkdir(exist_ok=True)
    outputs = []
    details = []
    report = ["# テロップ案（承認待ち）", "", "| Cut | 表示文 | 文字数 | 行数 | 位置 | 青強調 |", "| ---: | --- | ---: | ---: | --- | --- |"]
    for index, (source, frame) in enumerate(zip(sources, FRAMES), 1):
        filename, lines, position = frame
        output = OUT_DIR / f"telop_{index:02d}.png"
        draw_frame(source, lines, position).save(output)
        outputs.append(output)
        texts = [line_text(line) for line in lines]
        highlights = [segment[0] for line in lines for segment in line if isinstance(segment, tuple)]
        count = sum(len(value) for value in texts)
        report.append(f"| {index:02d} | {'<br>'.join(texts)} | {count} | {len(lines)} | {position} | {'、'.join(highlights) or 'なし'} |")
        details.append({
            "cut": index,
            "source": str(source),
            "source_sha256": before[source],
            "output": str(output.resolve()),
            "lines": texts,
            "character_count": count,
            "line_count": len(lines),
            "position": position,
            "x_center": X_CENTER,
            "y_center": Y_CENTER[position],
            "highlights": highlights,
        })
    if any(image_hash(source) != digest for source, digest in before.items()):
        raise RuntimeError("An approved input image changed during telop generation")
    make_contact_sheet(outputs)
    report += [
        "",
        "- 全カットのX中心は540px。Y中心は通常960px、顔・髪と重なるCut 01・02・07・08のみ上中央310px。",
        "- フォントはM PLUS Rounded 1c Bold、白い角丸背景は不透明度70%。青強調は単語単位。",
        "- Cut 08は電話で使う言葉の要点だけを表示。音声用の全文は書き起こしていない。",
        "- 承認済み入力画像9枚のハッシュが生成前後で一致。音声・動画は未作成。",
    ]
    (OUT_DIR / "telop_plan.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT_DIR / "telop_manifest.json").write_text(json.dumps(details, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Verified {len(sources)} locked inputs; created {len(outputs)} telop frames")


if __name__ == "__main__":
    main()
