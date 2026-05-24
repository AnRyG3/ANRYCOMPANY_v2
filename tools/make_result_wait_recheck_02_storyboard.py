from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
BASE = ROOT / "reel_assets" / "result_wait_recheck_02_same_person"
SRC = BASE / "01_no_text"
GUIDE = BASE / "02_text_safe_guide"
STORYBOARD = BASE / "storyboard_no_text.png"
GUIDE_STORYBOARD = BASE / "storyboard_text_safe_guide.png"

W, H = 1080, 1920
FONT = r"C:\Windows\Fonts\YuGothB.ttc"


FILES = [
    "01_retest_word.png",
    "02_mind_blank.png",
    "03_not_confirmed.png",
    "04_maybe_stage.png",
    "05_contrast_detail.png",
    "06_yes_or_no.png",
    "07_next_step.png",
    "08_not_bad_result.png",
    "09_breathe.png",
]


SCRIPT = [
    "「再検査です」",
    "その言葉を聞いた瞬間、\n頭が真っ白になる方もいます。",
    "でも、再検査は\n“異常が確定した”\nという意味ではありません。",
    "最初の検査では、\n「もしかしたら…」という\n段階にしかなりません。",
    "造影剤を使って\nより詳しく見ることで、",
    "はじめて\n「ある」か「ない」かが\nわかります。",
    "つまり再検査は、\n答えを出すための\n次のステップです。",
    "再検査＝悪い結果\nではありません。",
    "怖い気持ちはわかります。\nでもまず、深呼吸してください。",
]


def font(size: int):
    return ImageFont.truetype(FONT, size)


def cover(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    w, h = size
    scale = max(w / img.width, h / img.height)
    resized = img.resize((int(img.width * scale), int(img.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - w) // 2
    top = (resized.height - h) // 2
    return resized.crop((left, top, left + w, top + h))


def make_guide(img: Image.Image, text: str) -> Image.Image:
    out = img.convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Instagram UI and CapCut subtitle safe zone: avoid the extreme top/bottom/right.
    x1, y1, x2, y2 = 115, 1040, 965, 1510
    draw.rounded_rectangle((x1, y1, x2, y2), radius=34, fill=(8, 28, 44, 164), outline=(255, 255, 255, 210), width=4)
    draw.text((W // 2, y1 + 42), "テロップ安全域", font=font(34), fill=(255, 255, 255, 238), anchor="mm")

    f = font(48)
    lines = text.split("\n")
    line_h = 62
    start_y = y1 + 145
    for i, line in enumerate(lines):
        draw.text((W // 2, start_y + i * line_h), line, font=f, fill=(255, 255, 255, 255), anchor="mm")

    out.alpha_composite(overlay)
    return out.convert("RGB")


def make_storyboard(paths: list[Path], out_path: Path):
    thumbs = []
    for path in paths:
        img = Image.open(path).convert("RGB")
        thumbs.append(cover(img, (216, 384)))
    board = Image.new("RGB", (216 * 3, 384 * 3), "white")
    for i, thumb in enumerate(thumbs):
        board.paste(thumb, ((i % 3) * 216, (i // 3) * 384))
    board.save(out_path, quality=94)


def main():
    GUIDE.mkdir(parents=True, exist_ok=True)
    src_paths = [SRC / name for name in FILES]
    guide_paths = []
    for name, text in zip(FILES, SCRIPT):
        img = Image.open(SRC / name).convert("RGB")
        guided = make_guide(cover(img, (W, H)), text)
        out = GUIDE / name
        guided.save(out, quality=94)
        guide_paths.append(out)
    make_storyboard(src_paths, STORYBOARD)
    make_storyboard(guide_paths, GUIDE_STORYBOARD)
    (BASE / "cut_order_and_telop.txt").write_text(
        "\n\n".join(f"{file}\n{script}" for file, script in zip(FILES, SCRIPT)),
        encoding="utf-8",
    )
    print(STORYBOARD)
    print(GUIDE_STORYBOARD)


if __name__ == "__main__":
    main()
