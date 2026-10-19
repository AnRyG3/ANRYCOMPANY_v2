from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
IMAGES = ROOT / "reel_assets" / "pre_exam_series" / "pediatric_hip_shield_v1_images"
OUTPUT = ROOT / "reel_assets" / "pre_exam_series" / "pediatric_hip_shield_v1_telop"
MANIFEST = IMAGES / "production_manifest.md"
FONT = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

WIDTH, HEIGHT = 941, 1672
CENTER_X = WIDTH / 2
CENTERS_Y = {"center": HEIGHT / 2, "top": HEIGHT / 4}
FONT_SIZE = 62
LINE_GAP = 22
PADDING_X = 42
PADDING_Y = 28
NAVY = (13, 34, 61, 255)
BLUE = (9, 92, 178, 255)
PANEL = (255, 255, 255, 179)  # 70% opacity

FRAMES = [
    ("frame_01_hook.png", ("子どもの股関節撮影", "前掛けなし？"), "center", "前掛け"),
    ("frame_02_child_waiting.png", ("前はつけたのに？",), "top", None),
    ("frame_03_statement_background.png", ("前掛け見直しの根拠は", "投稿文のURLへ"), "center", "URL"),
    ("frame_04_equipment.png", ("前掛けの効果は限定的",), "center", "限定的"),
    ("frame_05_shield_storage.png", ("前掛けが画像に", "重なることも"), "center", "重なる"),
    ("frame_06_technologist_preparing.png", ("施設で対応が異なります",), "center", "施設"),
    ("frame_07_technologist_listening.png", ("前掛けを使わない理由を", "教えてください"), "center", "理由"),
    ("frame_08_save_background.png", ("撮影前に見返すなら保存",), "center", "保存"),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_sources() -> list[dict]:
    if not MANIFEST.is_file() or not FONT.is_file():
        raise FileNotFoundError("Production manifest or required font is missing")
    expected = [str(IMAGES / name) for name, _, _, _ in FRAMES]
    listed = re.findall(r"\| \d{2} \| `([A-Za-z]:\\[^`]+\.png)` \|", MANIFEST.read_text(encoding="utf-8"))
    if listed != expected:
        raise RuntimeError("Approved images differ from manifest count, paths, or cut order")
    actual_files = sorted(IMAGES.glob("frame_*.png"))
    if [str(path) for path in actual_files] != expected:
        raise RuntimeError("Production folder images differ from the source lock")
    if len(FRAMES) != 8:
        raise RuntimeError("Unexpected cut count")
    source_info = []
    for name, lines, position, highlight in FRAMES:
        source = IMAGES / name
        if position not in CENTERS_Y or not 1 <= len(lines) <= 2:
            raise ValueError(f"Invalid position or line count: {name}")
        count = sum(len(line) for line in lines)
        if count > 20 or any(not line for line in lines):
            raise ValueError(f"Telop text too long or empty: {name}: {count}")
        if highlight is not None and sum(line.count(highlight) for line in lines) != 1:
            raise ValueError(f"Highlight must occur once as a complete word: {name}")
        with Image.open(source) as image:
            if image.size != (WIDTH, HEIGHT):
                raise ValueError(f"Approved image dimensions changed: {name}")
        source_info.append({"path": source, "hash": sha256(source)})
    return source_info


def draw_line(draw: ImageDraw.ImageDraw, line: str, keyword: str | None, x: float, y: float, font: ImageFont.FreeTypeFont) -> None:
    if keyword is None or keyword not in line:
        draw.text((x, y), line, font=font, fill=NAVY)
        return
    prefix, suffix = line.split(keyword, 1)
    draw.text((x, y), prefix, font=font, fill=NAVY)
    highlight_x = x + draw.textlength(prefix, font=font)
    draw.text((highlight_x, y), keyword, font=font, fill=BLUE)
    draw.text((highlight_x + draw.textlength(keyword, font=font), y), suffix, font=font, fill=NAVY)


def render(name: str, lines: tuple[str, ...], position: str, keyword: str | None, font: ImageFont.FreeTypeFont) -> dict:
    source = IMAGES / name
    with Image.open(source) as image:
        canvas = image.convert("RGBA")
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    widths = [draw.textlength(line, font=font) for line in lines]
    boxes = [draw.textbbox((0, 0), line, font=font) for line in lines]
    heights = [box[3] - box[1] for box in boxes]
    text_height = sum(heights) + LINE_GAP * (len(lines) - 1)
    panel_width = max(widths) + 2 * PADDING_X
    panel_height = text_height + 2 * PADDING_Y
    if panel_width > WIDTH - 140:
        raise ValueError(f"Text exceeds centered safe width at fixed font size: {name}")
    center_y = CENTERS_Y[position]
    panel_box = (
        round(CENTER_X - panel_width / 2),
        round(center_y - panel_height / 2),
        round(CENTER_X + panel_width / 2),
        round(center_y + panel_height / 2),
    )
    draw.rounded_rectangle(panel_box, radius=30, fill=PANEL)
    line_y = center_y - text_height / 2
    for line, width, bbox, height in zip(lines, widths, boxes, heights):
        x = CENTER_X - width / 2 - bbox[0]
        y = line_y - bbox[1]
        draw_line(draw, line, keyword, x, y, font)
        line_y += height + LINE_GAP
    result = Image.alpha_composite(canvas, overlay).convert("RGB")
    destination = OUTPUT / f"telop_{name}"
    result.save(destination, format="PNG")
    return {
        "cut": name[6:8],
        "source": str(source),
        "output": str(destination),
        "text": "\n".join(lines),
        "characters": sum(len(line) for line in lines),
        "lines": len(lines),
        "position": position,
        "center_x": CENTER_X,
        "center_y": center_y,
        "panel_box": panel_box,
        "font_size": FONT_SIZE,
        "highlight": keyword,
        "text_widths": [round(width, 1) for width in widths],
    }


def main() -> None:
    sources = verify_sources()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype(str(FONT), FONT_SIZE)
    qa = [render(name, lines, position, keyword, font) for name, lines, position, keyword in FRAMES]
    for source in sources:
        if sha256(source["path"]) != source["hash"]:
            raise RuntimeError(f"Approved image changed during text insertion: {source['path']}")
    (OUTPUT / "telop_qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(qa, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
