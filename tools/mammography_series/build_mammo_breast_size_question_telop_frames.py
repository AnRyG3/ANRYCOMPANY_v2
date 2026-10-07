from __future__ import annotations

import json
import math
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "mammography_series" / "mammo_breast_size_question_v1"
PRODUCTION_MANIFEST = ASSET_DIR / "production_manifest.md"
OUTPUT_DIR = ASSET_DIR / "telop_frames"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (12, 34, 64, 255)
BLUE = (0, 112, 185, 255)
PANEL = (255, 255, 255, 179)
PANEL_EDGE = (255, 255, 255, 215)
SHADOW = (8, 18, 32, 48)

BOXES = {
    "top": (82, 252, 998, 488),
    "center": (82, 842, 998, 1078),
    "bottom": (82, 1248, 998, 1484),
}

FRAMES = [
    {
        "src": "01_hook_patient.png",
        "out": "telop_01_hook_patient.png",
        "segments": [["胸が小さいと"], [("マンモ", "blue"), "で挟めない？"]],
        "position": "center",
    },
    {
        "src": "02_answer_with_technologist.png",
        "out": "telop_02_answer_with_technologist.png",
        "segments": [["胸の大きさだけで"], ["受けられないとは", ("決まりません", "blue")]],
        "position": "center",
    },
    {
        "src": "03_position_adjustment.png",
        "out": "telop_03_position_adjustment.png",
        "segments": [[("診療放射線技師", "blue"), "が"], ["位置を調整します"]],
        "position": "center",
    },
    {
        "src": "04_individual_discomfort.png",
        "out": "telop_04_individual_discomfort.png",
        "segments": [["痛みの感じ方には"], [("個人差", "blue"), "があります"]],
        "position": "center",
    },
    {
        "src": "05_tell_before_exam.png",
        "out": "telop_05_tell_before_exam.png",
        "segments": [["不安なことは"], [("撮影前", "blue"), "に伝えてください"]],
        "position": "center",
    },
    {
        "src": "06_speak_up_during_exam.png",
        "out": "telop_06_speak_up_during_exam.png",
        "segments": [["つらくなったら"], ["その場で", ("声をかけて", "blue")]],
        "position": "center",
    },
    {
        "src": "07_history_preparation.png",
        "out": "telop_07_history_preparation.png",
        "segments": [["豊胸や乳房の", ("手術歴", "blue"), "は"], ["予約時に伝えて"]],
        "position": "center",
    },
    {
        "src": "08_facility_confirmation.png",
        "out": "telop_08_facility_confirmation.png",
        "segments": [["撮影できるか"], [("検査施設", "blue"), "へ確認を"]],
        "position": "center",
    },
    {
        "src": "09_seek_medical_care.png",
        "out": "telop_09_seek_medical_care.png",
        "segments": [["気になる症状がある方は"], ["検診を待たず", ("医療機関", "blue"), "へ"]],
        "position": "center",
    },
    {
        "src": "10_cta_background.png",
        "out": "telop_10_cta_background.png",
        "segments": [["検査前の不安に答えます"], ["よければ", ("フォロー", "blue"), "を"]],
        "position": "center",
    },
]


def font(size: int) -> ImageFont.FreeTypeFont:
    if not FONT_PATH.exists():
        raise FileNotFoundError(f"Required telop font not found: {FONT_PATH}")
    return ImageFont.truetype(str(FONT_PATH), size=size)


def manifest_sources() -> list[Path]:
    text = PRODUCTION_MANIFEST.read_text(encoding="utf-8-sig")
    sources = []
    for line in text.splitlines():
        match = re.match(r"^\|\s*(\d{2})\s*\|\s*`([A-Z]:\\[^`]+\.png)`\s*\|", line)
        if match:
            sources.append(Path(match.group(2)))
    return sources


def verify_source_lock() -> list[Path]:
    locked = manifest_sources()
    expected = [ASSET_DIR / frame["src"] for frame in FRAMES]
    if len(locked) != 10:
        raise RuntimeError(f"production_manifest.md must contain 10 approved images, found {len(locked)}")
    if locked != expected:
        raise RuntimeError("Source lock mismatch: manifest count, cut order, or absolute path differs")
    missing = [str(path) for path in locked if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing approved source images:\n" + "\n".join(missing))
    return locked


def cover_resize(image: Image.Image) -> Image.Image:
    image = image.convert("RGB")
    scale = max(W / image.width, H / image.height)
    nw, nh = round(image.width * scale), round(image.height * scale)
    resized = image.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - W) // 2
    top = (nh - H) // 2
    return resized.crop((left, top, left + W, top + H))


def part_text(part) -> str:
    return part[0] if isinstance(part, tuple) else part


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> tuple[int, int]:
    left, top, right, bottom = draw.textbbox((0, 0), text, font=fnt)
    return right - left, bottom - top


def line_width(draw: ImageDraw.ImageDraw, line: list, fnt: ImageFont.FreeTypeFont) -> int:
    return sum(text_size(draw, part_text(part), fnt)[0] for part in line)


def line_height(draw: ImageDraw.ImageDraw, line: list, fnt: ImageFont.FreeTypeFont) -> int:
    return max(text_size(draw, part_text(part), fnt)[1] for part in line)


def fit_font(draw: ImageDraw.ImageDraw, segments: list[list], max_w: int, max_h: int):
    for size in range(74, 41, -2):
        fnt = font(size)
        spacing = max(12, round(size * 0.22))
        width = max(line_width(draw, line, fnt) for line in segments)
        height = sum(line_height(draw, line, fnt) for line in segments) + spacing * (len(segments) - 1)
        if width <= max_w and height <= max_h:
            return fnt, spacing
    return font(42), 10


def draw_panel(image: Image.Image, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        (x0 + 8, y0 + 10, x1 + 8, y1 + 10),
        radius=34,
        fill=SHADOW,
    )
    image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(12)))
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rounded_rectangle(box, radius=34, fill=PANEL)
    draw.rounded_rectangle(
        (x0 + 7, y0 + 7, x1 - 7, y1 - 7),
        radius=28,
        outline=PANEL_EDGE,
        width=4,
    )


def draw_telop(image: Image.Image, frame: dict) -> None:
    box = BOXES[frame["position"]]
    x0, y0, x1, y1 = box
    segments = frame["segments"]
    draw_panel(image, box)
    draw = ImageDraw.Draw(image, "RGBA")
    fnt, spacing = fit_font(draw, segments, (x1 - x0) - 84, (y1 - y0) - 64)
    heights = [line_height(draw, line, fnt) for line in segments]
    total_h = sum(heights) + spacing * (len(segments) - 1)
    yy = y0 + ((y1 - y0) - total_h) // 2 - 4

    for line, height in zip(segments, heights):
        xx = x0 + ((x1 - x0) - line_width(draw, line, fnt)) // 2
        for part in line:
            text, color = part if isinstance(part, tuple) else (part, "navy")
            draw.text((xx, yy), text, font=fnt, fill=BLUE if color == "blue" else NAVY)
            xx += text_size(draw, text, fnt)[0]
        yy += height + spacing


def make_contact_sheet(paths: list[Path], output: Path) -> None:
    cols, thumb_w, thumb_h, label_h = 5, 216, 384, 42
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (244, 246, 248))
    draw = ImageDraw.Draw(sheet)
    label_font = font(20)
    for idx, path in enumerate(paths):
        thumb = Image.open(path).convert("RGB")
        thumb.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (idx % cols) * thumb_w
        y = (idx // cols) * (thumb_h + label_h)
        sheet.paste(thumb, (x + (thumb_w - thumb.width) // 2, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill=(255, 255, 255))
        draw.text((x + 8, y + thumb_h + 8), f"{idx + 1:02d}", font=label_font, fill=NAVY)
    sheet.save(output, quality=94)


def main() -> None:
    locked_sources = verify_source_lock()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    manifest_frames = []
    text_lines = []

    for idx, (source, frame) in enumerate(zip(locked_sources, FRAMES), start=1):
        output = OUTPUT_DIR / frame["out"]
        image = cover_resize(Image.open(source)).convert("RGBA")
        draw_telop(image, frame)
        image.convert("RGB").save(output, quality=95)
        outputs.append(output)

        telop = ["".join(part_text(part) for part in line) for line in frame["segments"]]
        highlights = [
            part[0]
            for line in frame["segments"]
            for part in line
            if isinstance(part, tuple) and part[1] == "blue"
        ]
        text_lines.append(f"{idx:02d}. {' / '.join(telop)} [{frame['position']}] blue={','.join(highlights)}")
        manifest_frames.append(
            {
                "index": idx,
                "source": str(source),
                "output": str(output),
                "telop": telop,
                "highlights": highlights,
                "position": frame["position"],
                "box": BOXES[frame["position"]],
                "font": str(FONT_PATH),
            }
        )

    contact_sheet = OUTPUT_DIR / "contact_sheet_telop_frames.png"
    make_contact_sheet(outputs, contact_sheet)
    (OUTPUT_DIR / "telop_manifest.json").write_text(
        json.dumps(
            {
                "title": "胸が小さいと、マンモで挟めない？",
                "style": "要点だけ、1画面1メッセージ、X軸中央、上・中央・下のみ、全フレーム中央配置、白角丸背景70%不透明、濃紺文字、重要語だけ青強調",
                "size": {"width": W, "height": H},
                "frames": manifest_frames,
                "contact_sheet": str(contact_sheet),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8-sig",
    )
    (OUTPUT_DIR / "telop_texts.txt").write_text(
        "\n".join(text_lines) + "\n",
        encoding="utf-8-sig",
    )
    print(f"created {len(outputs)} telop frames")
    print(contact_sheet)


if __name__ == "__main__":
    main()

