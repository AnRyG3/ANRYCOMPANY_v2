from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BASE = Path(r"F:\ANRYCAMPANY\reel_assets\fracture_xray_ct_mri_series")
SRC_DIR = BASE / "sample_frames"
OUT_DIR = BASE / "telop_frames"
FONT_PATH = Path(
    r"F:\ANRYCAMPANY\reel_assets\fonts\M_PLUS_Rounded_1c\MPLUSRounded1c-Bold.ttf"
)

SLIDES = [
    ("slide01_doctor_patient_hip_xray_sample.png", "slide01_telop.png", ["レントゲンだけでは", "足りないことも"]),
    ("slide02_patient_puzzled.png", "slide02_telop.png", ["骨折は写るはず…", "なぜ？"]),
    ("slide03_xray_room.png", "slide03_telop.png", ["レントゲンは", "最初の大切な検査"]),
    ("slide04_blurred_exam_room.png", "slide04_telop.png", ["でも、写りにくい", "骨折もあります"]),
    ("slide05_ct_room_partial.png", "slide05_telop.png", ["小さなヒビや", "骨が重なる部分など"]),
    ("slide06_ct_patient_rt_tech_sample_v2.png", "slide06_telop.png", ["CTで骨の形を", "詳しく見ることも"]),
    ("slide07_mri_room.png", "slide07_telop.png", ["場合によってはMRIで", "骨の内部も確認"]),
    ("slide08_patient_understands.png", "slide08_telop.png", ["検査には", "段階があります"]),
    ("slide09_rt_tech_reassures_patient.png", "slide09_telop.png", ["不安に感じるのは", "自然なことです"]),
    ("slide10_patient_leaves.png", "slide10_telop.png", ["見逃しを減らすための", "慎重な確認です"]),
    ("slide11_save_phone_cta_bg.png", "slide11_telop.png", ["そういう流れだったんだ", "と思ったら保存"]),
    ("slide12_rt_tech_bow_cta_bg.png", "slide12_telop.png", ["診療放射線技師の発信", "フォローで応援お願いします"]),
]

TEXT_COLOR = (12, 35, 62, 255)
BOX_COLOR = (255, 255, 255, 232)
SHADOW_COLOR = (0, 0, 0, 55)
FONT_CACHE = {}


def get_font(size):
    if size not in FONT_CACHE:
        FONT_CACHE[size] = ImageFont.truetype(str(FONT_PATH), size)
    return FONT_CACHE[size]


def fit_font(draw, lines, max_width, start=68, min_size=44):
    size = start
    while size >= min_size:
        font = get_font(size)
        widths = [draw.textbbox((0, 0), line, font=font)[2] for line in lines]
        if max(widths) <= max_width:
            return font, size
        size -= 2
    return get_font(min_size), min_size


def render_slide(index, src_name, out_name, lines):
    img = Image.open(SRC_DIR / src_name).convert("RGBA")
    width, _ = img.size
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font, size = fit_font(draw, lines, int(width * 0.78))
    line_gap = int(size * 0.22)
    bboxes = [draw.textbbox((0, 0), line, font=font) for line in lines]
    text_w = max(box[2] - box[0] for box in bboxes)
    text_h = sum(box[3] - box[1] for box in bboxes) + line_gap * (len(lines) - 1)
    pad_x = 54
    pad_y = 34
    box_w = text_w + pad_x * 2
    box_h = text_h + pad_y * 2

    y = 210
    if index in (3, 4, 5, 7):
        y = 820
    elif index in (11, 12):
        y = 210
    elif index in (6, 9, 10):
        y = 230
    x = int((width - box_w) / 2)
    rect = (x, y, x + box_w, y + box_h)

    draw.rounded_rectangle((rect[0], rect[1] + 8, rect[2], rect[3] + 8), radius=34, fill=SHADOW_COLOR)
    draw.rounded_rectangle(rect, radius=34, fill=BOX_COLOR)

    cur_y = y + pad_y
    for line, bbox in zip(lines, bboxes):
        line_w = bbox[2] - bbox[0]
        line_h = bbox[3] - bbox[1]
        text_x = int((width - line_w) / 2)
        text_y = cur_y - bbox[1]
        draw.text((text_x, text_y), line, font=font, fill=TEXT_COLOR)
        cur_y += line_h + line_gap

    Image.alpha_composite(img, overlay).convert("RGB").save(OUT_DIR / out_name, quality=95)


def build_contact_sheet():
    thumb_w, thumb_h = 270, 480
    sheet = Image.new("RGB", (thumb_w * 4, thumb_h * 3), (245, 245, 245))
    for i, (_, out_name, _) in enumerate(SLIDES):
        image = Image.open(OUT_DIR / out_name).convert("RGB").resize((thumb_w, thumb_h), Image.LANCZOS)
        sheet.paste(image, ((i % 4) * thumb_w, (i // 4) * thumb_h))
    sheet.save(OUT_DIR / "contact_sheet_telop_all_12.png", quality=92)


def main():
    OUT_DIR.mkdir(exist_ok=True)
    for index, (src_name, out_name, lines) in enumerate(SLIDES, start=1):
        render_slide(index, src_name, out_name, lines)
    build_contact_sheet()
    print(f"created {len(SLIDES)} telop frames")
    print(OUT_DIR)


if __name__ == "__main__":
    main()
