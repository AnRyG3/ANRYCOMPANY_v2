from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
SRC_DIR = ROOT / "reel_assets" / "mri_series" / "exam_discomfort_tell_staff_m70" / "image_frames"
OUT_DIR = ROOT / "reel_assets" / "mri_series" / "exam_discomfort_tell_staff_m70" / "text_frames"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (8, 30, 54, 255)
WHITE = (255, 255, 255, 238)
SHADOW = (16, 26, 38, 70)


FRAMES = [
    ("frame01_patient_flat_mri.png", "frame01_telop.png", ["急に、息が苦しい…"]),
    ("frame02_staff_call_button_flat.png", "frame02_telop.png", ["迷惑かな、と迷ったら"]),
    ("frame03_staff_reassures.png", "frame03_telop.png", ["我慢せず、すぐ伝えて"]),
    ("frame04_call_button_closeup.png", "frame04_telop.png", ["ブザーやマイクで伝えられます"]),
    ("frame05_staff_responds_control_room.png", "frame05_telop.png", ["必要に応じて", "いったん止めて対応します"]),
    ("frame06_staff_intercom.png", "frame06_telop.png", ["体調の変化も", "大切な情報です"]),
    ("frame07_patient_call_button.png", "frame07_telop.png", ["「苦しいです」だけでもOK"]),
    ("frame08_patient_reassured_flat.png", "frame08_telop.png", ["伝えることは、迷惑じゃない"]),
    ("frame09_save_cta_background.png", "frame09_telop.png", ["検査前に見返せるよう", "保存しておいてください"]),
    ("frame10_follow_cta_staff.png", "frame10_telop.png", ["フォローして", "一緒に不安を減らそう"]),
]


def cover_resize(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")
    scale = max(W / img.width, H / img.height)
    resized = img.resize((round(img.width * scale), round(img.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - W) // 2
    top = (resized.height - H) // 2
    return resized.crop((left, top, left + W, top + H))


def text_measure(draw: ImageDraw.ImageDraw, lines: list[str], font: ImageFont.FreeTypeFont, gap: int):
    boxes = [draw.textbbox((0, 0), line, font=font) for line in lines]
    widths = [box[2] - box[0] for box in boxes]
    heights = [box[3] - box[1] for box in boxes]
    return max(widths), sum(heights) + gap * (len(lines) - 1), boxes


def fit_font(draw: ImageDraw.ImageDraw, lines: list[str], max_text_w: int = int(W * 0.76)):
    for size in range(70, 40, -2):
        font = ImageFont.truetype(str(FONT_PATH), size=size)
        gap = max(10, int(size * 0.22))
        width, height, boxes = text_measure(draw, lines, font, gap)
        if width <= max_text_w and height <= 172:
            return font, gap, width, height, boxes
    font = ImageFont.truetype(str(FONT_PATH), size=40)
    width, height, boxes = text_measure(draw, lines, font, 10)
    return font, 10, width, height, boxes


def draw_telop(
    image: Image.Image,
    lines: list[str],
    x_override: int | None = None,
    max_text_w: int = int(W * 0.76),
    centered: bool = False,
) -> Image.Image:
    base = cover_resize(image).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    shadow_draw = ImageDraw.Draw(shadow_layer)
    font, gap, text_w, text_h, boxes = fit_font(draw, lines, max_text_w)

    pad_x, pad_y = 54, 30
    box_w = min(W - 160, text_w + pad_x * 2)
    box_h = text_h + pad_y * 2
    x0 = (W - box_w) // 2 if x_override is None else x_override
    y0 = (H - box_h) // 2 if centered else 250
    x1, y1 = x0 + box_w, y0 + box_h

    shadow_draw.rounded_rectangle((x0 + 8, y0 + 10, x1 + 8, y1 + 10), radius=34, fill=SHADOW)
    overlay.alpha_composite(shadow_layer.filter(ImageFilter.GaussianBlur(10)))
    draw.rounded_rectangle((x0, y0, x1, y1), radius=34, fill=WHITE)

    y = y0 + pad_y
    for line, box in zip(lines, boxes):
        line_w = box[2] - box[0]
        line_h = box[3] - box[1]
        x = (x0 + x1 - line_w) // 2
        draw.text((x, y - box[1]), line, font=font, fill=NAVY)
        y += line_h + gap

    return Image.alpha_composite(base, overlay).convert("RGB")


def contact_sheet(paths: list[Path]) -> None:
    cols, thumb_w, thumb_h, label_h = 4, 216, 384, 34
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (245, 247, 250))
    label_font = ImageFont.load_default()
    draw = ImageDraw.Draw(sheet)
    for index, path in enumerate(paths):
        x = (index % cols) * thumb_w
        y = (index // cols) * (thumb_h + label_h)
        image = Image.open(path).convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        sheet.paste(image, (x, y))
        draw.text((x + 8, y + thumb_h + 9), path.name, fill=(0, 0, 0), font=label_font)
    sheet.save(OUT_DIR / "contact_sheet_telop_frames.png", quality=94)


def main() -> None:
    if not FONT_PATH.exists():
        raise FileNotFoundError(FONT_PATH)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs, manifest = [], []
    for src_name, out_name, lines in FRAMES:
        source = SRC_DIR / src_name
        output = OUT_DIR / out_name
        if not source.exists():
            raise FileNotFoundError(source)
        if out_name == "frame10_telop.png":
            image = draw_telop(Image.open(source), lines, x_override=18, max_text_w=500)
        else:
            image = draw_telop(
                Image.open(source),
                lines,
                centered=out_name in {
                    "frame01_telop.png",
                    "frame04_telop.png",
                    "frame08_telop.png",
                    "frame09_telop.png",
                },
            )
        image.save(output, quality=95)
        outputs.append(output)
        manifest.append({"source": str(source), "output": str(output), "telop": lines, "y": 250})
    contact_sheet(outputs)
    (OUT_DIR / "telop_manifest.json").write_text(
        json.dumps({"font": str(FONT_PATH), "style": "white rounded rectangle, dark navy M PLUS Rounded 1c Bold", "frames": manifest}, ensure_ascii=False, indent=2),
        encoding="utf-8-sig",
    )
    print(OUT_DIR)


if __name__ == "__main__":
    main()
