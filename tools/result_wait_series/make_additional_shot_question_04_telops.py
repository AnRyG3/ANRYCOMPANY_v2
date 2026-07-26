from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
BASE = ROOT / "reel_assets" / "result_wait_series" / "additional_shot_question_04"
OUT = BASE / "02_telop"
STORYBOARD = BASE / "storyboard_telop.png"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (16, 36, 55, 255)
ACCENT = (204, 93, 47, 255)
WHITE = (255, 255, 255, 235)
SHADOW = (0, 0, 0, 45)

TELOP_Y = {
    "frame_01_opening.png": 760,
    "frame_05_exam_table.png": 800,
    "frame_10_save_cta_bg.png": 800,
    "frame_11_follow_cta_bg.png": 640,
}


CUTS = [
    (
        "frame_01_opening.png",
        "frame_01_opening_telop.png",
        [["「もう一枚」", "って言われると"], ["少し", "不安", "になる"]],
        {"「もう一枚」", "不安"},
    ),
    (
        "frame_02_monitor_glance.png",
        "frame_02_monitor_glance_telop.png",
        [["悪いもの？", "と"], ["気になる", "ことも"]],
        {"悪いもの？", "気になる"},
    ),
    (
        "frame_03_reassurance.png",
        "frame_03_reassurance_telop.png",
        [["その気持ち、"], ["おかしくありません"]],
        {"おかしくありません"},
    ),
    (
        "frame_04_image_check.png",
        "frame_04_image_check_telop.png",
        [["写り方", "や", "向き", "を"], ["確認することがあります"]],
        {"写り方", "向き"},
    ),
    (
        "frame_05_exam_table.png",
        "frame_05_exam_table_telop.png",
        [["少しのズレ", "でも"], ["確認することがあります"]],
        {"少しのズレ"},
    ),
    (
        "frame_06_role_explanation.png",
        "frame_06_role_explanation_telop.png",
        [["画像の診断は"], ["医師が行います"]],
        {"医師"},
    ),
    (
        "frame_07_routine_operation.png",
        "frame_07_routine_operation_telop.png",
        [["追加撮影", "は"], ["珍しいことではありません"]],
        {"追加撮影"},
    ),
    (
        "frame_08_after_exam_concern.png",
        "frame_08_after_exam_concern_telop.png",
        [["気になってしまうのは"], ["自然なことです"]],
        {"自然"},
    ),
    (
        "frame_09_ask_staff.png",
        "frame_09_ask_staff_telop.png",
        [["検査の流れ", "は"], ["聞いて大丈夫"]],
        {"検査の流れ", "大丈夫"},
    ),
    (
        "frame_10_save_cta_bg.png",
        "frame_10_save_cta_bg_telop.png",
        [["不安なとき", "のために"], ["保存", "しておいてください"]],
        {"不安なとき", "保存"},
    ),
    (
        "frame_11_follow_cta_bg.png",
        "frame_11_follow_cta_bg_telop.png",
        [["検査のこと"], ["一緒に考えていきます"]],
        {"一緒に"},
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


def add_telop(img: Image.Image, lines: list[list[str]], highlights: set[str], box_y1: int = 188) -> Image.Image:
    img = cover(img.convert("RGB"), (W, H)).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    size = fit_size(draw, lines, 760)
    fnt = font(size)
    line_h = int(size * 1.18)
    text_h = line_h * len(lines)
    pad_x, pad_y = 60, 42
    box_w = min(900, max(layout_width(draw, line, fnt) for line in lines) + pad_x * 2)
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


def make_storyboard(paths: list[Path]) -> None:
    cols, rows = 4, 3
    tw, th = 216, 384
    board = Image.new("RGB", (tw * cols, th * rows), "white")
    for i, path in enumerate(paths):
        thumb = cover(Image.open(path).convert("RGB"), (tw, th))
        board.paste(thumb, ((i % cols) * tw, (i // cols) * th))
    board.save(STORYBOARD, quality=94)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    out_paths = []
    for src_name, out_name, lines, highlights in CUTS:
        img = Image.open(BASE / src_name)
        out_path = OUT / out_name
        add_telop(img, lines, highlights, TELOP_Y.get(src_name, 188)).save(out_path, quality=95)
        out_paths.append(out_path)
    make_storyboard(out_paths)
    (BASE / "telop_texts.txt").write_text(
        "\n".join(
            f"{i:02d}. " + " / ".join("".join(line) for line in lines)
            for i, (_, _, lines, _) in enumerate(CUTS, start=1)
        )
        + "\n",
        encoding="utf-8-sig",
    )
    print(OUT)
    print(STORYBOARD)


if __name__ == "__main__":
    main()
