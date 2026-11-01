from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
UNIT = ROOT / "reel_assets" / "mri_series" / "mri_kairo_20261109"
MANIFEST = UNIT / "production_manifest.md"
OUTPUT = UNIT / "telop_frames"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
FONT_SIZE = 64  # Fixed on every frame. Never reduce to fit.
X_CENTER = W // 2
Y_CENTERS = {"top": 300, "center": H // 2, "bottom": 1500}
PANEL_WIDTH = 920
PANEL_ALPHA = 179  # 70 percent
NAVY = (12, 34, 64, 255)
BLUE = (0, 105, 180, 255)

# A tuple marks one blue keyword. All other text stays dark navy.
FRAMES = [
    ("center", [["MRIの日、貼る", ("カイロ", "blue"), "は"], ["入室前に伝えて"]]),
    ("center", [["貼って来ても、慌てずに"]]),
    ("center", [["持ち込めない物を確認"]]),
    ("center", [[("カイロ", "blue"), "は検査前に外す"]]),
    ("center", [["背中・腰のカイロを確認"]]),
    ("center", [["身につけた物を", ("確認", "blue")]]),
    ("center", [["外す場所は案内に沿って"]]),
    ("center", [["迷ったら", ("検査担当者", "blue"), "に相談"]]),
    ("top", [[("カイロ", "blue"), "を貼っています"], ["どうすればいいですか"]]),
    ("center", [["検査前に"], ["見返せるよう", ("保存", "blue")]]),
]

SOURCE_NAMES = [
    "sample_01_arrival_PATIENT_F30_001.png",
    "sample_02_lobby_PATIENT_F30_001.png",
    "image_03_belongings.png",
    "image_04_heat_patch.png",
    "image_05_remember_PATIENT_F30_001.png",
    "image_06_checklist.png",
    "image_07_reception_guide_RECEPTION_F28_001.png",
    "image_08_exam_waiting.png",
    "image_09_patient_technologist_PATIENT_F30_001_RT_TECH_001.png",
    "image_10_locker_save.png",
]


def plain(part: str | tuple[str, str]) -> str:
    return part[0] if isinstance(part, tuple) else part


def approved_sources() -> list[Path]:
    content = MANIFEST.read_text(encoding="utf-8-sig")
    rows = re.findall(r"^\|\s*(\d{2})\s*\|\s*`([A-Z]:\\[^`]+\.png)`\s*\|", content, re.M)
    if len(rows) != len(FRAMES):
        raise ValueError(f"Expected {len(FRAMES)} manifest images, found {len(rows)}")
    if [number for number, _ in rows] != [f"{i:02d}" for i in range(1, 11)]:
        raise ValueError("Manifest cut order is not 01–10")
    sources = [Path(path) for _, path in rows]
    if [path.name for path in sources] != SOURCE_NAMES or len(set(sources)) != 10:
        raise ValueError("Actual source names/order differ from approved manifest")
    if any(path.parent != UNIT or not path.is_file() for path in sources):
        raise ValueError("Approved image is missing or outside the production unit")
    return sources


def cover_resize(source: Path) -> Image.Image:
    with Image.open(source) as original:
        image = original.convert("RGB")
    scale = max(W / image.width, H / image.height)
    size = (round(image.width * scale), round(image.height * scale))
    image = image.resize(size, Image.Resampling.LANCZOS)
    left = (image.width - W) // 2
    top = (image.height - H) // 2
    return image.crop((left, top, left + W, top + H)).convert("RGBA")


def line_text(line: list) -> str:
    return "".join(plain(part) for part in line)


def width(draw: ImageDraw.ImageDraw, line: list, font: ImageFont.FreeTypeFont) -> int:
    return sum(draw.textlength(plain(part), font=font) for part in line)


def check_text(draw: ImageDraw.ImageDraw, font: ImageFont.FreeTypeFont) -> None:
    for index, (_, lines) in enumerate(FRAMES, 1):
        if not 1 <= len(lines) <= 2:
            raise ValueError(f"Cut {index:02d}: expected 1–2 lines")
        total = sum(len(line_text(line)) for line in lines)
        if total > 20:
            raise ValueError(f"Cut {index:02d}: {total} characters exceed 20")
        for line in lines:
            if width(draw, line, font) > PANEL_WIDTH - 100:
                raise ValueError(f"Cut {index:02d}: 64px line does not fit; shorten text")
        if sum(isinstance(part, tuple) for line in lines for part in line) > 1:
            raise ValueError(f"Cut {index:02d}: too many blue terms")


def add_telop(source: Path, position: str, lines: list, font: ImageFont.FreeTypeFont) -> Image.Image:
    base = cover_resize(source)
    line_step = 84
    content_height = FONT_SIZE + (len(lines) - 1) * line_step
    panel_height = content_height + 78
    y_center = Y_CENTERS[position]
    left, top = (W - PANEL_WIDTH) // 2, round(y_center - panel_height / 2)
    right, bottom = left + PANEL_WIDTH, top + panel_height

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        (left + 5, top + 8, right + 5, bottom + 8), radius=32, fill=(8, 18, 32, 55)
    )
    base.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(11)))

    panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(panel).rounded_rectangle(
        (left, top, right, bottom), radius=32, fill=(255, 255, 255, PANEL_ALPHA)
    )
    base.alpha_composite(panel)

    draw = ImageDraw.Draw(base)
    first_y = y_center - content_height / 2
    for row, line in enumerate(lines):
        x = X_CENTER - width(draw, line, font) / 2
        y_visible = first_y + row * line_step
        for part in line:
            value = plain(part)
            color = BLUE if isinstance(part, tuple) else NAVY
            bbox = draw.textbbox((0, 0), value, font=font)
            draw.text(
                (round(x), round(y_visible - bbox[1])),
                value,
                font=font,
                fill=color,
                stroke_width=1,
                stroke_fill=(255, 255, 255, 140),
            )
            x += draw.textlength(value, font=font)
    return base.convert("RGB")


def contact_sheet(paths: list[Path]) -> None:
    thumb_w, thumb_h, label_h = 216, 384, 38
    sheet = Image.new("RGB", (thumb_w * 5, (thumb_h + label_h) * 2), (245, 246, 248))
    draw = ImageDraw.Draw(sheet)
    number_font = ImageFont.truetype(str(FONT_PATH), 22)
    for index, path in enumerate(paths):
        with Image.open(path) as frame:
            thumb = frame.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (index % 5) * thumb_w
        y = (index // 5) * (thumb_h + label_h)
        sheet.paste(thumb, (x, y))
        draw.text((x + 10, y + thumb_h + 3), f"{index + 1:02d}", fill=NAVY[:3], font=number_font)
    sheet.save(OUTPUT / "contact_sheet.png")


def main() -> None:
    sources = approved_sources()
    if not FONT_PATH.is_file():
        raise FileNotFoundError(FONT_PATH)
    font = ImageFont.truetype(str(FONT_PATH), FONT_SIZE)
    check_text(ImageDraw.Draw(Image.new("RGB", (W, H))), font)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    paths = []
    details = []
    for index, (source, (position, lines)) in enumerate(zip(sources, FRAMES), 1):
        destination = OUTPUT / f"telop_{index:02d}.png"
        add_telop(source, position, lines, font).save(destination)
        paths.append(destination)
        details.append({
            "cut": index,
            "source": str(source),
            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "output": str(destination),
            "lines": [line_text(line) for line in lines],
            "characters": sum(len(line_text(line)) for line in lines),
            "position": position,
            "x_center": X_CENTER,
            "y_center": Y_CENTERS[position],
            "font_size_px": FONT_SIZE,
            "blue_terms": [plain(part) for line in lines for part in line if isinstance(part, tuple)],
        })
    contact_sheet(paths)
    (OUTPUT / "telop_details.json").write_text(
        json.dumps({"canvas": [W, H], "font": str(FONT_PATH), "frames": details}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Rendered {len(paths)} frames at {W}x{H}; font {FONT_SIZE}px, x={X_CENTER}")


if __name__ == "__main__":
    main()
