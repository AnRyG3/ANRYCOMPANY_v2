from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
BASE = ROOT / "reel_assets" / "xray_no_abnormality_pain_images"
OUT = ROOT / "reel_assets" / "xray_no_abnormality_pain_telop_frames"
CONTACT = OUT / "contact_sheet_telop_frames.jpg"
TEXTS = OUT / "telop_texts.txt"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (16, 36, 55, 255)
ACCENT = (0, 104, 150, 255)
WHITE = (255, 255, 255, 235)
SHADOW = (0, 0, 0, 40)


CUTS = [
    (
        "image_01_patient_waiting_area_review.png",
        "telop_01_patient_waiting_area_review.png",
        [["「異常なし」", "なのに"], ["まだ", "痛い"]],
        {"「異常なし」", "痛い"},
        210,
    ),
    (
        "image_02_patient_confused_hallway.png",
        "telop_02_patient_confused_hallway.png",
        [["何も写らない", "のに"], ["痛みが続く"]],
        {"痛みが続く"},
        210,
    ),
    (
        "image_03_rt_reassuring_consultation.png",
        "telop_03_rt_reassuring_consultation.png",
        [["その気持ち"], ["おかしくありません"]],
        {"おかしくありません"},
        210,
    ),
    (
        "image_04_patient_pain_can_continue.png",
        "telop_04_patient_pain_can_continue.png",
        [["写らなくても"], ["痛むことがあります"]],
        {"痛むこと"},
        210,
    ),
    (
        "image_05_xray_bone_review_monitor_only.png",
        "telop_05_xray_bone_review_monitor_only.png",
        [["レントゲン", "は"], ["骨を見る手がかり"]],
        {"レントゲン", "骨"},
        None,
    ),
    (
        "image_06_rt_result_meaning_review_room.png",
        "telop_06_rt_result_meaning_review_room.png",
        [["「異常なし」", "は"], ["痛みなし", "ではありません"]],
        {"「異常なし」", "痛みなし"},
        210,
    ),
    (
        "image_07_patient_not_convinced.png",
        "telop_07_patient_not_convinced.png",
        [["この痛みは何？"], ["そう感じることも"]],
        {"この痛みは何？"},
        210,
    ),
    (
        "image_08_rt_multiple_pain_factors.png",
        "telop_08_rt_multiple_pain_factors.png",
        [["原因は"], ["ひとつとは限りません"]],
        {"原因"},
        210,
    ),
    (
        "image_09_patient_tells_rt.png",
        "telop_09_patient_tells_rt.png",
        [["続く痛み", "は"], ["そのまま伝えて大丈夫"]],
        {"続く痛み"},
        210,
    ),
    (
        "image_10_save_cta_phone.png",
        "telop_10_save_cta_phone.png",
        [["不安な時", "に"], ["見返せるよう", "保存"]],
        {"不安な時", "保存"},
        None,
    ),
    (
        "image_11_follow_cta_rt_closing.png",
        "telop_11_follow_cta_rt_closing.png",
        [["検査の不安", "を"], ["やさしく解説します"]],
        {"検査の不安"},
        210,
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


def fit_size(draw: ImageDraw.ImageDraw, lines: list[list[str]], max_w: int, start: int = 70) -> int:
    size = start
    while size >= 40:
        fnt = font(size)
        if max(layout_width(draw, line, fnt) for line in lines) <= max_w:
            return size
        size -= 2
    return 40


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


def add_telop(img: Image.Image, lines: list[list[str]], highlights: set[str], box_y1: int | None) -> Image.Image:
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
    if box_y1 is None:
        box_y1 = (H - box_h) // 2
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
