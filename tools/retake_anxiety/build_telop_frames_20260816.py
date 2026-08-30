from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
BASE = ROOT / "reel_assets" / "retake_anxiety_images_20260816"
OUT = ROOT / "reel_assets" / "retake_anxiety_telop_frames_20260816"
CONTACT = OUT / "contact_sheet_20260816_telop_frames.jpg"
TEXTS = OUT / "telop_texts_20260816.txt"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (16, 36, 55, 255)
ACCENT = (0, 104, 150, 255)
WHITE = (255, 255, 255, 238)
SHADOW = (0, 0, 0, 38)


CUTS = [
    (
        "image_01_patient_retake_anxiety.png",
        "telop_01_patient_retake_anxiety.png",
        [["「もう一回」で"], ["ドキッ", "としたら"]],
        {"ドキッ"},
        1180,
    ),
    (
        "image_02_patient_worry_grows.png",
        "telop_02_patient_worry_grows.png",
        [["悪いもの", "が"], ["写ったのかな"]],
        {"悪いもの"},
        1180,
    ),
    (
        "image_03_patient_feeling_accepted.png",
        "telop_03_patient_feeling_accepted.png",
        [["その気持ち"], ["自然", "です"]],
        {"自然"},
        220,
    ),
    (
        "image_04_xray_room_routine_process.png",
        "telop_04_xray_room_routine_process.png",
        [["悪い結果", "とは"], ["限りません"]],
        {"悪い結果", "限りません"},
        1180,
    ),
    (
        "image_05_rt_adjusting_xray_angle_v2.png",
        "telop_05_rt_adjusting_xray_angle.png",
        [["角度", "や", "条件", "を"], ["整えることも"]],
        {"角度", "条件"},
        1180,
    ),
    (
        "image_06_control_monitor_confirmation.png",
        "telop_06_control_monitor_confirmation.png",
        [["必要な情報", "を"], ["揃える", "確認", "です"]],
        {"必要な情報", "確認"},
        220,
    ),
    (
        "image_07_patient_wonders_failed_shot.png",
        "telop_07_patient_wonders_failed_shot.png",
        [["失敗", "だったのかな"], ["と思うことも"]],
        {"失敗"},
        1180,
    ),
    (
        "image_08_rt_reassuring_explanation.png",
        "telop_08_rt_reassuring_explanation.png",
        [["でも"], ["失敗", "とは限りません"]],
        {"失敗", "限りません"},
        1180,
    ),
    (
        "image_09_rt_explains_to_patient.png",
        "telop_09_rt_explains_to_patient.png",
        [["理由", "は"], ["さまざま", "です"]],
        {"理由", "さまざま"},
        1180,
    ),
    (
        "image_10_patient_asks_rt.png",
        "telop_10_patient_asks_rt.png",
        [["気になることは"], ["聞いて", "大丈夫"]],
        {"聞いて", "大丈夫"},
        1180,
    ),
    (
        "image_11_save_cta_patient_phone.png",
        "telop_11_save_cta_patient_phone.png",
        [["検査前", "に"], ["見返せるよう", "保存"]],
        {"検査前", "保存"},
        1180,
    ),
    (
        "image_12_follow_cta_rt_closing.png",
        "telop_12_follow_cta_rt_closing.png",
        [["不安な場面", "を"], ["フォロー", "で確認"]],
        {"不安な場面", "フォロー"},
        1180,
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
