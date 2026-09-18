from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
BASE = ROOT / "reel_assets" / "pre_exam_series" / "15_chest_xray_hair_v1_images"
OUT = ROOT / "reel_assets" / "pre_exam_series" / "15_chest_xray_hair_v1_telop"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (16, 36, 55, 255)
BLUE = (0, 104, 150, 255)
WHITE = (255, 255, 255, 235)
SHADOW = (0, 0, 0, 34)


# One screen, one message. All boxes use the vertical-center safe band.
CUTS = [
    {
        "src": "01_hook_question.png",
        "out": "01_hook_question_telop.png",
        "lines": [["胸のレントゲン"], ["髪、このままで大丈夫？"]],
        "highlights": {"髪"},
    },
    {
        "src": "02_high_hair_guide.png",
        "out": "02_high_hair_guide_telop.png",
        "lines": [["迷ったら"], ["高めにまとめる"]],
        "highlights": {"高め"},
    },
    {
        "src": "03_retying_hair.png",
        "out": "03_retying_hair_telop.png",
        "lines": [["結び直すのが面倒でも"], ["大丈夫"]],
        "highlights": {"大丈夫"},
    },
    {
        "src": "04_hair_in_range.png",
        "out": "04_hair_in_range_telop.png",
        "lines": [["髪やヘアゴムが"], ["画像に重なることも"]],
        "highlights": {"重なる"},
    },
    {
        "src": "05_xray_room_variation.png",
        "out": "05_xray_room_variation_telop.png",
        "lines": [["目安は"], ["施設や髪の長さで少し違う"]],
        "highlights": {"少し違う"},
    },
    {
        "src": "06_staff_gentle_request.png",
        "out": "06_staff_gentle_request_telop.png",
        "lines": [["もう少し上で"], ["まとめてください"]],
        "highlights": {"上"},
    },
    {
        "src": "07_after_adjustment.png",
        "out": "07_after_adjustment_telop.png",
        "lines": [["その場で直せば"], ["大丈夫"]],
        "highlights": {"大丈夫"},
    },
    {
        "src": "08_staff_confirmation.png",
        "out": "08_staff_confirmation_telop.png",
        "lines": [["不安なら"], ["撮影前に確認を"]],
        "highlights": {"確認"},
    },
    {
        "src": "09_save_cta_background.png",
        "out": "09_save_cta_telop.png",
        "lines": [["検査前日に見返せるよう"], ["保存"]],
        "highlights": {"保存"},
    },
    {
        "src": "10_follow_cta_background.png",
        "out": "10_follow_cta_telop.png",
        "lines": [["検査前の迷いに答えます"], ["フォローで"]],
        "highlights": {"フォロー"},
    },
]


def cover(image: Image.Image) -> Image.Image:
    scale = max(W / image.width, H / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS
    )
    left = (resized.width - W) // 2
    top = (resized.height - H) // 2
    return resized.crop((left, top, left + W, top + H))


def text_width(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def split_line(line: str, highlights: set[str]) -> list[str]:
    parts = []
    remaining = line
    while remaining:
        next_match = min(
            ((remaining.find(word), word) for word in highlights if remaining.find(word) >= 0),
            default=(-1, ""),
            key=lambda item: item[0] if item[0] >= 0 else 10**9,
        )
        index, word = next_match
        if index < 0:
            parts.append(remaining)
            break
        if index:
            parts.append(remaining[:index])
        parts.append(word)
        remaining = remaining[index + len(word):]
    return parts


def line_width(draw: ImageDraw.ImageDraw, parts: list[str], fnt: ImageFont.FreeTypeFont) -> int:
    return sum(text_width(draw, part, fnt) for part in parts)


def fit_font(draw: ImageDraw.ImageDraw, lines: list[list[str]]) -> ImageFont.FreeTypeFont:
    for size in range(68, 39, -2):
        fnt = ImageFont.truetype(str(FONT_PATH), size)
        if max(line_width(draw, line, fnt) for line in lines) <= 820:
            return fnt
    return ImageFont.truetype(str(FONT_PATH), 38)


def add_telop(image: Image.Image, cut: dict) -> Image.Image:
    base = cover(image.convert("RGB")).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    lines = [
        split_line("".join(line) if isinstance(line, list) else line, cut["highlights"])
        for line in cut["lines"]
    ]
    fnt = fit_font(draw, lines)
    line_h = round(fnt.size * 1.22)
    pad_x, pad_y = 58, 34
    content_w = max(line_width(draw, line, fnt) for line in lines)
    box_w = min(900, content_w + pad_x * 2)
    box_h = line_h * len(lines) + pad_y * 2
    x1 = (W - box_w) // 2
    y1 = H // 2 - box_h // 2
    x2, y2 = x1 + box_w, y1 + box_h
    draw.rounded_rectangle((x1 + 5, y1 + 7, x2 + 5, y2 + 7), radius=30, fill=SHADOW)
    draw.rounded_rectangle((x1, y1, x2, y2), radius=30, fill=WHITE)

    text_y = y1 + pad_y + round(fnt.size * 0.08)
    for row, line in enumerate(lines):
        x = (W - line_width(draw, line, fnt)) // 2
        for part in line:
            color = BLUE if part in cut["highlights"] else NAVY
            draw.text((x, text_y + row * line_h), part, font=fnt, fill=color, anchor="la")
            x += text_width(draw, part, fnt)
    base.alpha_composite(overlay)
    return base.convert("RGB")


def make_contact_sheet(paths: list[Path]) -> None:
    cols, rows = 2, math.ceil(len(paths) / 2)
    thumb_w, thumb_h, label_h = 324, 576, 36
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (245, 245, 245))
    draw = ImageDraw.Draw(sheet)
    label_font = ImageFont.load_default()
    for index, path in enumerate(paths):
        thumb = cover(Image.open(path).convert("RGB")).resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (index % cols) * thumb_w
        y = (index // cols) * (thumb_h + label_h)
        sheet.paste(thumb, (x, y))
        draw.text((x + 8, y + thumb_h + 10), f"{index + 1:02d}", fill=(0, 0, 0), font=label_font)
    sheet.save(OUT / "contact_sheet_telop.jpg", quality=94)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    outputs = []
    manifest = []
    for index, cut in enumerate(CUTS, start=1):
        source = BASE / cut["src"]
        output = OUT / cut["out"]
        add_telop(Image.open(source), cut).save(output, quality=95)
        outputs.append(output)
        manifest.append(
            {
                "index": index,
                "source": str(source),
                "output": str(output),
                "telop": cut["lines"],
                "highlights": sorted(cut["highlights"]),
                "position": "center",
            }
        )
    make_contact_sheet(outputs)
    (OUT / "telop_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig"
    )
    print(f"created {len(outputs)} telop frames")
    print(OUT)


if __name__ == "__main__":
    main()
