from __future__ import annotations

import json
import math
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
MANIFEST = ROOT / "reel_assets" / "mri_series" / "mri_sleep_20261007_images" / "production_manifest.md"
OUTPUT_DIR = ROOT / "reel_assets" / "mri_series" / "mri_sleep_20261007_telop_frames"
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

# One screen, one message. Every frame stays centered on the x axis.
# Blue emphasis is restricted to the shortest useful keyword or phrase.
FRAMES = [
    {
        "out": "telop_01_hook.png",
        "segments": [["MRI中、", ("寝ても", "blue"), "いい？"], ["検査によっては大丈夫"]],
        "position": "bottom",
    },
    {
        "out": "telop_02_may_sleep.png",
        "segments": [["頭・背骨・関節などは"], [("眠っても", "blue"), "よい場合も"]],
        "position": "bottom",
    },
    {
        "out": "telop_03_motion_blur.png",
        "segments": [["ただし体が", ("動く", "blue"), "と"], ["画像がぶれることも"]],
        "position": "center",
    },
    {
        "out": "telop_04_staff_voice.png",
        "segments": [["動いてしまったら"], [("声", "blue"), "をかけることも"]],
        "position": "bottom",
    },
    {
        "out": "telop_05_breath_hold.png",
        "segments": [["お腹などの検査は"], [("息止め", "blue"), "の合図が必要なことも"]],
        "position": "bottom",
    },
    {
        "out": "telop_06_stay_awake.png",
        "segments": [[("合図", "blue"), "がある検査では"], ["起きているようお願いすることも"]],
        "position": "bottom",
    },
    {
        "out": "telop_07_tell_before_exam.png",
        "segments": [["眠りそうで心配なら"], [("検査前", "blue"), "に伝えてください"]],
        "position": "center",
    },
    {
        "out": "telop_08_question_phrase.png",
        "segments": [["確認するのは"], [("息止めの合図", "blue"), "はありますか？"]],
        "position": "bottom",
    },
    {
        "out": "telop_09_ask_staff.png",
        "segments": [["自分の検査について"], [("担当者", "blue"), "に確認できます"]],
        "position": "center",
    },
    {
        "out": "telop_10_follow.png",
        "segments": [["検査前の疑問に答えます"], ["よければ", ("フォロー", "blue"), "を"]],
        "position": "bottom",
    },
]


def font(size: int) -> ImageFont.FreeTypeFont:
    if not FONT_PATH.exists():
        raise FileNotFoundError(f"Required telop font not found: {FONT_PATH}")
    return ImageFont.truetype(str(FONT_PATH), size=size)


def manifest_sources() -> list[Path]:
    text = MANIFEST.read_text(encoding="utf-8-sig")
    sources = []
    for line in text.splitlines():
        match = re.match(r"^\|\s*(\d{2})\s*\|\s*`([A-Z]:\\[^`]+\.png)`\s*\|", line)
        if match:
            sources.append(Path(match.group(2)))
    return sources


def verify_source_lock() -> list[Path]:
    locked = manifest_sources()
    if len(locked) != len(FRAMES):
        raise RuntimeError(
            f"production_manifest.md must contain {len(FRAMES)} approved images, found {len(locked)}"
        )
    missing = [str(path) for path in locked if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing approved source images:\n" + "\n".join(missing))
    if len(set(locked)) != len(locked):
        raise RuntimeError("The production manifest contains a duplicate source image")
    return locked


def cover_resize(image: Image.Image) -> Image.Image:
    image = image.convert("RGB")
    scale = max(W / image.width, H / image.height)
    width, height = round(image.width * scale), round(image.height * scale)
    resized = image.resize((width, height), Image.Resampling.LANCZOS)
    left = (width - W) // 2
    top = (height - H) // 2
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
        (x0 + 8, y0 + 10, x1 + 8, y1 + 10), radius=34, fill=SHADOW
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
    y = y0 + ((y1 - y0) - total_h) // 2 - 4
    for line, height in zip(segments, heights):
        x = x0 + ((x1 - x0) - line_width(draw, line, fnt)) // 2
        for part in line:
            text, color = part if isinstance(part, tuple) else (part, "navy")
            draw.text((x, y), text, font=fnt, fill=BLUE if color == "blue" else NAVY)
            x += text_size(draw, text, fnt)[0]
        y += height + spacing


def make_contact_sheet(paths: list[Path], output: Path) -> None:
    columns, thumb_w, thumb_h, label_h = 5, 216, 384, 42
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
    sheet.save(output, quality=94)


def main() -> None:
    locked_sources = verify_source_lock()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    manifest_frames = []
    text_lines = []

    for index, (source, frame) in enumerate(zip(locked_sources, FRAMES), start=1):
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
        text_lines.append(
            f"{index:02d}. {' / '.join(telop)} [{frame['position']}] blue={','.join(highlights)}"
        )
        manifest_frames.append(
            {
                "index": index,
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
                "title": "MRI中、寝ちゃっても大丈夫？",
                "input_manifest": str(MANIFEST),
                "style": "要点だけ、1画面1メッセージ、X軸中央、上・中央・下のみ、指定フレームは下段中央、その他は中央、白角丸背景70%不透明、濃紺文字、重要語だけ青強調",
                "size": {"width": W, "height": H},
                "frames": manifest_frames,
                "contact_sheet": str(contact_sheet),
                "note": "Audio and video generation are not included.",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8-sig",
    )
    (OUTPUT_DIR / "telop_texts.txt").write_text(
        "\n".join(text_lines) + "\n", encoding="utf-8-sig"
    )
    print(f"created {len(outputs)} telop frames")
    print(contact_sheet)


if __name__ == "__main__":
    main()
