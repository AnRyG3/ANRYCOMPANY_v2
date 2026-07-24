from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BASE = Path(__file__).resolve().parent
OUT = BASE / "telop_frames"
FONT = Path(r"F:\ANRYCAMPANY\reel_assets\fonts\M_PLUS_Rounded_1c\MPLUSRounded1c-Bold.ttf")
CENTER = -1.0


TELOPS = [
    ("frame_01_mri_room_entrance_patient_f50.png", "telop_01_mri_room_entrance_patient_f50.png", ["MRI、狭くて", "こわい..."], 0.48, 0.125),
    ("frame_02_patient_looks_at_mri_bore.png", "telop_02_patient_looks_at_mri_bore.png", ["狭いところが苦手だと", "不安ですよね"], CENTER, 0.380),
    ("frame_03_reassuring_validation.png", "telop_03_reassuring_validation.png", ["その気持ち", "おかしくありません"], CENTER, 0.420),
    ("frame_04_clean_mri_room.png", "telop_04_clean_mri_room.png", ["閉所不安は", "珍しくありません"], CENTER, 0.125),
    ("frame_05_pre_exam_anxiety_consult.png", "telop_05_pre_exam_anxiety_consult.png", ["検査前に", "伝えてください"], CENTER, 0.380),
    ("frame_06_signal_method_check.png", "telop_06_signal_method_check.png", ["合図の方法を", "確認できます"], 0.48, 0.125),
    ("frame_07_strong_anxiety_consult.png", "telop_07_strong_anxiety_consult.png", ["強い不安は", "医師に相談を"], CENTER, 0.390),
    ("frame_08_patient_hesitation.png", "telop_08_patient_hesitation.png", ["弱いから、では", "ありません"], CENTER, 0.430),
    ("frame_09_reassuring_conversation.png", "telop_09_reassuring_conversation.png", ["先に伝えると", "一緒に考えやすい"], CENTER, 0.400),
    ("frame_10_save_cta_patient_phone.png", "telop_10_save_cta_patient_phone.png", ["保存して", "検査前に見返す"], CENTER, 0.370),
]


def text_bbox(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int, int, int]:
    return draw.textbbox((0, 0), text, font=font)


def fit_font(draw: ImageDraw.ImageDraw, lines: list[str], max_width: int, start_size: int) -> ImageFont.FreeTypeFont:
    size = start_size
    while size >= 44:
        font = ImageFont.truetype(str(FONT), size)
        widest = max(text_bbox(draw, line, font)[2] for line in lines)
        if widest <= max_width:
            return font
        size -= 2
    return ImageFont.truetype(str(FONT), size)


def rounded_telop(img: Image.Image, lines: list[str], x_frac: float, y_frac: float) -> Image.Image:
    img = img.convert("RGBA")
    w, h = img.size
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    margin_x = int(w * 0.075)
    max_box_w = int(w * 0.75)
    top_y = int(h * y_frac)
    pad_x = int(w * 0.045)
    pad_y = int(h * 0.018)
    gap = int(h * 0.006)
    radius = int(w * 0.035)

    font = fit_font(draw, lines, max_box_w - pad_x * 2, int(w * 0.061))
    heights = []
    widths = []
    for line in lines:
        bbox = text_bbox(draw, line, font)
        widths.append(bbox[2] - bbox[0])
        heights.append(bbox[3] - bbox[1])

    line_h = max(heights)
    text_w = max(widths)
    box_w = min(max_box_w, text_w + pad_x * 2)
    box_h = line_h * len(lines) + gap * (len(lines) - 1) + pad_y * 2

    if x_frac == CENTER:
        x0 = int((w - box_w) / 2)
    else:
        x0 = int(w * x_frac)
    x0 = max(margin_x, min(x0, w - margin_x - box_w))
    y0 = top_y
    x1 = x0 + box_w
    y1 = y0 + box_h

    draw.rounded_rectangle((x0, y0, x1, y1), radius=radius, fill=(255, 255, 255, 232))

    navy = (24, 43, 69, 255)
    current_y = y0 + pad_y
    for line, tw in zip(lines, widths):
        tx = x0 + (box_w - tw) / 2
        draw.text((tx, current_y), line, font=font, fill=navy)
        current_y += line_h + gap

    return Image.alpha_composite(img, overlay).convert("RGB")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for src_name, out_name, lines, x_frac, y_frac in TELOPS:
        src = BASE / src_name
        out = OUT / out_name
        img = Image.open(src)
        rounded_telop(img, lines, x_frac, y_frac).save(out, quality=95)
        print(out)


if __name__ == "__main__":
    main()
