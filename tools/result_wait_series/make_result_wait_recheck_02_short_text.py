from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
BASE = ROOT / "reel_assets" / "result_wait_series" / "02_recheck"
SRC = BASE / "01_no_text"
OUT = BASE / "03_short_text"
STORYBOARD = BASE / "storyboard_short_text.png"

W, H = 1080, 1920
FONT_BOLD = r"C:\Windows\Fonts\YuGothB.ttc"
FONT_REG = r"C:\Windows\Fonts\YuGothM.ttc"


CUTS = [
    ("01_retest_word.png", "再検査"),
    ("02_mind_blank.png", "頭が真っ白"),
    ("03_not_confirmed.png", "確定ではない"),
    ("04_maybe_stage.png", "もしかしたら…"),
    ("05_contrast_detail.png", "詳しく見る"),
    ("06_yes_or_no.png", "ある？ ない？"),
    ("07_next_step.png", "次のステップ"),
    ("08_not_bad_result.png", "悪い結果じゃない"),
    ("09_breathe.png", "深呼吸"),
]


def font(size: int, bold: bool = True):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def fit_font(draw: ImageDraw.ImageDraw, text: str, max_w: int, start: int = 92):
    size = start
    while size >= 52:
        fnt = font(size)
        box = draw.textbbox((0, 0), text, font=fnt)
        if box[2] - box[0] <= max_w:
            return fnt
        size -= 2
    return font(52)


def add_short_text(img: Image.Image, text: str) -> Image.Image:
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
    draw.text((W // 2, box[1] + 48), "知っておきたいこと", font=small, fill=(255, 255, 255, 220), anchor="mm")

    fnt = fit_font(draw, text, 700)
    draw.text((W // 2, box[1] + 145), text, font=fnt, fill=(255, 255, 255, 255), anchor="mm")

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
    board = Image.new("RGB", (216 * 3, 384 * 3), "white")
    for i, path in enumerate(paths):
        thumb = cover(Image.open(path).convert("RGB"), (216, 384))
        board.paste(thumb, ((i % 3) * 216, (i // 3) * 384))
    board.save(STORYBOARD, quality=94)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    out_paths = []
    for filename, text in CUTS:
        img = cover(Image.open(SRC / filename).convert("RGB"), (W, H))
        out = OUT / filename
        add_short_text(img, text).save(out, quality=95)
        out_paths.append(out)
    make_storyboard(out_paths)
    (BASE / "short_text_keywords.txt").write_text(
        "\n".join(f"{filename}: {text}" for filename, text in CUTS) + "\n",
        encoding="utf-8",
    )
    print(OUT)
    print(STORYBOARD)


if __name__ == "__main__":
    main()
