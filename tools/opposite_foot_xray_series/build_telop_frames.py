from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
SRC = ROOT / "reel_assets" / "opposite_foot_xray_series" / "sample_frames"
OUT = ROOT / "reel_assets" / "opposite_foot_xray_series" / "text_frames"
FONT = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

SLIDES = [
    ("slide01_patient_looks_at_foot_sample.png", "01", "足の検査なのに\n反対側も撮るの？"),
    ("slide02_patient_puzzled_closeup.png", "02", "間違いでは\nありません"),
    ("slide03_exam_room_transition.png", "03", "診断のために\n必要なことがあります"),
    ("slide04_xray_like_v2.png", "04", "左右を比べると\n違いが見えやすい"),
    ("slide05_monitor_xray_like_v2.png", "05", "本来の形か\n変化かを確認"),
    ("slide06_crutches_quiet_room.png", "06", "治療方針の参考に\nなることも"),
    ("slide07_patient_understands.png", "07", "理由がわかると\n安心しやすい"),
    ("slide08_table_explanation.png", "08", "気になる時は\n遠慮なく確認を"),
    ("slide09_rt_tech_explains_sample.png", "09", "説明してから\n撮影します"),
    ("slide10_patient_leaves_room.png", "10", "不安が少し\n軽くなるように"),
    ("slide11_save_phone_cta_bg.png", "11", "この投稿を\n保存してください"),
    ("slide12_rt_tech_bow_cta_bg.png", "12", "診療放射線技師の発信\nフォローで応援お願いします"),
]

POSITIONS = {
    "03": "center",
    "06": "center",
    "08": "lower",
    "09": "lower",
    "10": "lower",
}


def fit_font(draw, text, max_width, start_size):
    size = start_size
    while size >= 34:
        font = ImageFont.truetype(str(FONT), size)
        widths = [draw.textbbox((0, 0), line, font=font)[2] for line in text.splitlines()]
        if max(widths) <= max_width:
            return font
        size -= 2
    return ImageFont.truetype(str(FONT), size)


def get_y0(position, image_h, box_h):
    if position == "center":
        return int((image_h - box_h) / 2)
    if position == "lower":
        return int(image_h * 0.69)
    return int(image_h * 0.105)


def draw_telop(image, text, position="upper"):
    base = image.convert("RGBA")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    w, h = base.size

    margin_x = int(w * 0.08)
    max_text_width = int(w * 0.76)
    font = fit_font(draw, text, max_text_width, 62)
    lines = text.splitlines()
    line_gap = int(font.size * 0.22)
    line_boxes = [draw.textbbox((0, 0), line, font=font) for line in lines]
    text_w = max(box[2] - box[0] for box in line_boxes)
    text_h = sum(box[3] - box[1] for box in line_boxes) + line_gap * (len(lines) - 1)

    pad_x = int(w * 0.055)
    pad_y = int(h * 0.022)
    box_w = min(w - margin_x * 2, text_w + pad_x * 2)
    box_h = text_h + pad_y * 2
    x0 = int((w - box_w) / 2)
    y0 = get_y0(position, h, box_h)
    x1 = x0 + box_w
    y1 = y0 + box_h

    draw.rounded_rectangle((x0, y0, x1, y1), radius=28, fill=(255, 255, 255, 232))

    y = y0 + pad_y
    for line, box in zip(lines, line_boxes):
        line_w = box[2] - box[0]
        line_h = box[3] - box[1]
        x = int((w - line_w) / 2)
        draw.text((x, y - box[1]), line, fill=(18, 38, 66, 255), font=font)
        y += line_h + line_gap

    return Image.alpha_composite(base, overlay).convert("RGB")


def make_contact_sheet(files):
    thumb_w, thumb_h = 220, 390
    margin, label_h = 18, 38
    cols = 4
    rows = 3
    sheet = Image.new(
        "RGB",
        (cols * (thumb_w + margin) + margin, rows * (thumb_h + label_h + margin) + margin),
        "white",
    )
    draw = ImageDraw.Draw(sheet)
    for i, file in enumerate(files):
        img = Image.open(file).convert("RGB").resize((thumb_w, thumb_h), Image.LANCZOS)
        x = margin + (i % cols) * (thumb_w + margin)
        y = margin + (i // cols) * (thumb_h + label_h + margin)
        sheet.paste(img, (x, y))
        draw.text((x, y + thumb_h + 4), file.stem[:28], fill=(0, 0, 0))
    sheet.save(OUT / "contact_sheet_text_frames.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    outputs = []
    for src_name, num, text in SLIDES:
        out = OUT / f"slide{num}_telop.png"
        img = Image.open(SRC / src_name)
        draw_telop(img, text, POSITIONS.get(num, "upper")).save(out, quality=95)
        outputs.append(out)
    make_contact_sheet(outputs)
    for path in outputs:
        print(path)
    print(OUT / "contact_sheet_text_frames.png")


if __name__ == "__main__":
    main()
