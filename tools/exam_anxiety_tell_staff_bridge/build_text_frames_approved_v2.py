from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "exam_anxiety_tell_staff_bridge"
INPUT_DIR = ASSET_DIR / "image_frames_approved_v2"
OUTPUT_DIR = ASSET_DIR / "text_frames_approved_v2"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

NAVY = (20, 42, 74, 255)
WHITE = (255, 255, 255, 232)

FRAMES = [
    ("frame01_patient_unwell_ct.png", "01_text_patient_unwell_ct.png", ["検査中に気分が悪い…", "言っていい？"], "top"),
    ("frame02_rt_tech_reassuring_distance.png", "02_text_rt_tech_reassuring_distance.png", ["我慢せず", "すぐ伝えてOK"], "bottom"),
    ("frame03_clean_exam_room_symptoms.png", "03_text_clean_exam_room_symptoms.png", ["めまい・冷や汗・吐き気も", "体調変化のサイン"], "center"),
    ("frame04_patient_hesitates.png", "04_text_patient_hesitates.png", ["迷惑かも…と", "我慢しなくて大丈夫"], "top"),
    ("frame05_rt_tech_monitor_attention.png", "05_text_rt_tech_monitor_attention.png", ["小さな変化こそ", "知りたいです"], "top"),
    ("frame06_contrast_iv_line_closeup.png", "06_text_contrast_iv_line_closeup.png", ["造影剤を使う検査や", "長時間同じ姿勢では"], "top"),
    ("frame07_patient_speaks_to_rt_no_gantry.png", "07_text_patient_speaks_to_rt_no_gantry.png", ["「気持ち悪いです」", "その一言で十分"], "top"),
    ("frame08_patient_resting.png", "08_text_patient_resting.png", ["必要なら", "一時中断して休めます"], "top"),
    ("frame09_rt_tech_reassuring_nod.png", "09_text_rt_tech_reassuring_nod.png", ["伝えても", "検査は失敗ではありません"], "top"),
    ("frame10_patient_leaves_relaxed.png", "10_text_patient_leaves_relaxed.png", ["我慢しないことが", "安心の一歩"], "top"),
    ("frame11_smartphone_save_cta.png", "11_text_smartphone_save_cta.png", ["あとで見返すなら", "保存"], "top"),
    ("frame12_rt_tech_bowing_cta.png", "12_text_rt_tech_bowing_cta.png", ["診療放射線技師の発信", "フォローで応援お願いします"], "top"),
]


def rounded_box(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], radius: int) -> None:
    draw.rounded_rectangle(xy, radius=radius, fill=WHITE)


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    return right - left, bottom - top


def fit_font(draw: ImageDraw.ImageDraw, lines: list[str], max_width: int) -> ImageFont.FreeTypeFont:
    for size in range(68, 42, -2):
        font = ImageFont.truetype(str(FONT_PATH), size)
        widest = max(text_size(draw, line, font)[0] for line in lines)
        if widest <= max_width:
            return font
    return ImageFont.truetype(str(FONT_PATH), 42)


def board_position(position: str, image_w: int, image_h: int, board_w: int, board_h: int) -> tuple[int, int]:
    x = (image_w - board_w) // 2
    if position == "bottom":
        y = image_h - board_h - 250
    elif position == "center":
        y = (image_h - board_h) // 2
    else:
        y = 205
    return x, y


def render_frame(src: Path, dst: Path, lines: list[str], position: str) -> None:
    image = Image.open(src).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    max_text_width = int(image.width * 0.76)
    font = fit_font(draw, lines, max_text_width)
    line_sizes = [text_size(draw, line, font) for line in lines]
    line_gap = 18
    pad_x = 54
    pad_y = 34
    text_w = max(width for width, _ in line_sizes)
    text_h = sum(height for _, height in line_sizes) + line_gap * (len(lines) - 1)
    board_w = min(image.width - 120, text_w + pad_x * 2)
    board_h = text_h + pad_y * 2 + 8
    x, y = board_position(position, image.width, image.height, board_w, board_h)

    rounded_box(draw, (x, y, x + board_w, y + board_h), 30)

    current_y = y + pad_y
    for line, (_, line_h) in zip(lines, line_sizes):
        line_w, _ = text_size(draw, line, font)
        draw.text((x + (board_w - line_w) // 2, current_y), line, font=font, fill=NAVY)
        current_y += line_h + line_gap

    Image.alpha_composite(image, overlay).convert("RGB").save(dst, quality=95)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not FONT_PATH.exists():
        raise FileNotFoundError(FONT_PATH)
    for src_name, dst_name, lines, position in FRAMES:
        src = INPUT_DIR / src_name
        dst = OUTPUT_DIR / dst_name
        if not src.exists():
            raise FileNotFoundError(src)
        render_frame(src, dst, lines, position)


if __name__ == "__main__":
    main()
