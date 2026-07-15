from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "same_exam_different_positioning_images"
OUT_DIR = ROOT / "reel_assets" / "same_exam_different_positioning_telop_frames"
CONTACT_SHEET = OUT_DIR / "contact_sheet_telop_frames.png"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (8, 30, 54, 255)
WHITE = (255, 255, 255, 238)
SHADOW = (16, 26, 38, 70)
ACCENT = (57, 139, 154, 255)
ACCENT_YELLOW = (255, 213, 86, 255)


FRAMES = [
    ("slide01_patient_puzzled.png", "slide01_telop.png", ["前回と違う？"], "top", "yellow"),
    ("slide02_patient_closeup.png", "slide02_telop.png", ["やり方が", "違うのかな"], "top", "yellow"),
    ("slide03_blurred_room.png", "slide03_telop.png", ["同じ検査でも", "微調整します"], "top", "green"),
    ("slide04_hands_adjustment.png", "slide04_telop.png", ["支え方を", "少し変えることも"], "top", "green"),
    ("slide05_supported_angle.png", "slide05_telop.png", ["楽な姿勢で", "支えます"], "top", "green"),
    ("slide06_monitor_review.png", "slide06_telop.png", ["前回画像も", "確認します"], "top", "green"),
    ("slide07_patient_reassured.png", "slide07_telop.png", ["毎回見て", "くれているんだ"], "top", "yellow"),
    ("slide08_explanation.png", "slide08_telop.png", ["その日の状態に", "合わせます"], "top", "green"),
    ("slide09_tech_monitor_work.png", "slide09_telop.png", ["必要な情報を", "得やすく"], "top", "green"),
    ("slide10_patient_leaving.png", "slide10_telop.png", ["理由がある", "調整です"], "top", "yellow"),
    ("slide11_save_phone.png", "slide11_telop.png", ["あとで見返すなら", "保存"], "top", "yellow"),
    ("slide12_cta_bow.png", "slide12_telop.png", ["診療放射線技師の発信", "フォローで応援お願いします"], "top", "green"),
]


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size=size)


def cover_resize(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")
    scale = max(W / img.width, H / img.height)
    resized = img.resize((int(img.width * scale), int(img.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - W) // 2
    top = (resized.height - H) // 2
    return resized.crop((left, top, left + W, top + H))


def text_box(draw: ImageDraw.ImageDraw, lines: list[str], fnt: ImageFont.FreeTypeFont, gap: int) -> tuple[int, int, list[int]]:
    boxes = [draw.textbbox((0, 0), line, font=fnt) for line in lines]
    widths = [box[2] - box[0] for box in boxes]
    heights = [box[3] - box[1] for box in boxes]
    return max(widths), sum(heights) + gap * (len(lines) - 1), heights


def fit_font(draw: ImageDraw.ImageDraw, lines: list[str], max_w: int, max_h: int) -> tuple[ImageFont.FreeTypeFont, int]:
    for size in range(72, 42, -2):
        gap = max(10, int(size * 0.22))
        fnt = font(size)
        width, height, _ = text_box(draw, lines, fnt, gap)
        if width <= max_w and height <= max_h:
            return fnt, gap
    return font(42), 10


def panel_position(position: str, panel_h: int) -> tuple[int, int, int, int]:
    x0, x1 = 74, 1006
    if position == "bottom":
        y0 = 1160
    elif position == "center":
        y0 = (H - panel_h) // 2
    else:
        y0 = 190
    return x0, y0, x1, y0 + panel_h


def draw_telop(img: Image.Image, lines: list[str], position: str, accent_kind: str) -> None:
    panel_h = 190 if len(lines) == 1 else 245
    x0, y0, x1, y1 = panel_position(position, panel_h)

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x0 + 10, y0 + 14, x1 + 10, y1 + 14), radius=34, fill=SHADOW)
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(13)))

    draw = ImageDraw.Draw(img, "RGBA")
    draw.rounded_rectangle((x0, y0, x1, y1), radius=34, fill=WHITE)
    accent = ACCENT_YELLOW if accent_kind == "yellow" else ACCENT
    draw.rounded_rectangle((x0 + 64, y1 - 32, x1 - 64, y1 - 23), radius=5, fill=accent)

    fnt, gap = fit_font(draw, lines, (x1 - x0) - 96, (y1 - y0) - 84)
    _, total_h, heights = text_box(draw, lines, fnt, gap)
    yy = y0 + ((y1 - y0) - total_h) // 2 - 10
    for line, line_h in zip(lines, heights):
        bbox = draw.textbbox((0, 0), line, font=fnt)
        line_w = bbox[2] - bbox[0]
        xx = x0 + ((x1 - x0) - line_w) // 2
        draw.text((xx, yy), line, font=fnt, fill=NAVY)
        yy += line_h + gap


def make_contact_sheet(paths: list[Path]) -> None:
    cols = 4
    thumb_w, thumb_h = 216, 384
    label_h = 34
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (245, 247, 250))
    label_font = ImageFont.load_default()
    for idx, path in enumerate(paths):
        im = Image.open(path).convert("RGB")
        im.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), "white")
        tile.paste(im, ((thumb_w - im.width) // 2, 0))
        ImageDraw.Draw(tile).text((8, thumb_h + 9), path.name, fill=(0, 0, 0), font=label_font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
    sheet.save(CONTACT_SHEET, quality=94)


def main() -> None:
    if not FONT_PATH.exists():
        raise FileNotFoundError(FONT_PATH)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    manifest = []
    for src_name, out_name, lines, position, accent_kind in FRAMES:
        src = ASSET_DIR / src_name
        out = OUT_DIR / out_name
        if not src.exists():
            raise FileNotFoundError(src)
        img = cover_resize(Image.open(src)).convert("RGBA")
        draw_telop(img, lines, position, accent_kind)
        img.convert("RGB").save(out, quality=95)
        outputs.append(out)
        manifest.append({"source": str(src), "output": str(out), "telop": lines})

    make_contact_sheet(outputs)
    (OUT_DIR / "telop_manifest.json").write_text(
        json.dumps(
            {
                "title": "同じ検査なのに前回と撮り方が違う気がする",
                "font": str(FONT_PATH),
                "style": "white rounded rectangle, dark navy M PLUS Rounded 1c Bold",
                "frames": manifest,
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
