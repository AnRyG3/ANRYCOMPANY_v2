from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
UNIT = ROOT / "reel_assets" / "echo_series" / "10_heart_echo_onepiece_v1_samples"
MANIFEST = UNIT / "production_manifest.md"
OUT = UNIT / "telop_frames"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

WIDTH, HEIGHT = 1080, 1920
FONT_SIZE = 58
PANEL_WIDTH = 820
PANEL_CENTER_X = WIDTH // 2
PANEL_CENTER_Y = HEIGHT // 2
NAVY = (12, 34, 58, 255)
BLUE = (0, 104, 150, 255)
WHITE_70 = (255, 255, 255, 178)

FRAMES = [
    (1, ("心臓エコーでワンピース", "対応は施設ごと"), "施設ごと"),
    (2, ("上下別にすればよかった？",), None),
    (3, ("胸部に機器を当てる検査",), "胸部"),
    (4, ("胸部を出せるよう調整",), None),
    (5, ("ワンピースを控える施設も",), "ワンピース"),
    (6, ("検査着がある施設も",), "検査着"),
    (7, ("気になれば担当者に相談",), "相談"),
    (8, ("次回は案内票で服装確認",), "服装"),
]


def read_sources() -> list[Path]:
    rows = re.findall(r"^\| (\d{2}) \| ([A-Z]:\\[^|]+?) \|", MANIFEST.read_text(encoding="utf-8"), re.M)
    if [int(number) for number, _ in rows] != list(range(1, 9)):
        raise RuntimeError("Manifest source count or cut order mismatch")
    sources = [Path(path.strip()) for _, path in rows]
    for source in sources:
        if not source.is_file():
            raise FileNotFoundError(source)
    if len({str(source).lower() for source in sources}) != 8:
        raise RuntimeError("Duplicate image in source manifest")
    return sources


def line_width(draw: ImageDraw.ImageDraw, line: str, font: ImageFont.FreeTypeFont) -> int:
    return round(draw.textlength(line, font=font))


def draw_line(
    draw: ImageDraw.ImageDraw,
    line: str,
    highlight: str | None,
    font: ImageFont.FreeTypeFont,
    top: int,
) -> None:
    full_width = line_width(draw, line, font)
    x = PANEL_CENTER_X - full_width // 2
    if highlight is None or highlight not in line:
        draw.text((x, top), line, font=font, fill=NAVY, anchor="lt")
        return
    before, after = line.split(highlight, 1)
    for part, color in ((before, NAVY), (highlight, BLUE), (after, NAVY)):
        if part:
            draw.text((x, top), part, font=font, fill=color, anchor="lt")
            x += line_width(draw, part, font)


def render(source: Path, lines: tuple[str, ...], highlight: str | None) -> tuple[Image.Image, dict]:
    with Image.open(source) as opened:
        base = opened.convert("RGB").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    font = ImageFont.truetype(str(FONT_PATH), FONT_SIZE)
    measure = ImageDraw.Draw(base)
    widths = [line_width(measure, line, font) for line in lines]
    if max(widths) > PANEL_WIDTH - 90:
        raise RuntimeError(f"Text too wide at fixed font size: {lines}")

    line_height = 72
    panel_height = 76 + line_height * len(lines)
    x0 = PANEL_CENTER_X - PANEL_WIDTH // 2
    y0 = PANEL_CENTER_Y - panel_height // 2
    x1, y1 = x0 + PANEL_WIDTH, y0 + panel_height
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        (x0 + 5, y0 + 7, x1 + 5, y1 + 7), radius=28, fill=(0, 0, 0, 38)
    )
    overlay.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(8)))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle((x0, y0, x1, y1), radius=28, fill=WHITE_70)
    for index, line in enumerate(lines):
        draw_line(draw, line, highlight, font, y0 + 35 + index * line_height)
    rendered = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")
    return rendered, {
        "source": str(source),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "lines": list(lines),
        "characters": sum(len(line) for line in lines),
        "line_count": len(lines),
        "highlight": highlight,
        "panel_box": [x0, y0, x1, y1],
        "panel_center": [PANEL_CENTER_X, PANEL_CENTER_Y],
        "font": str(FONT_PATH),
        "font_size": FONT_SIZE,
        "panel_opacity": 0.7,
    }


def make_contact_sheet(paths: list[Path]) -> Path:
    thumb_w, thumb_h, label_h, cols = 270, 480, 34, 4
    sheet = Image.new("RGB", (cols * thumb_w, 2 * (thumb_h + label_h)), (245, 247, 249))
    draw = ImageDraw.Draw(sheet)
    label_font = ImageFont.truetype(str(FONT_PATH), 20)
    for index, path in enumerate(paths):
        with Image.open(path) as opened:
            thumb = opened.convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (index % cols) * thumb_w
        y = (index // cols) * (thumb_h + label_h)
        sheet.paste(thumb, (x, y))
        draw.text((x + 8, y + thumb_h + 5), f"{index + 1:02d}", font=label_font, fill=NAVY)
    output = OUT / "contact_sheet.png"
    sheet.save(output)
    return output


def main() -> None:
    if not FONT_PATH.is_file():
        raise FileNotFoundError(FONT_PATH)
    sources = read_sources()
    OUT.mkdir(exist_ok=True)
    records = []
    output_paths = []
    for (cut, lines, highlight), source in zip(FRAMES, sources, strict=True):
        count = sum(len(line) for line in lines)
        if count > 20 or len(lines) > 2:
            raise RuntimeError(f"Text length/line limit exceeded: {cut}")
        if highlight is not None and sum(line.count(highlight) for line in lines) != 1:
            raise RuntimeError(f"Highlight must occur once: {cut}")
        image, record = render(source, lines, highlight)
        output = OUT / f"telop_{cut:02d}.png"
        image.save(output)
        record["cut"] = cut
        record["output"] = str(output)
        records.append(record)
        output_paths.append(output)
    contact = make_contact_sheet(output_paths)
    (OUT / "telop_manifest.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Created {len(records)} telop frames and {contact}")


if __name__ == "__main__":
    main()
