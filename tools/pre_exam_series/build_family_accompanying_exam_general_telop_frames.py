from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
IMAGE_DIR = ROOT / "reel_assets" / "family_accompanying_exam_general_images"
OUT_DIR = ROOT / "reel_assets" / "family_accompanying_exam_general_telop_frames"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

NAVY = (20, 43, 74, 255)
TEAL = (0, 128, 128, 255)
WHITE = (255, 255, 255, 232)


FRAMES = [
    (
        "approved_20260804_frame_01_exam_room_door.png",
        "approved_20260804_frame_01_exam_room_door_telop.png",
        [("親の検査、", NAVY), ("一緒に入れる？", TEAL)],
        "low",
    ),
    (
        "approved_20260804_frame_02_threshold_confusion.png",
        "approved_20260804_frame_02_threshold_confusion_telop.png",
        [("検査室前で", NAVY), ("離れることも", TEAL)],
        "low",
    ),
    (
        "approved_20260804_frame_03_empathy_hands.png",
        "approved_20260804_frame_03_empathy_hands_telop.png",
        [("その不安は", NAVY), ("自然です", TEAL)],
        "low",
    ),
    (
        "approved_20260804_frame_04_exam_type_rules.png",
        "approved_20260804_frame_04_exam_type_rules_telop.png",
        [("入れるかは", NAVY), ("検査で変わります", TEAL)],
        "center",
    ),
    (
        "approved_20260804_frame_05_ct_safety_management.png",
        "approved_20260804_frame_05_ct_safety_management_telop.png",
        [("X線・CTは", TEAL), ("外で待つことも", NAVY)],
        "center",
    ),
    (
        "approved_20260804_frame_06_waiting_outside.png",
        "approved_20260804_frame_06_waiting_outside_telop.png",
        [("離れて", TEAL), ("待つ時間もあります", NAVY)],
        "low",
    ),
    (
        "approved_20260804_frame_07_support_nearby.png",
        "approved_20260804_frame_07_support_nearby_telop.png",
        [("そばにいる方が", NAVY), ("安心な検査も", TEAL)],
        "low",
    ),
    (
        "approved_20260804_frame_08_ask_before_exam.png",
        "approved_20260804_frame_08_ask_before_exam_telop.png",
        [("事前に", TEAL), ("スタッフへ確認", NAVY)],
        "low",
    ),
    (
        "approved_20260804_frame_09_mild_concern_waiting.png",
        "approved_20260804_frame_09_mild_concern_waiting_telop.png",
        [("一人で大丈夫かな…", NAVY)],
        "low",
    ),
    (
        "approved_20260804_frame_10_staff_voice_support_v2.png",
        "approved_20260804_frame_10_staff_voice_support_telop_v2.png",
        [("声をかけながら", TEAL), ("進めます", NAVY)],
        "low",
    ),
    (
        "approved_20260804_frame_11_save_cta_background.png",
        "approved_20260804_frame_11_save_cta_background_telop.png",
        [("付き添い前に", NAVY), ("保存", TEAL)],
        "center",
    ),
    (
        "approved_20260804_frame_12_follow_cta_background.png",
        "approved_20260804_frame_12_follow_cta_background_telop.png",
        [("検査前の不安を", NAVY), ("一緒に減らす", TEAL)],
        "low",
    ),
]


def fit_font(draw: ImageDraw.ImageDraw, runs, max_width: int, start_size: int = 72) -> ImageFont.FreeTypeFont:
    for size in range(start_size, 40, -2):
        font = ImageFont.truetype(str(FONT_PATH), size)
        width = sum(draw.textbbox((0, 0), text, font=font)[2] for text, _ in runs)
        if width <= max_width:
            return font
    return ImageFont.truetype(str(FONT_PATH), 40)


def draw_telop(image_path: Path, output_path: Path, runs, position: str) -> None:
    image = Image.open(image_path).convert("RGBA")
    image = image.resize((1080, 1920), Image.Resampling.LANCZOS)
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    max_width = 920
    font = fit_font(draw, runs, max_width)
    boxes = [draw.textbbox((0, 0), text, font=font) for text, _ in runs]
    widths = [box[2] - box[0] for box in boxes]
    heights = [box[3] - box[1] for box in boxes]
    total_width = sum(widths)
    text_height = max(heights)

    pad_x = 44
    pad_y = 30
    box_width = total_width + pad_x * 2
    box_height = text_height + pad_y * 2 + 10
    x0 = (1080 - box_width) // 2
    y0 = 840 if position == "center" else 1270
    x1 = x0 + box_width
    y1 = y0 + box_height

    draw.rounded_rectangle((x0, y0, x1, y1), radius=34, fill=WHITE)

    cursor = x0 + pad_x
    baseline = y0 + pad_y - 4
    for text, color in runs:
        draw.text((cursor, baseline), text, font=font, fill=color)
        cursor += draw.textbbox((0, 0), text, font=font)[2]

    combined = Image.alpha_composite(image, overlay).convert("RGB")
    combined.save(output_path, quality=95)


def make_contact_sheet(paths: list[Path]) -> None:
    thumbs = []
    for path in paths:
        thumb = Image.open(path).convert("RGB")
        thumb.thumbnail((270, 480), Image.Resampling.LANCZOS)
        thumbs.append((path.name, thumb))

    sheet = Image.new("RGB", (1080, 4 * 540), (245, 247, 250))
    draw = ImageDraw.Draw(sheet)
    label_font = ImageFont.truetype(str(FONT_PATH), 22)
    for index, (name, thumb) in enumerate(thumbs):
        col = index % 4
        row = index // 4
        x = col * 270 + (270 - thumb.width) // 2
        y = row * 540 + 8
        sheet.paste(thumb, (x, y))
        draw.text((col * 270 + 12, row * 540 + 494), name[:30], font=label_font, fill=NAVY[:3])

    sheet.save(OUT_DIR / "_qa_contact_sheet_approved_20260804_telop.png", quality=95)


def main() -> None:
    if not FONT_PATH.exists():
        raise FileNotFoundError(FONT_PATH)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    outputs = []
    for source, target, runs, position in FRAMES:
        source_path = IMAGE_DIR / source
        output_path = OUT_DIR / target
        if not source_path.exists():
            raise FileNotFoundError(source_path)
        draw_telop(source_path, output_path, runs, position)
        outputs.append(output_path)

    make_contact_sheet(outputs)
    for output in outputs:
        print(output)
    print(OUT_DIR / "_qa_contact_sheet_approved_20260804_telop.png")


if __name__ == "__main__":
    main()
