from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
BASE = ROOT / "reel_assets" / "angle_adjustment_images_20260818"
OUT = ROOT / "reel_assets" / "angle_adjustment_telop_frames_20260818"
CONTACT = OUT / "contact_sheet_20260818_telop_frames.jpg"
TEXTS = OUT / "telop_texts_20260818.txt"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (16, 36, 55, 255)
ACCENT = (0, 104, 150, 255)
WHITE = (255, 255, 255, 240)
SHADOW = (0, 0, 0, 38)


CUTS = [
    (
        "image_01_patient_angle_anxiety.png",
        "telop_01_patient_angle_anxiety.png",
        [["角度を変えて撮影します"], ["と言われて", "不安", "に"]],
        {"不安"},
        830,
    ),
    (
        "image_02_rt_adjusting_angle_revised.png",
        "telop_02_rt_adjusting_angle.png",
        [["角度", "や", "条件", "を"], ["整えることがあります"]],
        {"角度", "条件"},
        830,
    ),
    (
        "image_03_patient_awkward_feeling.png",
        "telop_03_patient_awkward_feeling.png",
        [["自分のせいかな"], ["と思うことも"]],
        {"自分のせい"},
        830,
    ),
    (
        "image_04_rt_reassures_patient.png",
        "telop_04_rt_reassures_patient.png",
        [["その気持ち"], ["おかしくありません"]],
        {"おかしくありません"},
        830,
    ),
    (
        "image_05_individual_positioning.png",
        "telop_05_individual_positioning.png",
        [["体の向き", "に合わせて"], ["微調整", "します"]],
        {"微調整"},
        830,
    ),
    (
        "image_06_rt_control_room_xray_room_revised2.png",
        "telop_06_rt_control_room_xray_room.png",
        [["必要な情報", "が"], ["写っているか確認"]],
        {"必要な情報", "確認"},
        250,
    ),
    (
        "image_07_patient_multiple_checks_uncertain.png",
        "telop_07_patient_multiple_checks_uncertain.png",
        [["何回か確認", "が入ると"], ["不安", "になることも"]],
        {"不安"},
        830,
    ),
    (
        "image_08_rt_detector_adjustment_revised.png",
        "telop_08_rt_detector_adjustment.png",
        [["調整", "は"], ["通常の工程", "です"]],
        {"調整", "通常の工程"},
        830,
    ),
    (
        "image_09_patient_asks_question.png",
        "telop_09_patient_asks_question.png",
        [["気になることは"], ["伝えて", "大丈夫"]],
        {"伝えて", "大丈夫"},
        250,
    ),
    (
        "image_10_save_cta_patient_phone.png",
        "telop_10_save_cta_patient_phone.png",
        [["検査前", "に見返せるよう"], ["保存"]],
        {"検査前", "保存"},
        520,
    ),
    (
        "image_11_follow_cta_rt_closing.png",
        "telop_11_follow_cta_rt_closing.png",
        [["検査の不安", "を"], ["フォロー", "で確認"]],
        {"検査の不安", "フォロー"},
        520,
    ),
]


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size)


def cover(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    w, h = size
    scale = max(w / img.width, h / img.height)
    resized = img.resize((int(img.width * scale), int(img.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - w) // 2
    top = (resized.height - h) // 2
    return resized.crop((left, top, left + w, top + h))


def segment_width(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def layout_width(draw: ImageDraw.ImageDraw, line: list[str], fnt: ImageFont.FreeTypeFont) -> int:
    gap = int(fnt.size * 0.08)
    return sum(segment_width(draw, part, fnt) for part in line) + gap * (len(line) - 1)


def fit_size(draw: ImageDraw.ImageDraw, lines: list[list[str]], max_w: int, start: int = 66) -> int:
    size = start
    while size >= 38:
        fnt = font(size)
        if max(layout_width(draw, line, fnt) for line in lines) <= max_w:
            return size
        size -= 2
    return 38


def draw_centered_segments(
    draw: ImageDraw.ImageDraw,
    y: int,
    line: list[str],
    fnt: ImageFont.FreeTypeFont,
    highlights: set[str],
) -> None:
    gap = int(fnt.size * 0.08)
    total_w = layout_width(draw, line, fnt)
    x = (W - total_w) // 2
    for part in line:
        fill = ACCENT if part in highlights else NAVY
        draw.text((x, y), part, font=fnt, fill=fill, anchor="la")
        x += segment_width(draw, part, fnt) + gap


def add_telop(img: Image.Image, lines: list[list[str]], highlights: set[str], box_y1: int) -> Image.Image:
    img = cover(img.convert("RGB"), (W, H)).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    size = fit_size(draw, lines, 790)
    fnt = font(size)
    line_h = int(size * 1.18)
    text_h = line_h * len(lines)
    pad_x, pad_y = 58, 42
    box_w = min(910, max(layout_width(draw, line, fnt) for line in lines) + pad_x * 2)
    box_h = text_h + pad_y * 2
    box_x1 = (W - box_w) // 2
    box_x2 = box_x1 + box_w
    box_y2 = box_y1 + box_h

    draw.rounded_rectangle(
        (box_x1 + 5, box_y1 + 7, box_x2 + 5, box_y2 + 7),
        radius=30,
        fill=SHADOW,
    )
    draw.rounded_rectangle((box_x1, box_y1, box_x2, box_y2), radius=30, fill=WHITE)

    first_y = box_y1 + pad_y + int(size * 0.12)
    for i, line in enumerate(lines):
        draw_centered_segments(draw, first_y + i * line_h, line, fnt, highlights)

    img.alpha_composite(overlay)
    return img.convert("RGB")


def make_contact_sheet(paths: list[Path]) -> None:
    cols, rows = 3, 4
    tw, th = 240, 426
    label_h = 34
    board = Image.new("RGB", (tw * cols, (th + label_h) * rows), (245, 245, 245))
    label_font = ImageFont.load_default()
    draw = ImageDraw.Draw(board)
    for i, path in enumerate(paths):
        thumb = cover(Image.open(path).convert("RGB"), (tw, th))
        x = (i % cols) * tw
        y = (i // cols) * (th + label_h)
        board.paste(thumb, (x, y))
        draw.text((x + 8, y + th + 8), path.stem[:28], fill=(0, 0, 0), font=label_font)
    board.save(CONTACT, quality=92)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    out_paths: list[Path] = []
    text_lines: list[str] = []
    for i, (src_name, out_name, lines, highlights, y) in enumerate(CUTS, start=1):
        out_path = OUT / out_name
        add_telop(Image.open(BASE / src_name), lines, highlights, y).save(out_path, quality=95)
        out_paths.append(out_path)
        text_lines.append(f"{i:02d}. " + " / ".join("".join(line) for line in lines))

    make_contact_sheet(out_paths)
    TEXTS.write_text("\n".join(text_lines) + "\n", encoding="utf-8-sig")
    print(f"created {len(out_paths)} telop frames")
    print(OUT)
    print(CONTACT)


if __name__ == "__main__":
    main()
