from pathlib import Path
from shutil import copy2

from PIL import Image, ImageDraw, ImageFont

from build_keigo_work_stamps import key_green_to_alpha, trim_alpha


ROOT = Path(r"F:\ANRYCAMPANY")
BASE = ROOT / "02_LINEスタンプ" / "あんりぃ_LINEスタンプ制作工場" / "04_完成画像" / "敬語・仕事返信スタンプ_あんりぃ40"
SOURCE = BASE / "08_再設計40確認"
OUT = BASE / "09_LINE提出用"
FONT = Path(r"C:\Windows\Fonts\meiryob.ttc")


def paste_fit(canvas: Image.Image, src: Image.Image, box: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = box
    max_w = x2 - x1
    max_h = y2 - y1
    src = src.convert("RGBA")
    bbox = src.getbbox()
    if bbox:
        src = src.crop(bbox)
    ratio = min(max_w / src.width, max_h / src.height)
    resized = src.resize((int(src.width * ratio), int(src.height * ratio)), Image.Resampling.LANCZOS)
    x = x1 + (max_w - resized.width) // 2
    y = y1 + (max_h - resized.height) // 2
    canvas.alpha_composite(resized, (x, y))


def paste_chroma_fit(canvas: Image.Image, path: Path, box: tuple[int, int, int, int]) -> None:
    paste_fit(canvas, trim_alpha(key_green_to_alpha(Image.open(path))), box)


def draw_text(draw: ImageDraw.ImageDraw, text: str, xy: tuple[int, int], max_width: int, size: int, fill) -> int:
    font = ImageFont.truetype(str(FONT), size)
    while size > 12 and draw.textbbox((0, 0), text, font=font, stroke_width=0)[2] > max_width:
        size -= 1
        font = ImageFont.truetype(str(FONT), size)
    x, y = xy
    draw.text((x + 1, y + 2), text, font=font, fill=(92, 60, 48, 255), stroke_width=4, stroke_fill=(255, 255, 255, 255))
    draw.text((x, y), text, font=font, fill=fill, stroke_width=2, stroke_fill=(255, 255, 255, 255))
    return draw.textbbox((x, y), text, font=font, stroke_width=2)[3]


def build_main() -> None:
    canvas = Image.new("RGBA", (240, 240), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((8, 8, 232, 232), radius=34, fill=(245, 251, 248, 230))
    paste_chroma_fit(canvas, BASE / "03_再設計試作3個" / "生成素材" / "03_shouchi_chroma.png", (14, 78, 105, 220))
    paste_chroma_fit(canvas, BASE / "05_再設計17-24" / "生成素材" / "17_kyouyuu_chroma.png", (92, 77, 226, 222))
    draw_text(draw, "敬語", (30, 16), 88, 42, (42, 91, 150, 255))
    draw_text(draw, "仕事返信", (102, 22), 118, 28, (47, 120, 92, 255))
    canvas.save(OUT / "main.png")


def build_tab() -> None:
    canvas = Image.new("RGBA", (96, 74), (0, 0, 0, 0))
    paste_chroma_fit(canvas, BASE / "03_再設計試作3個" / "生成素材" / "04_ryoukai_chroma.png", (4, 2, 92, 72))
    canvas.save(OUT / "tab.png")


def build_preview() -> None:
    thumb = (148, 128)
    columns = 5
    rows = 8
    preview = Image.new("RGBA", (thumb[0] * columns, thumb[1] * rows), (246, 244, 241, 255))
    draw = ImageDraw.Draw(preview)
    font = ImageFont.truetype(str(FONT), 13)
    for i in range(1, 41):
        src = Image.open(OUT / f"{i:02d}.png").convert("RGBA")
        src.thumbnail((thumb[0] - 8, thumb[1] - 12), Image.Resampling.LANCZOS)
        x = ((i - 1) % columns) * thumb[0] + (thumb[0] - src.width) // 2
        y = ((i - 1) // columns) * thumb[1] + 12
        preview.alpha_composite(src, (x, y))
        draw.text((((i - 1) % columns) * thumb[0] + 4, ((i - 1) // columns) * thumb[1] + 2), f"{i:02d}", font=font, fill=(90, 86, 82, 255))
    preview.convert("RGB").save(OUT / "preview_submission_40.png", quality=95)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for i in range(1, 41):
        copy2(SOURCE / f"{i:02d}.png", OUT / f"{i:02d}.png")
    build_main()
    build_tab()
    build_preview()
    print(OUT)


if __name__ == "__main__":
    main()
