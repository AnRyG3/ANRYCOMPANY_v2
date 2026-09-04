from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
INPUT_DIR = ROOT / "reel_assets" / "libre2_xray_ct_20260831" / "backgrounds"
OUTPUT_DIR = ROOT / "reel_assets" / "libre2_xray_ct_20260831" / "telop_frames"
CONTACT_SHEET = OUTPUT_DIR / "_qa_contact_sheet_telop.png"
TEXTS = OUTPUT_DIR / "telop_texts_20260831.txt"
MANIFEST = OUTPUT_DIR / "telop_manifest_20260831.json"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (12, 34, 64, 255)
ACCENT_BLUE = (0, 108, 190, 255)
ACCENT_SAVE = (218, 145, 25, 255)
PANEL = (255, 255, 255, 242)
PANEL_EDGE = (255, 255, 255, 255)
SHADOW = (8, 18, 32, 58)

Y_POSITIONS = {
    "top": 300,
    "center": H // 2,
    "bottom": 1370,
}

CUTS = [
    {
        "src": "frame_01_patient_home_sensor.png",
        "out": "telop_01_patient_home_sensor.png",
        "lines": [[("このセンサー", "blue")], ["検査で外すのかな..."]],
        "position": "center",
    },
    {
        "src": "frame_02_reception_sensor_notice.png",
        "out": "telop_02_reception_sensor_notice.png",
        "lines": [["まず", ("つけてます", "blue"), "と"], ["伝えてください"]],
        "position": "center",
    },
    {
        "src": "frame_03_rt_instruction_update.png",
        "out": "telop_03_rt_instruction_update.png",
        "lines": [[("リブレ2", "blue"), "の説明書が"], [("改訂", "blue"), "されました"]],
        "position": "bottom",
    },
    {
        "src": "frame_04_old_instruction_leaflet.png",
        "out": "telop_04_old_instruction_leaflet.png",
        "lines": [["以前は", ("X線・CT", "blue"), "でも"], ["外す案内がありました"]],
        "position": "center",
    },
    {
        "src": "frame_05_ct_room_sensor_check.png",
        "out": "telop_05_ct_room_sensor_check.png",
        "lines": [[("X線・CT", "blue"), "は"], ["原則外す必要はありません"]],
        "position": "center",
    },
    {
        "src": "frame_06_mri_entrance_remove.png",
        "out": "telop_06_mri_entrance_remove.png",
        "lines": [[("MRI", "blue"), "は今まで通り"], ["検査前に外します"]],
        "position": "center",
    },
    {
        "src": "frame_07_instruction_transition.png",
        "out": "telop_07_instruction_transition.png",
        "lines": [[("10月以降", "blue"), "に順次"], ["表示が切り替わります"]],
        "position": "center",
    },
    {
        "src": "frame_08_rt_questionnaire_check.png",
        "out": "telop_08_rt_questionnaire_check.png",
        "lines": [["古い説明書の時も"], ["現場で", ("確認", "blue"), "します"]],
        "position": "bottom",
    },
    {
        "src": "frame_09_patient_tells_rt.png",
        "out": "telop_09_patient_tells_rt.png",
        "lines": [["迷ったら"], ["遠慮なく", ("伝えて", "blue"), "OK"]],
        "position": "center",
    },
    {
        "src": "frame_10_save_cta_phone.png",
        "out": "telop_10_save_cta_phone.png",
        "lines": [["検査前日・受付前に"], ["見返せるよう", ("保存", "save")]],
        "position": "top",
    },
]


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size)


def cover(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")
    scale = max(W / img.width, H / img.height)
    resized = img.resize((int(img.width * scale), int(img.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - W) // 2
    top = (resized.height - H) // 2
    return resized.crop((left, top, left + W, top + H))


def segment_text(segment):
    return segment[0] if isinstance(segment, tuple) else segment


def segment_mark(segment):
    return segment[1] if isinstance(segment, tuple) else None


def text_width(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=fnt)
    return bbox[2] - bbox[0]


def text_height(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=fnt)
    return bbox[3] - bbox[1]


def line_width(draw: ImageDraw.ImageDraw, line: list, fnt: ImageFont.FreeTypeFont) -> int:
    gap = int(fnt.size * 0.05)
    parts = [segment_text(segment) for segment in line]
    return sum(text_width(draw, text, fnt) for text in parts) + gap * max(0, len(parts) - 1)


def line_height(draw: ImageDraw.ImageDraw, line: list, fnt: ImageFont.FreeTypeFont) -> int:
    heights = [text_height(draw, segment_text(segment), fnt) for segment in line]
    return max(heights) if heights else 0


def fit_font(draw: ImageDraw.ImageDraw, lines: list[list], max_w: int, max_h: int):
    for size in range(68, 39, -2):
        fnt = font(size)
        spacing = max(12, int(size * 0.24))
        width = max(line_width(draw, line, fnt) for line in lines)
        height = sum(line_height(draw, line, fnt) for line in lines) + spacing * (len(lines) - 1)
        if width <= max_w and height <= max_h:
            return fnt, spacing
    return font(40), 10


def color_for(mark: str | None):
    if mark == "blue":
        return ACCENT_BLUE
    if mark == "save":
        return ACCENT_SAVE
    return NAVY


def box_top(position: str, box_h: int) -> int:
    center_y = Y_POSITIONS[position]
    if position == "top":
        return center_y
    if position == "bottom":
        return center_y - box_h
    return center_y - box_h // 2


def draw_telop(img: Image.Image, lines: list[list], position: str) -> Image.Image:
    base = cover(img).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")

    fnt, spacing = fit_font(draw, lines, 820, 185)
    line_heights = [line_height(draw, line, fnt) for line in lines]
    total_h = sum(line_heights) + spacing * (len(lines) - 1)
    pad_x, pad_y = 58, 40
    box_w = min(920, max(line_width(draw, line, fnt) for line in lines) + pad_x * 2)
    box_h = total_h + pad_y * 2
    x1 = (W - box_w) // 2
    y1 = box_top(position, box_h)
    x2 = x1 + box_w
    y2 = y1 + box_h

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow, "RGBA")
    shadow_draw.rounded_rectangle((x1 + 6, y1 + 8, x2 + 6, y2 + 8), radius=30, fill=SHADOW)
    overlay.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(10)))
    draw.rounded_rectangle((x1, y1, x2, y2), radius=30, fill=PANEL)
    draw.rounded_rectangle((x1 + 6, y1 + 6, x2 - 6, y2 - 6), radius=24, outline=PANEL_EDGE, width=3)

    yy = y1 + pad_y + int(fnt.size * 0.08)
    gap = int(fnt.size * 0.05)
    for line, line_h in zip(lines, line_heights):
        width = line_width(draw, line, fnt)
        xx = (W - width) // 2
        for segment in line:
            text = segment_text(segment)
            mark = segment_mark(segment)
            draw.text((xx, yy), text, font=fnt, fill=color_for(mark))
            xx += text_width(draw, text, fnt) + gap
        yy += line_h + spacing

    base.alpha_composite(overlay)
    return base.convert("RGB")


def plain_line(line: list) -> str:
    return "".join(segment_text(segment) for segment in line)


def make_contact_sheet(paths: list[Path]) -> None:
    cols = 2
    thumb_w, thumb_h = 270, 480
    label_h = 42
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (244, 246, 248))
    label_font = font(20)
    draw = ImageDraw.Draw(sheet)
    for idx, path in enumerate(paths):
        thumb = cover(Image.open(path))
        thumb.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (idx % cols) * thumb_w
        y = (idx // cols) * (thumb_h + label_h)
        sheet.paste(thumb, (x + (thumb_w - thumb.width) // 2, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill=(255, 255, 255))
        draw.text((x + 10, y + thumb_h + 8), f"{idx + 1:02d} {path.stem[:18]}", font=label_font, fill=NAVY)
    sheet.save(CONTACT_SHEET, quality=94)


def main() -> None:
    if not FONT_PATH.exists():
        raise FileNotFoundError(f"Required telop font not found: {FONT_PATH}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    outputs = []
    text_rows = []
    manifest = []
    for idx, cut in enumerate(CUTS, start=1):
        src = INPUT_DIR / cut["src"]
        out = OUTPUT_DIR / cut["out"]
        if not src.exists():
            raise FileNotFoundError(src)
        result = draw_telop(Image.open(src), cut["lines"], cut["position"])
        result.save(out, quality=95)
        outputs.append(out)
        telop_lines = [plain_line(line) for line in cut["lines"]]
        text_rows.append(f"{idx:02d}. {' / '.join(telop_lines)}")
        manifest.append(
            {
                "index": idx,
                "source": str(src.relative_to(ROOT)),
                "output": str(out.relative_to(ROOT)),
                "telop": telop_lines,
                "highlights": [
                    segment_text(segment)
                    for line in cut["lines"]
                    for segment in line
                    if segment_mark(segment) in {"blue", "save"}
                ],
                "x_axis": "center",
                "position": cut["position"],
                "font": str(FONT_PATH),
            }
        )

    make_contact_sheet(outputs)
    TEXTS.write_text("\n".join(text_rows) + "\n", encoding="utf-8-sig")
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(f"created {len(outputs)} telop frames")
    print(OUTPUT_DIR)
    print(CONTACT_SHEET)


if __name__ == "__main__":
    main()
