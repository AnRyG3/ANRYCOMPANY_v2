from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
SRC = ROOT / "reel_assets" / "companion_waiting_role_07_samples"
OUT = ROOT / "reel_assets" / "companion_waiting_role_07_telop"
FONT = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

NAVY = (22, 42, 67, 255)
WHITE = (255, 255, 255, 232)
MARKER = (255, 232, 153, 185)

FRAMES = [
    {
        "src": "frame01_companion_f40_waiting_v2_person.png",
        "out": "frame01_telop.png",
        "lines": ["待つだけで", "いいのかな"],
        "highlight": ["待つだけ"],
        "position": "top_center",
    },
    {
        "src": "frame04_hesitation_close_waiting.png",
        "out": "frame02_telop.png",
        "lines": ["役に立てていない", "気がすることも"],
        "highlight": ["役に立てていない"],
        "position": "center",
    },
    {
        "src": "frame05_reassuring_corridor.png",
        "out": "frame03_telop.png",
        "lines": ["その気持ち、", "おかしくありません"],
        "highlight": ["おかしくありません"],
        "position": "center",
    },
    {
        "src": "frame06_waiting_is_role.png",
        "out": "frame04_telop.png",
        "lines": ["外で待つことも", "大切な役割"],
        "highlight": ["大切な役割"],
        "position": "center",
    },
    {
        "src": "frame02_post_exam_waiting_sample.png",
        "out": "frame05_telop.png",
        "lines": ["検査後の変化に", "気づけることも"],
        "highlight": ["気づける"],
        "position": "center",
    },
    {
        "src": "frame07_companion_f40_staff_contact_v2_person.png",
        "out": "frame06_telop.png",
        "lines": ["近くにいるだけで", "助けになります"],
        "highlight": ["近くにいる"],
        "position": "top_center",
    },
    {
        "src": "frame08_taskless_but_meaningful.png",
        "out": "frame07_telop.png",
        "lines": ["手伝えなくても", "意味はあります"],
        "highlight": ["意味"],
        "position": "center",
    },
    {
        "src": "frame09_just_waiting_question.png",
        "out": "frame08_telop.png",
        "lines": ["ただ待つだけ？", "と思ったら"],
        "highlight": ["ただ待つだけ"],
        "position": "center",
    },
    {
        "src": "frame09_companion_f40_support_v2_person.png",
        "out": "frame09_telop.png",
        "lines": ["そばにいることが", "支えになります"],
        "highlight": ["支え"],
        "position": "top_center",
    },
    {
        "src": "frame10_save_cta_background.png",
        "out": "frame10_telop.png",
        "lines": ["付き添いで迷ったら", "保存して見返して"],
        "highlight": ["保存"],
        "position": "center",
    },
    {
        "src": "frame11_rt_tech_001_follow_cta_v2_person.png",
        "out": "frame11_telop.png",
        "lines": ["検査の不安を", "軽くする話をフォロー"],
        "highlight": ["フォロー"],
        "note": "RT_TECH_001 appears visually as the CTA subject.",
        "position": "center",
    },
]


def text_size(draw, text, font):
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def box_position(position, w, h, box_w, box_h, safe_x, safe_y):
    if position == "center":
        return int((w - box_w) / 2), int((h - box_h) / 2)
    if position == "top_center":
        return int((w - box_w) / 2), safe_y
    if position == "top_right":
        return int(w - safe_x - box_w), safe_y
    return safe_x, safe_y


def draw_telop(path_in, path_out, lines, highlights, position):
    img = Image.open(path_in).convert("RGBA")
    w, h = img.size
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_size = int(w * 0.065)
    font = ImageFont.truetype(str(FONT), font_size)
    line_gap = int(font_size * 0.34)
    pad_x = int(w * 0.055)
    pad_y = int(font_size * 0.48)
    safe_x = int(w * 0.07)
    safe_y = int(h * 0.145)

    sizes = [text_size(draw, line, font) for line in lines]
    text_w = max(s[0] for s in sizes)
    text_h = sum(s[1] for s in sizes) + line_gap * (len(lines) - 1)
    box_w = min(w - safe_x * 2, text_w + pad_x * 2)
    box_h = text_h + pad_y * 2
    x0, y0 = box_position(position, w, h, box_w, box_h, safe_x, safe_y)
    x1 = x0 + box_w
    y1 = y0 + box_h

    draw.rounded_rectangle((x0, y0, x1, y1), radius=int(w * 0.03), fill=WHITE)

    y = y0 + pad_y
    for line, (lw, lh) in zip(lines, sizes):
        x = x0 + pad_x
        if any(key in line for key in highlights):
            marker_pad_x = int(font_size * 0.12)
            marker_y0 = y + int(lh * 0.52)
            marker_y1 = y + lh + int(font_size * 0.18)
            draw.rounded_rectangle(
                (x - marker_pad_x, marker_y0, x + lw + marker_pad_x, marker_y1),
                radius=int(font_size * 0.16),
                fill=MARKER,
            )
        draw.text((x, y), line, font=font, fill=NAVY)
        y += lh + line_gap

    composed = Image.alpha_composite(img, overlay).convert("RGB")
    composed.save(path_out, quality=95)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for frame in FRAMES:
        draw_telop(
            SRC / frame["src"],
            OUT / frame["out"],
            frame["lines"],
            frame["highlight"],
            frame.get("position", "top_center"),
        )


if __name__ == "__main__":
    main()
