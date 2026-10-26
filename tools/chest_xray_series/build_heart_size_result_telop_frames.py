"""Render approved short telops onto copies of the locked source frames."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
UNIT = ROOT / "reel_assets" / "chest_xray_series" / "heart_size_result_consult_20261026"
MANIFEST = UNIT / "production_manifest.md"
PROPOSAL = UNIT / "telop_proposal.md"
OUT = UNIT / "telop_frames"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

SIZE = (941, 1672)
FONT_SIZE = 60
PANEL_PAD_X = 20
PANEL_PAD_Y = 18
LINE_DISTANCE = 72
WRAPS = {
    1: ("心臓が大きい？", "気になりますよね"),
    2: ("その一言では", "理由は分からない"),
    6: ("写真だけで状態は", "決められない"),
    10: ("「心臓が大きい」の", "意味と次は？"),
}
Y_POSITIONS = {"中央": 836, "上中央": 350, "下中央": 1322}
NAVY = (16, 46, 74, 255)
BLUE = (34, 105, 175, 255)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_sources() -> dict[int, Path]:
    entries = re.findall(r"^\|\s*(\d{2})\s*\|\s*`([^`]+)`\s*\|", MANIFEST.read_text(encoding="utf-8"), re.M)
    assert len(entries) == 11, f"Expected 11 manifest images, got {len(entries)}"
    result = {int(number): Path(name) for number, name in entries}
    assert sorted(result) == list(range(1, 12))
    assert len(set(result.values())) == 11
    for path in result.values():
        assert path.is_file(), path
        assert path.parent.resolve() == UNIT.resolve(), path
    return result


def read_telops() -> dict[int, dict]:
    pattern = r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|$"
    rows = re.findall(pattern, PROPOSAL.read_text(encoding="utf-8"), re.M)
    result = {}
    for number, text, count, lines, position, accent in rows:
        cut = int(number)
        assert cut not in result
        assert len(text) == int(count) <= 15, (cut, text, count)
        assert int(lines) in (1, 2) and "\n" not in text
        assert position in Y_POSITIONS
        assert text.count(accent) == 1, (cut, text, accent)
        display_lines = WRAPS.get(cut, (text,))
        assert "".join(display_lines) == text, (cut, text, display_lines)
        assert len(display_lines) == int(lines), (cut, lines, display_lines)
        result[cut] = {"text": text, "display_lines": display_lines, "position": position, "accent": accent}
    assert sorted(result) == list(range(1, 12)), sorted(result)
    assert all(row["position"] == "中央" for cut, row in result.items() if cut not in (5, 10))
    assert result[5]["position"] == "下中央"
    assert result[10]["position"] == "上中央"
    return result


def render(source: Path, row: dict, font: ImageFont.FreeTypeFont) -> tuple[Image.Image, dict]:
    with Image.open(source) as source_image:
        assert source_image.size == SIZE, (source, source_image.size)
        image = source_image.convert("RGBA")
    text = row["text"]
    accent = row["accent"]
    target_y = Y_POSITIONS[row["position"]]
    lines = row["display_lines"]
    line_geometry = []
    for index, line in enumerate(lines):
        center_y = target_y + (index - (len(lines) - 1) / 2) * LINE_DISTANCE
        width = font.getlength(line)
        left = (SIZE[0] - width) / 2
        bbox = font.getbbox(line)
        draw_y = center_y - (bbox[1] + bbox[3]) / 2
        line_geometry.append((line, left, draw_y, draw_y + bbox[1], draw_y + bbox[3], width))
    panel = (
        round(min(part[1] for part in line_geometry) - PANEL_PAD_X),
        round(min(part[3] for part in line_geometry) - PANEL_PAD_Y),
        round(max(part[1] + part[5] for part in line_geometry) + PANEL_PAD_X),
        round(max(part[4] for part in line_geometry) + PANEL_PAD_Y),
    )
    assert panel[0] >= 60 and panel[2] <= SIZE[0] - 60, (text, panel)
    assert 250 <= panel[1] and panel[3] <= 1450, (text, panel)

    overlay = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle(panel, radius=18, fill=(255, 255, 255, 179))
    for line, left, draw_y, _, _, _ in line_geometry:
        cursor = left
        if accent in line:
            before, after = line.split(accent, 1)
            segments = ((before, NAVY), (accent, BLUE), (after, NAVY))
        else:
            segments = ((line, NAVY),)
        for segment, color in segments:
            if segment:
                draw.text((cursor, draw_y), segment, font=font, fill=color)
                cursor += font.getlength(segment)
    return Image.alpha_composite(image, overlay).convert("RGB"), {
        "text": text,
        "characters": len(text),
        "lines": len(lines),
        "display_lines": lines,
        "x_center": SIZE[0] / 2,
        "y_center": target_y,
        "position": row["position"],
        "accent": accent,
        "panel": panel,
        "font_size": FONT_SIZE,
    }


def main() -> None:
    sources = read_sources()
    telops = read_telops()
    assert FONT_PATH.is_file(), FONT_PATH
    font = ImageFont.truetype(str(FONT_PATH), FONT_SIZE)
    OUT.mkdir(exist_ok=True)
    report = []
    for cut in range(1, 12):
        source = sources[cut]
        source_hash = sha256(source)
        result, details = render(source, telops[cut], font)
        target = OUT / f"frame_{cut:02d}_telop.png"
        result.save(target, optimize=True)
        assert sha256(source) == source_hash, source
        with Image.open(target) as check:
            assert check.size == SIZE
        report.append({"cut": cut, "source": str(source), "source_sha256": source_hash, "output": str(target), **details})

    (OUT / "telop_qa.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    thumbs = []
    for item in report:
        with Image.open(item["output"]) as image:
            thumbs.append(image.resize((235, 418), Image.Resampling.LANCZOS))
    sheet = Image.new("RGB", (235 * 4, 418 * 3), "#e5eaf0")
    for index, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((index % 4) * 235, (index // 4) * 418))
    sheet.save(OUT / "contact_sheet.png", optimize=True)
    print(f"Created {len(report)} telop frames in {OUT}")


if __name__ == "__main__":
    main()
