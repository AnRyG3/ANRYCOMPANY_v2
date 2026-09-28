from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
BASE = ROOT / "reel_assets" / "xray_additional_pain_20260927_images"
OUT = ROOT / "reel_assets" / "xray_additional_pain_20260927_telop_frames"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"
CONTACT = OUT / "contact_sheet_telop.png"
TEXTS = OUT / "telop_texts.txt"
MANIFEST = OUT / "telop_manifest.json"

W, H = 1080, 1920
NAVY = (16, 36, 55, 255)
BLUE = (0, 104, 150, 255)
PANEL = (255, 255, 255, 179)
SHADOW = (0, 0, 0, 38)


# One message per frame. Horizontal placement stays centered; position is only
# upper, center, or lower. Blue applies only to the specific important term.
FRAMES = [
    {
        "src": "01_hook_another_pain.png",
        "out": "telop_01_hook_another_pain.png",
        "lines": [["ここも痛い…"], ["ついでに", "撮ってもらえる？"]],
        "highlights": {"ついでに"},
        "position": "center",
    },
    {
        "src": "02_consult_doctor_next.png",
        "out": "telop_02_consult_doctor_next.png",
        "lines": [["別の痛い場所は"], ["診察で", "医師", "に伝えてください"]],
        "highlights": {"医師"},
        "position": "center",
    },
    {
        "src": "03_natural_question.png",
        "out": "telop_03_natural_question.png",
        "lines": [["「ついでに」と思う気持ち"], ["自然です"]],
        "highlights": {"自然です"},
        "position": "top",
    },
    {
        "src": "04_ordered_area_confirmed.png",
        "out": "telop_04_ordered_area_confirmed.png",
        "lines": [["レントゲンは"], ["医師から", "指示された部位", "を撮影"]],
        "highlights": {"指示された部位"},
        "position": "center",
    },
    {
        "src": "05_technologist_checks_order.png",
        "out": "telop_05_technologist_checks_order.png",
        "lines": [["撮影する部位は"], ["事前の", "指示", "で決まっています"]],
        "highlights": {"指示"},
        "position": "top",
    },
    {
        "src": "06_doctor_considers_need.png",
        "out": "telop_06_doctor_considers_need.png",
        "lines": [["追加が必要かは"], ["医師", "が判断します"]],
        "highlights": {"医師"},
        "position": "top",
    },
    {
        "src": "07_process_reassurance.png",
        "out": "telop_07_process_reassurance.png",
        "lines": [["少し手間に感じても"], ["必要性を確認する", "大切な手順", "です"]],
        "highlights": {"大切な手順"},
        "position": "center",
    },
    {
        "src": "08_tell_doctor_symptoms.png",
        "out": "telop_08_tell_doctor_symptoms.png",
        "lines": [["「", "ここも痛い", "」と"], ["伝えてください"]],
        "highlights": {"ここも痛い"},
        "position": "top",
    },
    {
        "src": "09_save_before_consultation.png",
        "out": "telop_09_save_before_consultation.png",
        "lines": [["診察前に見返せるよう"], ["この投稿を", "保存"]],
        "highlights": {"保存"},
        "position": "top",
    },
    {
        "src": "10_follow_cta_technologist.png",
        "out": "telop_10_follow_cta_technologist.png",
        "lines": [["役に立ったら"], ["フォロー", "もお願いします"]],
        "highlights": {"フォロー"},
        "position": "center",
    },
]


def load_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size)


def cover(image: Image.Image, size: tuple[int, int] = (W, H)) -> Image.Image:
    image = image.convert("RGB")
    scale = max(size[0] / image.width, size[1] / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = (resized.width - size[0]) // 2
    top = (resized.height - size[1]) // 2
    return resized.crop((left, top, left + size[0], top + size[1]))


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def line_width(draw: ImageDraw.ImageDraw, line: list[str], font: ImageFont.FreeTypeFont) -> int:
    gap = round(font.size * 0.08)
    return sum(text_width(draw, item, font) for item in line) + gap * (len(line) - 1)


def fit_font(draw: ImageDraw.ImageDraw, lines: list[list[str]]) -> ImageFont.FreeTypeFont:
    for size in range(66, 39, -2):
        candidate = load_font(size)
        if max(line_width(draw, line, candidate) for line in lines) <= 790:
            return candidate
    return load_font(38)


def telop_y(position: str, box_height: int) -> int:
    if position == "top":
        return 180
    if position == "bottom":
        return H - 260 - box_height
    return (H - box_height) // 2


def draw_telop(source: Image.Image, frame: dict) -> Image.Image:
    base = cover(source).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    lines = frame["lines"]
    font = fit_font(draw, lines)
    line_height = round(font.size * 1.16)
    pad_x, pad_y = 56, 34
    box_width = min(920, max(line_width(draw, line, font) for line in lines) + pad_x * 2)
    box_height = line_height * len(lines) + pad_y * 2
    x0 = (W - box_width) // 2
    y0 = telop_y(frame["position"], box_height)
    x1, y1 = x0 + box_width, y0 + box_height

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((x0 + 6, y0 + 8, x1 + 6, y1 + 8), radius=30, fill=SHADOW)
    overlay.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(7)))
    draw.rounded_rectangle((x0, y0, x1, y1), radius=30, fill=PANEL)

    first_y = y0 + pad_y + round(font.size * 0.06)
    gap = round(font.size * 0.08)
    for row, line in enumerate(lines):
        width = line_width(draw, line, font)
        x = (W - width) // 2
        y = first_y + row * line_height
        for item in line:
            color = BLUE if item in frame["highlights"] else NAVY
            draw.text((x, y), item, font=font, fill=color)
            x += text_width(draw, item, font) + gap

    base.alpha_composite(overlay)
    return base.convert("RGB")


def make_contact_sheet(paths: list[Path]) -> None:
    columns = 4
    thumb_w, thumb_h, label_h = 216, 384, 36
    rows = math.ceil(len(paths) / columns)
    sheet = Image.new("RGB", (columns * thumb_w, rows * (thumb_h + label_h)), (246, 248, 250))
    draw = ImageDraw.Draw(sheet)
    label_font = load_font(20)
    for index, path in enumerate(paths):
        x = (index % columns) * thumb_w
        y = (index // columns) * (thumb_h + label_h)
        sheet.paste(cover(Image.open(path), (thumb_w, thumb_h)), (x, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill=(255, 255, 255))
        draw.text((x + 8, y + thumb_h + 7), f"{index + 1:02d}", font=label_font, fill=NAVY)
    sheet.save(CONTACT)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    manifest = []
    text_lines = []
    for index, frame in enumerate(FRAMES, start=1):
        source = BASE / frame["src"]
        output = OUT / frame["out"]
        if not source.exists():
            raise FileNotFoundError(source)
        draw_telop(Image.open(source), frame).save(output, quality=95)
        outputs.append(output)
        text_lines.append(f"{index:02d}. {' / '.join(''.join(line) for line in frame['lines'])}")
        manifest.append({
            "index": index,
            "source": str(source.relative_to(ROOT)),
            "output": str(output.relative_to(ROOT)),
            "telop": frame["lines"],
            "highlights": sorted(frame["highlights"]),
            "position": frame["position"],
            "font": str(FONT_PATH),
            "panel_opacity": "70%",
        })
    make_contact_sheet(outputs)
    TEXTS.write_text("\n".join(text_lines) + "\n", encoding="utf-8-sig")
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(f"created {len(outputs)} telop frames")
    print(OUT)
    print(CONTACT)


if __name__ == "__main__":
    main()
