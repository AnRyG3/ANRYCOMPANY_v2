from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
BASE = ROOT / "reel_assets" / "xray_after_ct_addition_failure_question"
SRC = BASE / "frames_no_text"
OUT = BASE / "telop_frames"
CONTACT = BASE / "contact_sheet_telop_frames.jpg"
TEXTS = BASE / "telop_texts.txt"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (16, 36, 55, 255)
ACCENT = (204, 93, 47, 255)
WHITE = (255, 255, 255, 235)
SHADOW = (0, 0, 0, 45)


CUTS = [
    (
        "frame_01_waiting_explanation.png",
        "frame_01_waiting_explanation_telop.png",
        [["レントゲンのあと", "CT？"], ["失敗", "だったの？"]],
        {"CT", "失敗"},
        210,
    ),
    (
        "frame_02_patient_concern.png",
        "frame_02_patient_concern_telop.png",
        [["そう感じても"], ["おかしくありません"]],
        {"おかしくありません"},
        230,
    ),
    (
        "frame_03_rt_reassurance.png",
        "frame_03_rt_reassurance_telop.png",
        [["CT追加", "は"], ["失敗", "の意味ではありません"]],
        {"CT追加", "失敗"},
        220,
    ),
    (
        "frame_04_xray_room.png",
        "frame_04_xray_room_telop.png",
        [["レントゲン", "で"], ["全体を確認"]],
        {"レントゲン"},
        780,
    ),
    (
        "frame_05_ct_room_explanation.png",
        "frame_05_ct_room_explanation_telop.png",
        [["CT", "で"], ["詳しく確認"]],
        {"CT", "詳しく"},
        220,
    ),
    (
        "frame_06_bone_images_monitor.png",
        "frame_06_bone_images_monitor_telop.png",
        [["骨の重なり", "は"], ["分かりにくいことも"]],
        {"骨の重なり"},
        360,
    ),
    (
        "frame_07_roles_explanation.png",
        "frame_07_roles_explanation_telop.png",
        [["検査には"], ["それぞれ役割があります"]],
        {"役割"},
        760,
    ),
    (
        "frame_08_doctor_decision_bone.png",
        "frame_08_doctor_decision_bone_telop.png",
        [["必要性", "は"], ["医師が判断します"]],
        {"必要性", "医師"},
        220,
    ),
    (
        "frame_09_patient_relieved.png",
        "frame_09_patient_relieved_telop.png",
        [["最初の検査も"], ["無駄ではありません"]],
        {"無駄ではありません"},
        390,
    ),
    (
        "frame_10_save_cta_bg.png",
        "frame_10_save_cta_bg_telop.png",
        [["不安な時", "のために"], ["保存", "しておいてください"]],
        {"不安な時", "保存"},
        760,
    ),
    (
        "frame_11_follow_cta_bg.png",
        "frame_11_follow_cta_bg_telop.png",
        [["検査の不安を"], ["一緒に減らしましょう"]],
        {"不安", "一緒に"},
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


def fit_size(draw: ImageDraw.ImageDraw, lines: list[list[str]], max_w: int, start: int = 68) -> int:
    size = start
    while size >= 42:
        fnt = font(size)
        if max(layout_width(draw, line, fnt) for line in lines) <= max_w:
            return size
        size -= 2
    return 42


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
    for i, path in enumerate(paths):
        thumb = cover(Image.open(path).convert("RGB"), (tw, th))
        x = (i % cols) * tw
        y = (i // cols) * (th + label_h)
        board.paste(thumb, (x, y))
        draw = ImageDraw.Draw(board)
        draw.text((x + 8, y + th + 8), path.stem[:28], fill=(0, 0, 0))
    board.save(CONTACT, quality=92)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    out_paths: list[Path] = []
    text_lines: list[str] = []
    for i, (src_name, out_name, lines, highlights, y) in enumerate(CUTS, start=1):
        out_path = OUT / out_name
        add_telop(Image.open(SRC / src_name), lines, highlights, y).save(out_path, quality=95)
        out_paths.append(out_path)
        text_lines.append(f"{i:02d}. " + " / ".join("".join(line) for line in lines))

    make_contact_sheet(out_paths)
    TEXTS.write_text("\n".join(text_lines) + "\n", encoding="utf-8-sig")
    print(f"created {len(out_paths)} telop frames")
    print(OUT)
    print(CONTACT)


if __name__ == "__main__":
    main()
