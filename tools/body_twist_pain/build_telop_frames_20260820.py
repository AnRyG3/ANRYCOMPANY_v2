from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
BASE = ROOT / "reel_assets" / "body_twist_pain_images_20260820"
OUT = ROOT / "reel_assets" / "body_twist_pain_telop_frames_20260820"
CONTACT = OUT / "contact_sheet_20260820_telop_frames.jpg"
TEXTS = OUT / "telop_texts_20260820.txt"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (16, 36, 55, 255)
ACCENT = (0, 104, 150, 255)
WHITE = (255, 255, 255, 240)
SHADOW = (0, 0, 0, 38)
BOARD_CENTER_Y = H // 2


CUTS = [
    (
        "image_01_20260820_patient_instruction_moment.png",
        "telop_01_patient_instruction_moment.png",
        [["体をひねる時"], ["痛み", "があるなら"]],
        {"痛み"},
    ),
    (
        "image_02_20260820_patient_twist_limit.png",
        "telop_02_patient_twist_limit.png",
        [["途中まででも"], ["大丈夫"]],
        {"大丈夫"},
    ),
    (
        "image_03_20260820_patient_feeling_accepted.png",
        "telop_03_patient_feeling_accepted.png",
        [["迷う気持ちも"], ["自然", "です"]],
        {"自然"},
    ),
    (
        "image_04_20260820_patient_stops_within_range.png",
        "telop_04_patient_stops_within_range.png",
        [["動ける範囲", "で"], ["止めてください"]],
        {"動ける範囲"},
    ),
    (
        "image_05_20260820_patient_tells_limit.png",
        "telop_05_patient_tells_limit.png",
        [["ここまでです"], ["と", "伝えて", "OK"]],
        {"伝えて"},
    ),
    (
        "image_06_20260820_rt_checks_positioning.png",
        "telop_06_rt_checks_positioning.png",
        [["姿勢を", "確認", "しながら"], ["進めます"]],
        {"確認"},
    ),
    (
        "image_07_20260820_patient_relieved_after_telling.png",
        "telop_07_patient_relieved_after_telling.png",
        [["伝えることは"], ["大事な情報"]],
        {"大事な情報"},
    ),
    (
        "image_08_20260820_patient_raises_hand_pain.png",
        "telop_08_patient_raises_hand_pain.png",
        [["痛み", "が強い時は"], ["その場で", "伝えて"]],
        {"痛み", "伝えて"},
    ),
    (
        "image_09_20260820_save_cta_phone.png",
        "telop_09_save_cta_phone.png",
        [["検査前", "に見返せるよう"], ["保存"]],
        {"検査前", "保存"},
    ),
    (
        "image_10_20260820_follow_cta_rt_closing.png",
        "telop_10_follow_cta_rt_closing.png",
        [["検査のリアルを"], ["フォロー", "で確認"]],
        {"フォロー"},
        430,
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


def add_telop(
    img: Image.Image,
    lines: list[list[str]],
    highlights: set[str],
    center_y: int = BOARD_CENTER_Y,
) -> Image.Image:
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
    box_y1 = center_y - box_h // 2
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
    for i, cut in enumerate(CUTS, start=1):
        src_name, out_name, lines, highlights, *options = cut
        center_y = options[0] if options else BOARD_CENTER_Y
        out_path = OUT / out_name
        add_telop(Image.open(BASE / src_name), lines, highlights, center_y).save(out_path, quality=95)
        out_paths.append(out_path)
        text_lines.append(f"{i:02d}. " + " / ".join("".join(line) for line in lines))

    make_contact_sheet(out_paths)
    TEXTS.write_text("\n".join(text_lines) + "\n", encoding="utf-8-sig")
    print(f"created {len(out_paths)} telop frames")
    print(OUT)
    print(CONTACT)


if __name__ == "__main__":
    main()
