from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
SRC_DIR = ROOT / "reel_assets" / "bone_healing_xray_check_images"
OUT_DIR = ROOT / "reel_assets" / "bone_healing_xray_check_telop_frames"
CONTACT_SHEET = OUT_DIR / "contact_sheet_telop_frames.png"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (8, 30, 54, 255)
WHITE = (255, 255, 255, 238)
SHADOW = (16, 26, 38, 70)


FRAMES = [
    ("frame_01_patient_waiting.png", "frame_01_telop.png", ["骨、くっついたかな…？"], 210),
    ("frame_02_rt_tech_monitor.png", "frame_02_telop.png", ["X線写真で確認"], 210),
    ("frame_03_rt_tech_explaining.png", "frame_03_telop.png", ["新しい骨", "「仮骨」を見ます"], 210),
    ("frame_04_rt_tech_pointing_monitor.png", "frame_04_telop.png", ["骨折線を", "またいでいるか"], 210),
    ("frame_05_rt_tech_positioning.png", "frame_05_telop.png", ["はっきり写る向きを意識"], 210),
    ("frame_06_rt_tech_careful_review.png", "frame_06_telop.png", ["場所や写り方で", "判断が難しいことも"], 210),
    ("frame_07_guiding_patient.png", "frame_07_telop.png", ["必要に応じて", "CTなどで確認"], 210),
    ("frame_08_rt_tech_nodding.png", "frame_08_telop.png", ["くっつき方には個人差"], 210),
    ("frame_09_patient_relieved.png", "frame_09_telop.png", ["心配しすぎなくて大丈夫"], 210),
    ("frame_10_smiling_exchange.png", "frame_10_telop.png", ["医師の判断に沿って確認"], 210),
    ("frame_11_save_cta_background.png", "frame_11_telop.png", ["スマホに保存"], 210),
    ("frame_12_rt_tech_bowing.png", "frame_12_telop.png", ["診療放射線技師の発信", "フォローで応援お願いします"], 210),
]


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size=size)


def cover_resize(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")
    scale = max(W / img.width, H / img.height)
    resized = img.resize((round(img.width * scale), round(img.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - W) // 2
    top = (resized.height - H) // 2
    return resized.crop((left, top, left + W, top + H))


def measure(draw: ImageDraw.ImageDraw, lines: list[str], fnt: ImageFont.FreeTypeFont, gap: int):
    boxes = [draw.textbbox((0, 0), line, font=fnt) for line in lines]
    widths = [box[2] - box[0] for box in boxes]
    heights = [box[3] - box[1] for box in boxes]
    return max(widths), sum(heights) + gap * (len(lines) - 1), boxes


def fit_font(draw: ImageDraw.ImageDraw, lines: list[str], max_w: int, max_h: int):
    for size in range(72, 42, -2):
        fnt = font(size)
        gap = max(10, int(size * 0.22))
        text_w, text_h, _ = measure(draw, lines, fnt, gap)
        if text_w <= max_w and text_h <= max_h:
            return fnt, gap
    return font(42), 10


def draw_telop(img: Image.Image, lines: list[str], y: int) -> Image.Image:
    base = cover_resize(img).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    shadow_draw = ImageDraw.Draw(shadow_layer)

    max_text_w = int(W * 0.78)
    max_text_h = 168
    fnt, gap = fit_font(draw, lines, max_text_w, max_text_h)
    text_w, text_h, boxes = measure(draw, lines, fnt, gap)

    pad_x = 56
    pad_y = 32
    box_w = min(W - 150, text_w + pad_x * 2)
    box_h = text_h + pad_y * 2
    x0 = (W - box_w) // 2
    y0 = y
    x1 = x0 + box_w
    y1 = y0 + box_h

    shadow_draw.rounded_rectangle((x0 + 8, y0 + 10, x1 + 8, y1 + 10), radius=34, fill=SHADOW)
    overlay.alpha_composite(shadow_layer.filter(ImageFilter.GaussianBlur(10)))
    draw.rounded_rectangle((x0, y0, x1, y1), radius=34, fill=WHITE)

    yy = y0 + pad_y
    for line, box in zip(lines, boxes):
        line_w = box[2] - box[0]
        line_h = box[3] - box[1]
        xx = (W - line_w) // 2
        draw.text((xx, yy - box[1]), line, font=fnt, fill=NAVY)
        yy += line_h + gap

    return Image.alpha_composite(base, overlay).convert("RGB")


def make_contact_sheet(paths: list[Path]) -> None:
    cols = 4
    thumb_w, thumb_h = 270, 480
    label_h = 34
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (245, 247, 250))
    label_font = ImageFont.load_default()

    for idx, path in enumerate(paths):
        img = Image.open(path).convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (idx % cols) * thumb_w
        y = (idx // cols) * (thumb_h + label_h)
        sheet.paste(img, (x, y))
        ImageDraw.Draw(sheet).text((x + 8, y + thumb_h + 9), path.name, fill=(0, 0, 0), font=label_font)

    sheet.save(CONTACT_SHEET, quality=94)


def main() -> None:
    if not FONT_PATH.exists():
        raise FileNotFoundError(FONT_PATH)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    manifest = []

    for src_name, out_name, lines, y in FRAMES:
        src = SRC_DIR / src_name
        out = OUT_DIR / out_name
        if not src.exists():
            raise FileNotFoundError(src)
        draw_telop(Image.open(src), lines, y).save(out, quality=95)
        outputs.append(out)
        manifest.append({"source": str(src), "output": str(out), "telop": lines, "y": y})

    make_contact_sheet(outputs)
    (OUT_DIR / "telop_manifest.json").write_text(
        json.dumps(
            {
                "title": "骨がくっついたかどうか、レントゲンだけでわかるの？",
                "font": str(FONT_PATH),
                "style": "white rounded rectangle, dark navy M PLUS Rounded 1c Bold, short telop",
                "frames": manifest,
                "contact_sheet": str(CONTACT_SHEET),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8-sig",
    )
    print(OUT_DIR)
    print(CONTACT_SHEET)


if __name__ == "__main__":
    main()
