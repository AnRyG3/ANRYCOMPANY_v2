from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
BASE = ROOT / "reel_assets" / "result_wait_series" / "06_result_today_later"
SAMPLES = BASE / "01_sample_frames"
REMAINING = BASE / "02_remaining_no_text"
OUT = BASE / "03_telop"
STORYBOARD = BASE / "storyboard_telop.png"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (16, 36, 55, 255)
BLUE = (35, 113, 181, 255)
WHITE_70 = (255, 255, 255, 179)
SHADOW = (0, 0, 0, 45)


CUTS = [
    (
        SAMPLES / "sample_01_after_scan_question.png",
        "cut_01_after_scan_question_telop.png",
        [["結果は", "後日", "……"], ["悪かったから？"]],
        {"後日"},
        980,
    ),
    (
        SAMPLES / "sample_01_after_scan_question.png",
        "cut_02_reassurance_telop.png",
        [["後日", "＝悪い結果"], ["とは", "限りません"]],
        {"後日", "限りません"},
        980,
    ),
    (
        SAMPLES / "sample_02_confirm_result_time_v2.png",
        "cut_03_confirm_time_telop.png",
        [["会計前に"], ["いつ・どこで聞くか", "確認"]],
        {"確認"},
        980,
    ),
    (
        REMAINING / "cut_04_reading_room.png",
        "cut_04_reading_room_telop.png",
        [["画像を詳しく", "確認"], ["報告書を作ることがあります"]],
        {"確認"},
        250,
    ),
    (
        REMAINING / "cut_05_doctor_explanation.png",
        "cut_05_doctor_explanation_telop.png",
        [["結果は", "主治医", "が"], ["診察内容と合わせて説明"]],
        {"主治医"},
        250,
    ),
    (
        REMAINING / "cut_06_large_hospital.png",
        "cut_06_large_hospital_telop.png",
        [["大学病院でも"], ["説明が", "別日", "の施設があります"]],
        {"別日"},
        300,
    ),
    (
        REMAINING / "cut_07_referral_return.png",
        "cut_07_referral_return_telop.png",
        [["紹介検査では"], ["結果が", "依頼元", "へ返ることも"]],
        {"依頼元"},
        250,
    ),
    (
        REMAINING / "cut_08_check_guidance.png",
        "cut_08_check_guidance_telop.png",
        [["流れは", "施設ごと", "に違います"], ["受診先の案内を", "確認"]],
        {"施設ごと", "確認"},
        980,
    ),
    (
        SAMPLES / "sample_02_confirm_result_time_v2.png",
        "cut_09_save_follow_telop.png",
        [["会計前に見返せるよう"], ["保存", "・", "フォロー", "で不安を減らそう"]],
        {"保存", "フォロー"},
        980,
    ),
]


def cover(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    width, height = size
    scale = max(width / img.width, height / img.height)
    resized = img.resize(
        (round(img.width * scale), round(img.height * scale)), Image.Resampling.LANCZOS
    )
    left = (resized.width - width) // 2
    top = (resized.height - height) // 2
    return resized.crop((left, top, left + width, top + height))


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size)


def width_of(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def line_width(draw: ImageDraw.ImageDraw, parts: list[str], fnt: ImageFont.FreeTypeFont) -> int:
    gap = int(fnt.size * 0.08)
    return sum(width_of(draw, part, fnt) for part in parts) + gap * (len(parts) - 1)


def fit_font(draw: ImageDraw.ImageDraw, lines: list[list[str]]) -> ImageFont.FreeTypeFont:
    for size in range(72, 41, -2):
        fnt = font(size)
        if max(line_width(draw, line, fnt) for line in lines) <= 820:
            return fnt
    return font(42)


def draw_line(
    draw: ImageDraw.ImageDraw,
    y: int,
    parts: list[str],
    fnt: ImageFont.FreeTypeFont,
    highlights: set[str],
) -> None:
    gap = int(fnt.size * 0.08)
    x = (W - line_width(draw, parts, fnt)) // 2
    for part in parts:
        draw.text(
            (x, y),
            part,
            font=fnt,
            fill=BLUE if part in highlights else NAVY,
            anchor="la",
        )
        x += width_of(draw, part, fnt) + gap


def add_telop(
    image: Image.Image, lines: list[list[str]], highlights: set[str], y1: int
) -> Image.Image:
    base = cover(image.convert("RGB"), (W, H)).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    fnt = fit_font(draw, lines)
    line_height = int(fnt.size * 1.24)
    max_width = max(line_width(draw, line, fnt) for line in lines)
    box_width = min(920, max_width + 120)
    box_height = line_height * len(lines) + 84
    x1 = (W - box_width) // 2
    x2 = x1 + box_width
    y2 = y1 + box_height

    draw.rounded_rectangle(
        (x1 + 6, y1 + 8, x2 + 6, y2 + 8), radius=32, fill=SHADOW
    )
    draw.rounded_rectangle((x1, y1, x2, y2), radius=32, fill=WHITE_70)

    first_y = y1 + 38 + int(fnt.size * 0.10)
    for index, line in enumerate(lines):
        draw_line(draw, first_y + index * line_height, line, fnt, highlights)

    base.alpha_composite(overlay)
    return base.convert("RGB")


def make_storyboard(paths: list[Path]) -> None:
    thumb_w, thumb_h = 216, 384
    board = Image.new("RGB", (thumb_w * 3, thumb_h * 3), "white")
    for index, path in enumerate(paths):
        thumb = cover(Image.open(path).convert("RGB"), (thumb_w, thumb_h))
        board.paste(thumb, ((index % 3) * thumb_w, (index // 3) * thumb_h))
    board.save(STORYBOARD, quality=94)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    outputs = []
    for source, output_name, lines, highlights, y1 in CUTS:
        result = add_telop(Image.open(source), lines, highlights, y1)
        output = OUT / output_name
        result.save(output, quality=95)
        outputs.append(output)
    make_storyboard(outputs)
    (BASE / "telop_texts.txt").write_text(
        "\n".join(
            f"{index:02d}. " + " / ".join("".join(line) for line in lines)
            for index, (_, _, lines, _, _) in enumerate(CUTS, start=1)
        )
        + "\n",
        encoding="utf-8-sig",
    )
    print(OUT)
    print(STORYBOARD)


if __name__ == "__main__":
    main()
