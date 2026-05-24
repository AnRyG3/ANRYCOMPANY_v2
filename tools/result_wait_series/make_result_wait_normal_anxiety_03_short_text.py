from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
BASE = ROOT / "reel_assets" / "result_wait_series" / "03_normal_anxiety"
SRC = BASE / "01_no_text"
OUT = BASE / "03_short_text"
STORYBOARD = BASE / "storyboard_short_text.png"

W, H = 1080, 1920
FONT_BOLD = r"C:\Windows\Fonts\YuGothB.ttc"
FONT_REG = r"C:\Windows\Fonts\YuGothM.ttc"


CUTS = [
    ("01_still_anxious.png", "まだ不安", "知っておきたいこと"),
    ("02_should_feel_safe.png", "安心できるはず", "知っておきたいこと"),
    ("03_cant_catch_up.png", "追いつかない", "知っておきたいこと"),
    ("04_symptom_memory.png", "症状の記憶", "知っておきたいこと"),
    ("05_searched_words.png", "検索した言葉", "知っておきたいこと"),
    ("06_burned_into_mind.png", "頭に焼きつく", "知っておきたいこと"),
    ("07_not_strange.png", "おかしくない", "知っておきたいこと"),
    ("08_receiving_result.png", "受け取るにも", "知っておきたいこと"),
    ("09_takes_time.png", "時間がかかる", "知っておきたいこと"),
    ("10_next_questions_cta.png", "質問は\n次の動画で", "次回につづく"),
]


def font(size: int, bold: bool = True):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont):
    box = draw.multiline_textbbox((0, 0), text, font=fnt, spacing=8, align="center")
    return box[2] - box[0], box[3] - box[1]


def fit_font(draw: ImageDraw.ImageDraw, text: str, max_w: int, max_h: int, start: int = 92):
    size = start
    while size >= 48:
        fnt = font(size)
        tw, th = text_size(draw, text, fnt)
        if tw <= max_w and th <= max_h:
            return fnt
        size -= 2
    return font(48)


def add_short_text(img: Image.Image, text: str, label: str) -> Image.Image:
    img = img.convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    box = (135, 1120, 945, 1375)
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((box[0] + 8, box[1] + 10, box[2] + 8, box[3] + 10), radius=36, fill=(0, 0, 0, 80))
    img.alpha_composite(shadow)

    draw.rounded_rectangle(box, radius=36, fill=(7, 28, 44, 214), outline=(255, 255, 255, 210), width=4)
    draw.rounded_rectangle((box[0], box[1], box[2], box[1] + 16), radius=8, fill=(248, 205, 83, 238))

    small = font(31, False)
    draw.text((W // 2, box[1] + 48), label, font=small, fill=(255, 255, 255, 220), anchor="mm")

    fnt = fit_font(draw, text, 700, 142)
    y = box[1] + 145
    draw.multiline_text((W // 2, y), text, font=fnt, fill=(255, 255, 255, 255), anchor="mm", spacing=8, align="center")

    img.alpha_composite(overlay)
    return img.convert("RGB")


def cover(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    w, h = size
    scale = max(w / img.width, h / img.height)
    resized = img.resize((int(img.width * scale), int(img.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - w) // 2
    top = (resized.height - h) // 2
    return resized.crop((left, top, left + w, top + h))


def make_storyboard(paths: list[Path]):
    cols, rows = 5, 2
    tw, th = 216, 384
    board = Image.new("RGB", (tw * cols, th * rows), "white")
    for i, path in enumerate(paths):
        thumb = cover(Image.open(path).convert("RGB"), (tw, th))
        board.paste(thumb, ((i % cols) * tw, (i // cols) * th))
    board.save(STORYBOARD, quality=94)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    out_paths = []
    for filename, text, label in CUTS:
        img = cover(Image.open(SRC / filename).convert("RGB"), (W, H))
        out = OUT / filename
        add_short_text(img, text, label).save(out, quality=95)
        out_paths.append(out)
    make_storyboard(out_paths)
    (BASE / "short_text_keywords.txt").write_text(
        "\n".join(f"{filename}: {text.replace(chr(10), ' / ')}" for filename, text, _ in CUTS) + "\n",
        encoding="utf-8-sig",
    )
    print(OUT)
    print(STORYBOARD)


if __name__ == "__main__":
    main()
