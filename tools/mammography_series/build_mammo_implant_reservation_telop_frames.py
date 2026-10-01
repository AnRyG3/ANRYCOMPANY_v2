from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "mammography_series" / "mammo_implant_reservation_v1"
OUTPUT_DIR = ASSET_DIR / "telop_frames"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (12, 34, 64, 255)
BLUE = (0, 112, 185, 255)
PANEL = (255, 255, 255, 179)  # White at 70% opacity.
PANEL_EDGE = (255, 255, 255, 215)
SHADOW = (8, 18, 32, 48)

FRAMES = [
    {
        "src": "samples/01_hook_reservation_hesitation_sample.png",
        "out": "telop_01_hook_reservation_hesitation.png",
        "lines": [["豊胸", ("インプラント", "blue"), "がある"], ["マンモグラフィ"], ["予約していい？"]],
        "position": "bottom",
    },
    {
        "src": "samples/02_booking_call_sample.png",
        "out": "telop_02_booking_call.png",
        "lines": [["予約時に"], [("インプラントあり", "blue"), "と"], ["先に伝えて"]],
        "position": "bottom",
    },
    {
        "src": "03_facility_room.png",
        "out": "telop_03_facility_room.png",
        "lines": [["施設によっては"], [("実施していない", "blue"), "ことも"]],
        "position": "center",
    },
    {
        "src": "04_declaration_note.png",
        "out": "telop_04_declaration_note.png",
        "lines": [["言いにくくても"], [("大切な情報", "blue"), "です"]],
        "position": "bottom",
    },
    {
        "src": "05_mammography_compression_unit.png",
        "out": "telop_05_mammography_compression_unit.png",
        "lines": [["マンモグラフィは"], [("圧迫", "blue"), "して撮影します"]],
        "position": "center",
    },
    {
        "src": "06_individual_review.png",
        "out": "telop_06_individual_review.png",
        "lines": [[("安全面", "blue"), "や画像の見え方を"], ["確認します"]],
        "position": "center",
    },
    {
        "src": "07_reception_confirmation.png",
        "out": "telop_07_reception_confirmation.png",
        "lines": [["検診では"], ["施設ごとに", ("対応", "blue"), "が異なります"]],
        "position": "center",
    },
    {
        "src": "08_consultation_destination.png",
        "out": "telop_08_consultation_destination.png",
        "lines": [["実施できない場合は"], [("次の相談先", "blue"), "を確認"]],
        "position": "center",
    },
    {
        "src": "09_reassurance.png",
        "out": "telop_09_reassurance.png",
        "lines": [[("相談先", "blue"), "を確認して"], ["次の一歩へ"]],
        "position": "bottom",
    },
    {
        "src": "10_cta_background.png",
        "out": "telop_10_cta_background.png",
        "lines": [["予約前に見返せるよう"], [("保存", "blue"), "・", ("フォロー", "blue")]],
        "position": "center",
    },
]


def get_font(size: int) -> ImageFont.FreeTypeFont:
    if not FONT_PATH.exists():
        raise FileNotFoundError(f"Required telop font not found: {FONT_PATH}")
    return ImageFont.truetype(str(FONT_PATH), size=size)


def resize_cover(image: Image.Image) -> Image.Image:
    image = image.convert("RGB")
    scale = max(W / image.width, H / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - W) // 2
    top = (resized.height - H) // 2
    return resized.crop((left, top, left + W, top + H))


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    left, _, right, _ = draw.textbbox((0, 0), text, font=font)
    return right - left


def text_height(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    _, top, _, bottom = draw.textbbox((0, 0), text, font=font)
    return bottom - top


def line_width(draw: ImageDraw.ImageDraw, line: list, font: ImageFont.FreeTypeFont) -> int:
    return sum(text_width(draw, part[0] if isinstance(part, tuple) else part, font) for part in line)


def line_height(draw: ImageDraw.ImageDraw, line: list, font: ImageFont.FreeTypeFont) -> int:
    return max(text_height(draw, part[0] if isinstance(part, tuple) else part, font) for part in line)


def fit_font(draw: ImageDraw.ImageDraw, lines: list[list]) -> tuple[ImageFont.FreeTypeFont, int]:
    for size in range(74, 42, -2):
        font = get_font(size)
        line_gap = max(10, round(size * 0.18))
        widest = max(line_width(draw, line, font) for line in lines)
        total_h = sum(line_height(draw, line, font) for line in lines) + line_gap * (len(lines) - 1)
        if widest <= 780 and total_h <= 260:
            return font, line_gap
    return get_font(42), 10


def panel_y(position: str, panel_h: int) -> int:
    if position == "top":
        return 230
    if position == "bottom":
        return H - panel_h - 310
    return (H - panel_h) // 2


def draw_telop(source: Path, frame: dict) -> tuple[Image.Image, list[int]]:
    image = resize_cover(Image.open(source)).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    font, line_gap = fit_font(draw, frame["lines"])
    line_heights = [line_height(draw, line, font) for line in frame["lines"]]
    widest = max(line_width(draw, line, font) for line in frame["lines"])
    pad_x, pad_y = 52, 32
    panel_w = min(916, widest + pad_x * 2)
    panel_h = sum(line_heights) + line_gap * (len(line_heights) - 1) + pad_y * 2
    x0 = (W - panel_w) // 2
    y0 = panel_y(frame["position"], panel_h)
    x1, y1 = x0 + panel_w, y0 + panel_h

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((x0 + 7, y0 + 9, x1 + 7, y1 + 9), radius=30, fill=SHADOW)
    overlay.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(8)))
    draw.rounded_rectangle((x0, y0, x1, y1), radius=30, fill=PANEL)
    draw.rounded_rectangle((x0 + 5, y0 + 5, x1 - 5, y1 - 5), radius=25, outline=PANEL_EDGE, width=3)

    y = y0 + ((y1 - y0) - (sum(line_heights) + line_gap * (len(line_heights) - 1))) // 2 - 3
    for line, height in zip(frame["lines"], line_heights):
        x = (W - line_width(draw, line, font)) // 2
        for part in line:
            text, color = part if isinstance(part, tuple) else (part, "navy")
            draw.text((x, y), text, font=font, fill=BLUE if color == "blue" else NAVY)
            x += text_width(draw, text, font)
        y += height + line_gap

    image.alpha_composite(overlay)
    return image.convert("RGB"), [x0, y0, x1, y1]


def make_contact_sheet(paths: list[Path], output: Path) -> None:
    cols, thumb_w, thumb_h, label_h = 5, 216, 384, 40
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (246, 248, 250))
    draw = ImageDraw.Draw(sheet)
    label_font = get_font(20)
    for index, path in enumerate(paths):
        thumb = Image.open(path).convert("RGB")
        thumb.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (index % cols) * thumb_w
        y = (index // cols) * (thumb_h + label_h)
        sheet.paste(thumb, (x + (thumb_w - thumb.width) // 2, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill=(255, 255, 255))
        draw.text((x + 8, y + thumb_h + 8), f"{index + 1:02d}", font=label_font, fill=NAVY)
    sheet.save(output, quality=94)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    manifest = []
    text_lines = []
    for index, frame in enumerate(FRAMES, start=1):
        source = ASSET_DIR / frame["src"]
        output = OUTPUT_DIR / frame["out"]
        if not source.exists():
            raise FileNotFoundError(source)
        image, box = draw_telop(source, frame)
        image.save(output, quality=95)
        outputs.append(output)
        telop_lines = ["".join(part[0] if isinstance(part, tuple) else part for part in line) for line in frame["lines"]]
        highlighted = [part[0] for line in frame["lines"] for part in line if isinstance(part, tuple) and part[1] == "blue"]
        text_lines.append(f"{index:02d}. {' / '.join(telop_lines)} [{frame['position']}]")
        manifest.append({
            "index": index,
            "source": str(source.relative_to(ROOT)),
            "output": str(output.relative_to(ROOT)),
            "telop": telop_lines,
            "highlights": highlighted,
            "position": frame["position"],
            "box": box,
            "font": str(FONT_PATH.relative_to(ROOT)),
        })

    contact_sheet = OUTPUT_DIR / "contact_sheet_telop_frames.png"
    make_contact_sheet(outputs, contact_sheet)
    (OUTPUT_DIR / "telop_manifest.json").write_text(
        json.dumps({
            "title": "豊胸インプラントがある、マンモグラフィは予約していい？",
            "style": "要点だけ、1画面1メッセージ、X軸中央、上・中央・下のみ、白角丸背景70%不透明、濃紺文字、重要語だけ青強調",
            "frames": manifest,
        }, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8-sig",
    )
    (OUTPUT_DIR / "telop_texts.txt").write_text("\n".join(text_lines) + "\n", encoding="utf-8-sig")
    print(f"created {len(outputs)} telop frames")
    print(contact_sheet)


if __name__ == "__main__":
    main()
