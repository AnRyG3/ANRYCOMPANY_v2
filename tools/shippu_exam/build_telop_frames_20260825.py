from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
BASE = ROOT / "reel_assets" / "shippu_exam_20260825_images"
OUT = ROOT / "reel_assets" / "shippu_exam_20260825_telop_frames"
CONTACT = OUT / "contact_sheet_20260825_telop_frames.jpg"
TEXTS = OUT / "telop_texts_20260825.txt"
MANIFEST = OUT / "telop_manifest_20260825.json"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (16, 36, 55, 255)
ACCENT = (0, 104, 150, 255)
WHITE = (255, 255, 255, 242)
SHADOW = (0, 0, 0, 36)


CUTS = [
    {
        "src": "image_01_patient_notices_large_patch.png",
        "out": "telop_01_patient_notices_large_patch.png",
        "lines": [["湿布", "を貼ったまま"], ["来ちゃった時"]],
        "highlights": {"湿布"},
        "top_y": 170,
    },
    {
        "src": "image_02_patient_wonders_remove_patch.png",
        "out": "telop_02_patient_wonders_remove_patch.png",
        "lines": [["外していいか"], ["迷ったら"]],
        "highlights": {"迷ったら"},
        "top_y": 170,
    },
    {
        "src": "image_03_patient_pauses_before_removing.png",
        "out": "telop_03_patient_pauses_before_removing.png",
        "lines": [["自分で外さず"], ["まず", "確認"]],
        "highlights": {"確認"},
        "top_y": 170,
    },
    {
        "src": "image_04_rt_reassuring_acceptance.png",
        "out": "telop_04_rt_reassuring_acceptance.png",
        "lines": [["その", "気持ち"], ["おかしくありません"]],
        "highlights": {"気持ち"},
        "top_y": 190,
    },
    {
        "src": "image_05_exam_content_confirmation.png",
        "out": "telop_05_exam_content_confirmation.png",
        "lines": [["検査内容", "によって"], ["確認", "が必要なことも"]],
        "highlights": {"検査内容", "確認"},
        "top_y": 170,
    },
    {
        "src": "image_06_no_rush_to_remove.png",
        "out": "telop_06_no_rush_to_remove.png",
        "lines": [["慌てて外さなくて"], ["大丈夫", "です"]],
        "highlights": {"大丈夫"},
        "top_y": 170,
    },
    {
        "src": "image_07_tells_rt_large_patch.png",
        "out": "telop_07_tells_rt_large_patch.png",
        "lines": [["受付や検査前に"], ["伝えて", "ください"]],
        "highlights": {"伝えて"},
        "top_y": 170,
    },
    {
        "src": "image_08_where_and_when_confirmation.png",
        "out": "telop_08_where_and_when_confirmation.png",
        "lines": [["どこ", "に・", "いつから", "を"], ["伝える", "と確認しやすい"]],
        "highlights": {"どこ", "いつから", "伝える"},
        "top_y": 170,
    },
    {
        "src": "image_09_patient_remembers_to_tell.png",
        "out": "telop_09_patient_remembers_to_tell.png",
        "lines": [["気づいた時に"], ["伝えれば", "大丈夫"]],
        "highlights": {"大丈夫"},
        "top_y": 170,
    },
    {
        "src": "image_10_save_follow_cta_space.png",
        "out": "telop_10_save_follow_cta_space.png",
        "lines": [["検査前日に"], ["見返せるよう", "保存"]],
        "highlights": {"保存"},
        "top_y": 560,
    },
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


def line_width(draw: ImageDraw.ImageDraw, line: list[str], fnt: ImageFont.FreeTypeFont) -> int:
    gap = int(fnt.size * 0.08)
    return sum(segment_width(draw, part, fnt) for part in line) + gap * (len(line) - 1)


def fit_font(draw: ImageDraw.ImageDraw, lines: list[list[str]], max_w: int) -> ImageFont.FreeTypeFont:
    for size in range(64, 37, -2):
        fnt = font(size)
        if max(line_width(draw, line, fnt) for line in lines) <= max_w:
            return fnt
    return font(38)


def draw_centered_line(
    draw: ImageDraw.ImageDraw,
    y: int,
    line: list[str],
    fnt: ImageFont.FreeTypeFont,
    highlights: set[str],
) -> None:
    gap = int(fnt.size * 0.08)
    total = line_width(draw, line, fnt)
    x = (W - total) // 2
    for part in line:
        color = ACCENT if part in highlights else NAVY
        draw.text((x, y), part, font=fnt, fill=color, anchor="la")
        x += segment_width(draw, part, fnt) + gap


def add_telop(img: Image.Image, lines: list[list[str]], highlights: set[str], top_y: int) -> Image.Image:
    img = cover(img.convert("RGB"), (W, H)).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    fnt = fit_font(draw, lines, 820)
    size = fnt.size
    line_h = int(size * 1.16)
    pad_x, pad_y = 56, 36
    box_w = min(920, max(line_width(draw, line, fnt) for line in lines) + pad_x * 2)
    box_h = line_h * len(lines) + pad_y * 2
    box_x1 = (W - box_w) // 2
    box_y1 = top_y
    box_x2 = box_x1 + box_w
    box_y2 = box_y1 + box_h

    draw.rounded_rectangle((box_x1 + 5, box_y1 + 7, box_x2 + 5, box_y2 + 7), radius=30, fill=SHADOW)
    draw.rounded_rectangle((box_x1, box_y1, box_x2, box_y2), radius=30, fill=WHITE)

    first_y = box_y1 + pad_y + int(size * 0.08)
    for i, line in enumerate(lines):
        draw_centered_line(draw, first_y + i * line_h, line, fnt, highlights)

    img.alpha_composite(overlay)
    return img.convert("RGB")


def make_contact_sheet(paths: list[Path]) -> None:
    cols, rows = 3, 4
    tw, th = 240, 426
    label_h = 34
    sheet = Image.new("RGB", (tw * cols, (th + label_h) * rows), (245, 245, 245))
    draw = ImageDraw.Draw(sheet)
    label_font = ImageFont.load_default()
    for i, path in enumerate(paths):
        thumb = cover(Image.open(path).convert("RGB"), (tw, th))
        x = (i % cols) * tw
        y = (i // cols) * (th + label_h)
        sheet.paste(thumb, (x, y))
        draw.text((x + 8, y + th + 8), path.stem[:28], fill=(0, 0, 0), font=label_font)
    sheet.save(CONTACT, quality=92)


def main() -> None:
    if not FONT_PATH.exists():
        raise FileNotFoundError(f"Required telop font not found: {FONT_PATH}")

    OUT.mkdir(parents=True, exist_ok=True)
    out_paths: list[Path] = []
    text_lines: list[str] = []
    manifest = []

    for i, cut in enumerate(CUTS, start=1):
        src = BASE / cut["src"]
        out = OUT / cut["out"]
        if not src.exists():
            raise FileNotFoundError(src)
        add_telop(Image.open(src), cut["lines"], cut["highlights"], cut["top_y"]).save(out, quality=95)
        out_paths.append(out)
        text = " / ".join("".join(line) for line in cut["lines"])
        text_lines.append(f"{i:02d}. {text}")
        manifest.append(
            {
                "index": i,
                "source": str(src),
                "output": str(out),
                "telop": cut["lines"],
                "highlights": sorted(cut["highlights"]),
                "top_y": cut["top_y"],
                "x_axis": "center",
                "font": str(FONT_PATH),
            }
        )

    make_contact_sheet(out_paths)
    TEXTS.write_text("\n".join(text_lines) + "\n", encoding="utf-8-sig")
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"created {len(out_paths)} telop frames")
    print(OUT)
    print(CONTACT)


if __name__ == "__main__":
    main()
