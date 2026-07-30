from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
SRC = ROOT / "reel_assets" / "fall_mild_pain_xray_20260730" / "sample_frames"
OUT = ROOT / "reel_assets" / "fall_mild_pain_xray_20260730" / "telop_frames"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

NAVY = (22, 42, 76, 255)
ACCENT = (0, 104, 150, 255)
BOX = (255, 255, 255, 232)


FRAMES = [
    ("sample_01_home_after_fall.png", "telop_01_home_after_fall.png", [[("痛みが軽い", True), ("なら", False)], [("検査", True), ("はいらない？", False)]], None),
    ("sample_02_xray_explanation.png", "telop_02_xray_explanation.png", [[("病院に行くほど？", False)], [("迷うことも", True), ("あります", False)]], None),
    ("frame_03_reassurance.png", "telop_03_reassurance.png", [[("その気持ち", True)], [("おかしくありません", False)]], None),
    ("frame_04_xray_review_hands.png", "telop_04_xray_review_hands.png", [[("骨に異常", True), ("があっても", False)], [("痛みが軽い", True), ("ことがあります", False)]], None),
    ("frame_05_xray_room.png", "telop_05_xray_room.png", [[("痛みの感じ方", True), ("には", False)], [("個人差", True), ("があります", False)]], None),
    ("frame_06_rt_explains_monitor.png", "telop_06_rt_explains_monitor.png", [[("痛みの強さ", True), ("だけでは", False)], [("わからないことも", False)]], 0.155),
    ("frame_07_exam_table_guidance.png", "telop_07_exam_table_guidance.png", [[("転んだ後", True), ("は", False)], [("一度確認", True), ("を", False)]], None),
    ("frame_08_hesitation_corridor.png", "telop_08_hesitation_corridor.png", [[("大げさにしたくない", True)], [("そう思うことも", False)]], None),
    ("frame_09_reassuring_closing.png", "telop_09_reassuring_closing.png", [[("早めの確認", True), ("が", False)], [("安心", True), ("につながります", False)]], None),
    ("frame_10_save_cta_bg.png", "telop_10_save_cta_bg.png", [[("不安なとき", False), ("に", False)], [("見返せるよう", False), ("保存", True)]], None),
    ("frame_11_follow_cta_bg.png", "telop_11_follow_cta_bg.png", [[("検査のこと", True)], [("一緒に考えていきます", False)]], None),
]


def text_size(draw, text, font):
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def fit_font(draw, lines, max_width, start_size):
    size = start_size
    while size >= 34:
        font = ImageFont.truetype(str(FONT_PATH), size)
        max_line = 0
        for line in lines:
            width = sum(text_size(draw, run, font)[0] for run, _ in line)
            max_line = max(max_line, width)
        if max_line <= max_width:
            return font
        size -= 2
    return ImageFont.truetype(str(FONT_PATH), size)


def draw_telop(src_name, out_name, lines, y_ratio=None):
    image = Image.open(SRC / src_name).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    w, h = image.size
    margin_x = int(w * 0.075)
    max_width = int(w * 0.78)
    font = fit_font(draw, lines, max_width, int(w * 0.064))
    line_gap = int(w * 0.025)
    pad_x = int(w * 0.045)
    pad_y = int(w * 0.03)
    radius = int(w * 0.025)

    line_sizes = []
    for line in lines:
        line_w = sum(text_size(draw, run, font)[0] for run, _ in line)
        line_h = max(text_size(draw, run, font)[1] for run, _ in line)
        line_sizes.append((line_w, line_h))

    box_w = min(max(line_w for line_w, _ in line_sizes) + pad_x * 2, w - margin_x * 2)
    text_h = sum(line_h for _, line_h in line_sizes) + line_gap * (len(lines) - 1)
    box_h = text_h + pad_y * 2
    x0 = (w - box_w) // 2
    y0 = int(h * y_ratio) if y_ratio is not None else (h - box_h) // 2
    x1 = x0 + box_w
    y1 = y0 + box_h

    draw.rounded_rectangle((x0, y0, x1, y1), radius=radius, fill=BOX)

    y = y0 + pad_y
    for line, (line_w, line_h) in zip(lines, line_sizes):
        x = x0 + (box_w - line_w) // 2
        for run, emph in line:
            draw.text((x, y), run, font=font, fill=ACCENT if emph else NAVY)
            x += text_size(draw, run, font)[0]
        y += line_h + line_gap

    OUT.mkdir(parents=True, exist_ok=True)
    Image.alpha_composite(image, overlay).convert("RGB").save(OUT / out_name, quality=95)


def main():
    for src_name, out_name, lines, y_ratio in FRAMES:
        draw_telop(src_name, out_name, lines, y_ratio)


if __name__ == "__main__":
    main()

