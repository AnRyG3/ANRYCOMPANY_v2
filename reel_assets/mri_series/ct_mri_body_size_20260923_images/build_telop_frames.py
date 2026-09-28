from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


BASE = Path(r"F:\ANRYCAMPANY\reel_assets\mri_series\ct_mri_body_size_20260923_images")
OUTPUT_DIR = BASE / "telop_frames"
CONTACT_SHEET = OUTPUT_DIR / "contact_sheet_telop_frames.png"
MANIFEST = OUTPUT_DIR / "telop_manifest.json"
FONT_PATH = Path(r"F:\ANRYCAMPANY\reel_assets\fonts\M_PLUS_Rounded_1c\MPLUSRounded1c-Bold.ttf")

W, H = 1080, 1920
NAVY = (10, 32, 58, 255)
BLUE = (30, 105, 178, 255)
PANEL = (255, 255, 255, 179)  # white at 70% opacity
PANEL_EDGE = (255, 255, 255, 206)
SHADOW = (8, 18, 32, 60)
CENTER_BOX = (70, 795, 1010, 1115)
TOP_BOX = (70, 330, 1010, 650)
BOTTOM_BOX = (70, 1210, 1010, 1530)

# All telops keep horizontal center alignment. Blue is limited to key terms.
FRAMES = [
    ("01_mri_table_hook.png", "01_hook.png", [[("CT・MRI", "blue"), "の検査台"], ["私でも乗れる？"]], "bottom"),
    ("02_ct_table_consult.png", "02_consult.png", [["心配なときは"], [("予約時", "blue"), "に相談できます"]], "bottom"),
    ("03_mri_equipment_conditions.png", "03_equipment_conditions.png", [["装置ごとに"], [("条件", "blue"), "が異なります"]], "bottom"),
    ("04_ct_equipment_conditions.png", "04_check_items.png", [["体格や検査部位で"], [("確認内容", "blue"), "も変わります"]], "bottom"),
    ("05_reservation_memo_phone.png", "05_tell_body_size.png", [[("予約時", "blue"), "に"], [("体格", "blue"), "を伝える"]], "center"),
    ("06_reception_confirmation.png", "06_advance_check.png", [[("事前", "blue"), "にわかると"], ["確認しやすくなります"]], "top"),
    ("07_safety_confirmation.png", "07_for_safety.png", [[("安全", "blue"), "な検査のための"], [("確認", "blue"), "です"]], "top"),
    ("08_consult_reservation_desk.png", "08_ask_reservation_desk.png", [["まずは"], [("予約先", "blue"), "へ相談を"]], "center"),
    ("09_save_before_appointment.png", "09_save_cta.png", [[("保存", "blue"), "して"], ["予約前に見返す"]], "center"),
    ("10_follow_cta_background.png", "10_follow_cta.png", [["役立ったら"], [("フォロー", "blue"), "をお願いします"]], "center"),
]


def font(size: int) -> ImageFont.FreeTypeFont:
    if not FONT_PATH.exists():
        raise FileNotFoundError(f"Telop font not found: {FONT_PATH}")
    return ImageFont.truetype(str(FONT_PATH), size=size)


def cover_resize(image: Image.Image) -> Image.Image:
    image = image.convert("RGB")
    scale = max(W / image.width, H / image.height)
    width, height = round(image.width * scale), round(image.height * scale)
    image = image.resize((width, height), Image.Resampling.LANCZOS)
    left, top = (width - W) // 2, (height - H) // 2
    return image.crop((left, top, left + W, top + H))


def parts(line: list) -> list[str]:
    return [part[0] if isinstance(part, tuple) else part for part in line]


def line_width(draw: ImageDraw.ImageDraw, line: list, fnt: ImageFont.FreeTypeFont) -> int:
    return sum(draw.textbbox((0, 0), text, font=fnt)[2] for text in parts(line))


def line_height(draw: ImageDraw.ImageDraw, line: list, fnt: ImageFont.FreeTypeFont) -> int:
    return max(draw.textbbox((0, 0), text, font=fnt)[3] for text in parts(line))


def fit_font(draw: ImageDraw.ImageDraw, lines: list[list], max_width: int, max_height: int):
    for size in range(82, 43, -2):
        fnt = font(size)
        gap = max(14, round(size * 0.24))
        width = max(line_width(draw, line, fnt) for line in lines)
        height = sum(line_height(draw, line, fnt) for line in lines) + gap * (len(lines) - 1)
        if width <= max_width and height <= max_height:
            return fnt, gap
    return font(42), 14


def text_color(mark: str | None):
    return BLUE if mark == "blue" else NAVY


def add_telop(image: Image.Image, lines: list[list], box: tuple[int, int, int, int]) -> Image.Image:
    x0, y0, x1, y1 = box
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((x0 + 8, y0 + 10, x1 + 8, y1 + 10), radius=34, fill=SHADOW)
    image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(10)))

    draw = ImageDraw.Draw(image, "RGBA")
    draw.rounded_rectangle(box, radius=34, fill=PANEL)
    draw.rounded_rectangle((x0 + 7, y0 + 7, x1 - 7, y1 - 7), radius=29, outline=PANEL_EDGE, width=4)

    fnt, gap = fit_font(draw, lines, (x1 - x0) - 100, (y1 - y0) - 80)
    heights = [line_height(draw, line, fnt) for line in lines]
    total_height = sum(heights) + gap * (len(lines) - 1)
    y = y0 + ((y1 - y0) - total_height) // 2 - 4

    for line, height in zip(lines, heights):
        x = x0 + ((x1 - x0) - line_width(draw, line, fnt)) // 2
        for part in line:
            text, mark = part if isinstance(part, tuple) else (part, None)
            draw.text((x, y), text, font=fnt, fill=text_color(mark))
            x += draw.textbbox((0, 0), text, font=fnt)[2]
        y += height + gap
    return image


def make_contact_sheet(paths: list[Path]) -> None:
    cols, thumb_w, thumb_h, label_h = 5, 216, 384, 38
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (244, 246, 248))
    draw = ImageDraw.Draw(sheet)
    label_font = font(22)
    for index, path in enumerate(paths):
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (index % cols) * thumb_w
        y = (index // cols) * (thumb_h + label_h)
        sheet.paste(image, (x + (thumb_w - image.width) // 2, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill="white")
        draw.text((x + 10, y + thumb_h + 7), f"{index + 1:02d}", font=label_font, fill=NAVY)
    sheet.save(CONTACT_SHEET, quality=95)


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    outputs, manifest_frames = [], []
    boxes = {"top": TOP_BOX, "center": CENTER_BOX, "bottom": BOTTOM_BOX}
    for source_name, output_name, lines, position in FRAMES:
        source = BASE / source_name
        output = OUTPUT_DIR / output_name
        if not source.exists():
            raise FileNotFoundError(source)
        frame = add_telop(cover_resize(Image.open(source)).convert("RGBA"), lines, boxes[position])
        frame.convert("RGB").save(output, quality=95)
        outputs.append(output)
        manifest_frames.append({
            "source": source.name,
            "output": output.name,
            "telop": ["".join(parts(line)) for line in lines],
            "position": position,
        })
    make_contact_sheet(outputs)
    MANIFEST.write_text(json.dumps({
        "title": "体格が気になる、CTやMRIの検査台に乗れる？",
        "style": "white rounded rectangle at 70% opacity; dark navy M PLUS Rounded 1c Bold; blue only for key terms",
        "position_policy": "horizontal center only; frames 1-4 bottom, frames 6-7 top, all others center",
        "frames": manifest_frames,
    }, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(f"created {len(outputs)} telop frames in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
