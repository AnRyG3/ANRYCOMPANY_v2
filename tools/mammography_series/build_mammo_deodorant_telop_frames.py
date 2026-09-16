from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "mammography_series" / "mammo_deodorant_v1"
OUTPUT_DIR = ASSET_DIR / "telop_frames"
CONTACT_SHEET = ASSET_DIR / "contact_sheet_telop_frames.png"
MANIFEST = ASSET_DIR / "telop_manifest.json"
TEXTS = ASSET_DIR / "telop_texts.txt"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (12, 34, 64, 255)
BLUE = (0, 112, 185, 255)
PANEL = (255, 255, 255, 240)
PANEL_EDGE = (255, 255, 255, 255)
SHADOW = (8, 18, 32, 58)

BOXES = {
    "top": (82, 252, 998, 488),
    "center": (82, 842, 998, 1078),
    "bottom": (82, 1248, 998, 1484),
}

FRAMES = [
    {
        "src": "01_hook_antiperspirant.png",
        "out": "telop_01_hook_antiperspirant.png",
        "segments": [["脇に", ("制汗剤", "blue"), "つけちゃった…"], ["今日のマンモ、受けられる？"]],
        "position": "top",
    },
    {
        "src": "02_tell_staff.png",
        "out": "telop_02_tell_staff.png",
        "segments": [["まずは"], [("受付", "blue"), "で伝えてください"]],
        "position": "top",
    },
    {
        "src": "03_towel_guidance.png",
        "out": "telop_03_towel_guidance.png",
        "segments": [["必要に応じて"], [("拭き取り", "blue"), "をご案内します"]],
        "position": "top",
    },
    {
        "src": "04_product_reason.png",
        "out": "telop_04_product_reason.png",
        "segments": [["画像に", ("白い点", "blue"), "として"], ["写ることがあります"]],
        "position": "center",
    },
    {
        "src": "05_mammography_room.png",
        "out": "telop_05_mammography_room.png",
        "segments": [[("石灰化", "blue"), "に似て"], ["写ることがあります"]],
        "position": "center",
    },
    {
        "src": "06_reassurance.png",
        "out": "telop_06_reassurance.png",
        "segments": [["言い出しにくくても"], [("大丈夫", "blue"), "です"]],
        "position": "top",
    },
    {
        "src": "07_tell_technologist.png",
        "out": "telop_07_tell_technologist.png",
        "segments": [["気づいた時点で"], [("スタッフ", "blue"), "に伝えてください"]],
        "position": "center",
    },
    {
        "src": "08_next_time_prepare.png",
        "out": "telop_08_next_time_prepare.png",
        "segments": [[("検査当日", "blue"), "は"], ["脇に何もつけずに"]],
        "position": "center",
    },
    {
        "src": "09_save_background.png",
        "out": "telop_09_save_background.png",
        "segments": [[("検査前日", "blue"), "に"], ["見返せるように"]],
        "position": "center",
    },
]


def font(size: int) -> ImageFont.FreeTypeFont:
    if not FONT_PATH.exists():
        raise FileNotFoundError(f"Required telop font not found: {FONT_PATH}")
    return ImageFont.truetype(str(FONT_PATH), size=size)


def cover_resize(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")
    scale = max(W / img.width, H / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - W) // 2
    top = (nh - H) // 2
    return resized.crop((left, top, left + W, top + H))


def plain_segments(line: list) -> list[str]:
    return [part[0] if isinstance(part, tuple) else part for part in line]


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> tuple[int, int]:
    left, top, right, bottom = draw.textbbox((0, 0), text, font=fnt)
    return right - left, bottom - top


def line_width(draw: ImageDraw.ImageDraw, line: list, fnt: ImageFont.FreeTypeFont) -> int:
    return sum(text_size(draw, part, fnt)[0] for part in plain_segments(line))


def line_height(draw: ImageDraw.ImageDraw, line: list, fnt: ImageFont.FreeTypeFont) -> int:
    return max(text_size(draw, part, fnt)[1] for part in plain_segments(line))


def fit_font(draw: ImageDraw.ImageDraw, segments: list[list], max_w: int, max_h: int):
    for size in range(74, 41, -2):
        fnt = font(size)
        spacing = max(12, int(size * 0.22))
        width = max(line_width(draw, line, fnt) for line in segments)
        height = sum(line_height(draw, line, fnt) for line in segments) + spacing * (len(segments) - 1)
        if width <= max_w and height <= max_h:
            return fnt, spacing
    return font(42), 10


def draw_panel(img: Image.Image, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((x0 + 8, y0 + 10, x1 + 8, y1 + 10), radius=34, fill=SHADOW)
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(12)))
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rounded_rectangle(box, radius=34, fill=PANEL)
    draw.rounded_rectangle((x0 + 7, y0 + 7, x1 - 7, y1 - 7), radius=28, outline=PANEL_EDGE, width=4)


def draw_telop(img: Image.Image, frame: dict) -> None:
    box = BOXES[frame["position"]]
    x0, y0, x1, y1 = box
    segments = frame["segments"]
    draw_panel(img, box)
    draw = ImageDraw.Draw(img, "RGBA")
    fnt, spacing = fit_font(draw, segments, (x1 - x0) - 84, (y1 - y0) - 64)
    heights = [line_height(draw, line, fnt) for line in segments]
    total_h = sum(heights) + spacing * (len(segments) - 1)
    yy = y0 + ((y1 - y0) - total_h) // 2 - 4

    for line, height in zip(segments, heights):
        xx = x0 + ((x1 - x0) - line_width(draw, line, fnt)) // 2
        for part in line:
            text, color = part if isinstance(part, tuple) else (part, NAVY)
            fill = BLUE if color == "blue" else NAVY
            draw.text((xx, yy), text, font=fnt, fill=fill)
            xx += text_size(draw, text, fnt)[0]
        yy += height + spacing


def make_contact_sheet(paths: list[Path]) -> None:
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
    sheet.save(CONTACT_SHEET, quality=94)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs, manifest_frames, text_lines = [], [], []
    for idx, frame in enumerate(FRAMES, start=1):
        source = ASSET_DIR / frame["src"]
        output = OUTPUT_DIR / frame["out"]
        if not source.exists():
            raise FileNotFoundError(source)
        image = cover_resize(Image.open(source)).convert("RGBA")
        draw_telop(image, frame)
        image.convert("RGB").save(output, quality=95)
        outputs.append(output)
        telop = ["".join(plain_segments(line)) for line in frame["segments"]]
        text_lines.append(f"{idx:02d}. {' / '.join(telop)} [{frame['position']}]")
        manifest_frames.append({"source": str(source.relative_to(ROOT)), "output": str(output.relative_to(ROOT)), "telop": telop, "position": frame["position"], "box": BOXES[frame["position"]]})

    make_contact_sheet(outputs)
    MANIFEST.write_text(json.dumps({"title": "うっかり制汗剤、マンモは受けられない？", "style": "要点だけ、1画面1メッセージ、X軸中央、上・中央・下のみ、中央優先、白角丸背景、濃紺文字、重要語だけ青強調", "font": str(FONT_PATH), "size": {"width": W, "height": H}, "frames": manifest_frames, "contact_sheet": str(CONTACT_SHEET.relative_to(ROOT))}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8-sig")
    TEXTS.write_text("\n".join(text_lines) + "\n", encoding="utf-8-sig")
    print(f"created {len(outputs)} telop frames")
    print(OUTPUT_DIR)
    print(CONTACT_SHEET)


if __name__ == "__main__":
    main()
