from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "pediatric_radiation_safety_series"
FRAME_DIR = ASSET_DIR / "frames" / "pre_exam_explain_child"
OUT_DIR = ASSET_DIR / "telop_frames" / "pre_exam_explain_child"
FONT = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

NAVY = (7, 22, 43, 255)
WHITE = (255, 255, 255, 255)


ITEMS = [
    ("frame01_parent_worried.png", "01_telop.png", ["検査前の説明", "どうすれば？"]),
    ("frame02_rt_explains.png", "02_telop.png", ["難しい言葉は", "いりません"]),
    ("frame03_parent_simple_words.png", "03_telop.png", ["「痛くないよ」より", "「すぐ終わるよ」"]),
    ("frame04_still_practice.png", "04_telop.png", ["「じっとできるかな？」", "遊びのように"]),
    ("frame05_rt_calm_note.png", "05_telop.png", ["説明しすぎると", "不安が伝わることも"]),
    ("frame06_child_calm.png", "06_telop.png", ["シンプルな言葉で", "安心しやすく"]),
    ("frame07_rt_parent_consult.png", "07_telop.png", ["当日でも相談OK", "診療放射線技師へ"], 0.40, 0.80),
    ("frame08_parent_relief.png", "08_telop.png", ["うまく説明できなくても", "大丈夫"]),
    ("frame09_parent_child_support.png", "09_telop.png", ["そばにいることも", "大切です"]),
    ("frame10_rt_closing.png", "10_telop.png", ["お子さんのペースで", "進めましょう"]),
    (ASSET_DIR / "frames" / "11_smartphone_save.png", "11_telop.png", ["【保存】", "検査前に見返せる"], 0.40, 0.80),
    (ASSET_DIR / "frames" / "12_rt_bow_follow.png", "12_telop.png", ["診療放射線技師の発信", "フォローで応援お願いします"]),
]

CLEANUP_REGIONS = {"11_telop.png": True}


def text_bbox(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont):
    return draw.textbbox((0, 0), text, font=font)


def fit_font(draw: ImageDraw.ImageDraw, lines: list[str], max_width: int) -> ImageFont.FreeTypeFont:
    size = 72
    while size >= 44:
        font = ImageFont.truetype(str(FONT), size)
        widest = max(text_bbox(draw, line, font)[2] for line in lines)
        if widest <= max_width:
            return font
        size -= 2
    return ImageFont.truetype(str(FONT), 44)


def draw_telop(
    image: Image.Image,
    lines: list[str],
    y_factor: float = 0.125,
    box_width_factor: float | None = None,
) -> Image.Image:
    canvas = image.convert("RGBA")
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    w, h = canvas.size

    side_margin = int(w * 0.09)
    max_text_width = w - side_margin * 2 - 120
    font = fit_font(draw, lines, max_text_width)

    line_boxes = [text_bbox(draw, line, font) for line in lines]
    line_heights = [box[3] - box[1] for box in line_boxes]
    line_gap = int(font.size * 0.22)
    text_w = max(box[2] - box[0] for box in line_boxes)
    text_h = sum(line_heights) + line_gap * (len(lines) - 1)

    pad_x = 56
    pad_y = 34
    box_w = min(w - side_margin * 2, text_w + pad_x * 2)
    if box_width_factor is not None:
        box_w = max(box_w, int(w * box_width_factor))
    box_h = text_h + pad_y * 2
    x0 = (w - box_w) // 2
    y0 = int(h * y_factor)
    x1 = x0 + box_w
    y1 = y0 + box_h

    if box_width_factor is not None and box_width_factor >= 1.0:
        x0 = -120
        x1 = w + 120

    draw.rounded_rectangle((x0, y0, x1, y1), radius=30, fill=WHITE)

    y = y0 + pad_y
    for line, box, line_h in zip(lines, line_boxes, line_heights):
        line_w = box[2] - box[0]
        x = (w - line_w) // 2
        draw.text((x, y - box[1]), line, font=font, fill=NAVY)
        y += line_h + line_gap

    return Image.alpha_composite(canvas, overlay).convert("RGB")


def remove_old_board(image: Image.Image, out_name: str) -> Image.Image:
    cleaned = image.convert("RGB")
    if not CLEANUP_REGIONS.get(out_name):
        return cleaned

    w, _ = cleaned.size
    cleanup_h = 690
    top = (238, 226, 216)
    bottom = (232, 222, 209)
    patch = Image.new("RGB", (w, cleanup_h), top)
    patch_draw = ImageDraw.Draw(patch)
    for y in range(cleanup_h):
        t = y / max(1, cleanup_h - 1)
        color = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        patch_draw.line((0, y, w, y), fill=color)
    patch = patch.filter(ImageFilter.GaussianBlur(radius=12))
    cleaned.paste(patch, (0, 0))
    return cleaned


def make_contact_sheet(paths: list[Path]) -> None:
    thumbs = []
    for path in paths:
        img = Image.open(path).convert("RGB")
        img.thumbnail((260, 462), Image.LANCZOS)
        thumbs.append((path.name, img.copy()))

    cols = 4
    rows = 3
    cell_w = 300
    cell_h = 520
    sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), "white")
    draw = ImageDraw.Draw(sheet)
    label_font = ImageFont.truetype(str(FONT), 18)

    for i, (name, img) in enumerate(thumbs):
        col = i % cols
        row = i // cols
        x = col * cell_w + (cell_w - img.width) // 2
        y = row * cell_h + 20
        sheet.paste(img, (x, y))
        draw.text((col * cell_w + 18, y + img.height + 10), name, fill=(0, 0, 0), font=label_font)

    sheet.save(OUT_DIR / "contact_sheet_telop.jpg", quality=92)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_paths = []
    for item in ITEMS:
        src, out_name, lines = item[:3]
        y_factor = item[3] if len(item) > 3 else 0.125
        box_width_factor = item[4] if len(item) > 4 else None
        src_path = src if isinstance(src, Path) else FRAME_DIR / src
        if not src_path.exists():
            raise FileNotFoundError(src_path)
        image = remove_old_board(Image.open(src_path), out_name)
        out = draw_telop(image, lines, y_factor, box_width_factor)
        out_path = OUT_DIR / out_name
        out.save(out_path, quality=95)
        out_paths.append(out_path)
    make_contact_sheet(out_paths)
    for path in out_paths:
        print(path)
    print(OUT_DIR / "contact_sheet_telop.jpg")


if __name__ == "__main__":
    main()
