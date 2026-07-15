from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "postop_xray_followup_images"
OUT_DIR = ROOT / "reel_assets" / "postop_xray_followup_telop_frames"
CONTACT_SHEET = OUT_DIR / "contact_sheet_telop_frames.png"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (8, 30, 54, 255)
WHITE = (255, 255, 255, 238)
SHADOW = (16, 26, 38, 70)
ACCENT = (57, 139, 154, 255)
ACCENT_YELLOW = (255, 213, 86, 255)


FRAMES = [
    ("frame_01_patient_waiting.png", "frame_01_telop.png", ["またレントゲン？"], "top", "yellow"),
    ("frame_02_explanation.png", "frame_02_telop.png", ["術後の状態確認です"], "top", "green"),
    ("frame_03_monitor_real_xray.png", "frame_03_telop.png", ["金属の位置を確認"], "top", "green"),
    ("frame_04_plate_screw_explanation.png", "frame_04_telop.png", ["ズレがないか確認"], "top", "green"),
    ("frame_05_schedule_check.png", "frame_05_telop.png", ["タイミングごとに撮影"], "top", "green"),
    ("frame_06_xray_comparison.png", "frame_06_telop.png", ["前回画像と比較します"], "top", "green"),
    ("frame_07_reassuring_talk.png", "frame_07_telop.png", ["回復を見守る検査"], "top", "yellow"),
    ("frame_08_xray_preparation.png", "frame_08_telop.png", ["決まった時期に確認"], "top", "green"),
    ("frame_09_patient_relief.png", "frame_09_telop.png", ["丁寧に見てもらえています"], "top", "yellow"),
    ("frame_10_closing_smile.png", "frame_10_telop.png", ["安心して受けてください"], "top", "yellow"),
    ("frame_11_cta_save_smartphone.png", "frame_11_telop.png", ["保存して見返せます"], "top", "yellow"),
    ("frame_12_cta_bow.png", "frame_12_telop.png", ["診療放射線技師の発信", "フォローで応援お願いします"], "top", "green"),
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


def text_box(draw: ImageDraw.ImageDraw, lines: list[str], fnt: ImageFont.FreeTypeFont, gap: int):
    boxes = [draw.textbbox((0, 0), line, font=fnt) for line in lines]
    widths = [box[2] - box[0] for box in boxes]
    heights = [box[3] - box[1] for box in boxes]
    return max(widths), sum(heights) + gap * (len(lines) - 1), boxes


def fit_font(draw: ImageDraw.ImageDraw, lines: list[str], max_w: int, max_h: int):
    for size in range(72, 42, -2):
        gap = max(10, int(size * 0.22))
        fnt = font(size)
        width, height, _ = text_box(draw, lines, fnt, gap)
        if width <= max_w and height <= max_h:
            return fnt, gap
    return font(42), 10


def panel_position(position: str, panel_h: int):
    x0, x1 = 74, 1006
    if position == "bottom":
        y0 = 1160
    elif position == "center":
        y0 = (H - panel_h) // 2
    else:
        y0 = 190
    return x0, y0, x1, y0 + panel_h


def draw_telop(img: Image.Image, lines: list[str], position: str, accent_kind: str) -> Image.Image:
    base = cover_resize(img).convert("RGBA")
    panel_h = 178 if len(lines) == 1 else 236
    x0, y0, x1, y1 = panel_position(position, panel_h)

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x0 + 10, y0 + 14, x1 + 10, y1 + 14), radius=34, fill=SHADOW)
    base.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(13)))

    draw = ImageDraw.Draw(base, "RGBA")
    draw.rounded_rectangle((x0, y0, x1, y1), radius=34, fill=WHITE)
    accent = ACCENT_YELLOW if accent_kind == "yellow" else ACCENT
    draw.rounded_rectangle((x0 + 64, y1 - 31, x1 - 64, y1 - 22), radius=5, fill=accent)

    fnt, gap = fit_font(draw, lines, (x1 - x0) - 112, (y1 - y0) - 86)
    _, total_h, boxes = text_box(draw, lines, fnt, gap)
    yy = y0 + ((y1 - y0) - total_h) // 2 - 11
    for line, box in zip(lines, boxes):
        line_w = box[2] - box[0]
        line_h = box[3] - box[1]
        xx = x0 + ((x1 - x0) - line_w) // 2
        draw.text((xx, yy - box[1]), line, font=fnt, fill=NAVY)
        yy += line_h + gap

    return base.convert("RGB")


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
        draw_telop(Image.open(src), lines, position, accent_kind).save(out, quality=95)
        outputs.append(out)
        manifest.append({"source": str(src), "output": str(out), "telop": lines})

    make_contact_sheet(outputs)
    (OUT_DIR / "telop_manifest.json").write_text(
        json.dumps(
            {
                "title": "手術のあと、何度もレントゲンを撮るのはなぜ？",
                "font": str(FONT_PATH),
                "style": "white rounded rectangle, dark navy M PLUS Rounded 1c Bold, short key-point telop",
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
