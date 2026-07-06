from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
SERIES = ROOT / "reel_assets" / "pediatric_movement_series"
INPUT_DIR = SERIES / "background_frames_no_text"
OUTPUT_DIR = SERIES / "telop_frames"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

TEXT_COLOR = (12, 37, 63, 255)
BOX_COLOR = (255, 255, 255, 232)
BOX_RADIUS = 26

TELOPS = {
    "01_parent_worried_no_text.png": ["じっとできるか", "心配…"],
    "02_tech_reassure_no_text.png": ["動いてしまう子は", "多いです"],
    "03_child_moves_no_text.png": ["数秒じっとするのは", "難しい"],
    "04_tech_child_timing_no_text.png": ["声かけとタイミングを", "工夫しています"],
    "05_child_attention_no_text.png": ["音や声で", "注意を引くことも"],
    "06_tech_brief_still_no_text.png": ["検査によっては", "一瞬で撮れることも"],
    "07_tech_monitor_check_no_text.png": ["動いても", "すぐ確認します"],
    "08_parent_relieved_no_text.png": ["気まずく思わなくて", "大丈夫"],
    "09_parent_child_reassured_no_text.png": ["お子さんも保護者も", "悪くありません"],
    "10_tech_child_pace_no_text.png": ["ペースに合わせて", "進めます"],
    "11_save_cta_background_no_text.png": ["【保存】", "いざという時に"],
    "12_follow_end_no_text.png": ["診療放射線技師の発信", "フォローで応援"],
}


def fit_font(draw, lines, max_width, base_size):
    size = base_size
    while size >= 42:
        font = ImageFont.truetype(str(FONT_PATH), size)
        widths = [draw.textbbox((0, 0), line, font=font)[2] for line in lines]
        if max(widths) <= max_width:
            return font
        size -= 2
    return ImageFont.truetype(str(FONT_PATH), size)


def draw_telop(image, lines):
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    w, h = image.size

    margin_x = int(w * 0.075)
    max_box_w = int(w * 0.79)
    top_y = int(h * 0.105)
    pad_x = int(w * 0.045)
    pad_y = int(h * 0.020)

    font = fit_font(draw, lines, max_box_w - pad_x * 2, 66)
    bboxes = [draw.textbbox((0, 0), line, font=font) for line in lines]
    text_width = max(box[2] - box[0] for box in bboxes)
    line_heights = [box[3] - box[1] for box in bboxes]
    line_gap = int(font.size * 0.28)
    text_height = sum(line_heights) + line_gap * (len(lines) - 1)

    box_w = min(max_box_w, text_width + pad_x * 2)
    box_h = text_height + pad_y * 2
    x0 = margin_x
    y0 = top_y
    x1 = x0 + box_w
    y1 = y0 + box_h

    draw.rounded_rectangle((x0, y0, x1, y1), radius=BOX_RADIUS, fill=BOX_COLOR)

    y = y0 + pad_y
    for line, box, line_h in zip(lines, bboxes, line_heights):
        line_w = box[2] - box[0]
        x = x0 + (box_w - line_w) / 2
        draw.text((x, y - box[1]), line, font=font, fill=TEXT_COLOR)
        y += line_h + line_gap

    return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")


def build_contact_sheet(files):
    thumb_w, thumb_h = 240, 426
    label_h = 34
    cols = 4
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (245, 245, 245))
    label_font = ImageFont.load_default()

    for idx, file_path in enumerate(files):
        image = Image.open(file_path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h))
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), "white")
        tile.paste(image, ((thumb_w - image.width) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 10), file_path.name[:32], fill=(20, 20, 20), font=label_font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))

    out = SERIES / "contact_sheet_telop_frames.png"
    sheet.save(out)
    return out


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    for index, input_path in enumerate(sorted(INPUT_DIR.glob("*.png")), start=1):
        lines = TELOPS[input_path.name]
        image = Image.open(input_path)
        out = OUTPUT_DIR / f"{index:02d}_telop.png"
        draw_telop(image, lines).save(out, quality=95)
        outputs.append(out)

    contact_sheet = build_contact_sheet(outputs)
    print(f"wrote {len(outputs)} telop frames")
    print(contact_sheet)
    for out in outputs:
        print(out)


if __name__ == "__main__":
    main()
