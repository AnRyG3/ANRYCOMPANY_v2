from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
SRC_DIR = ROOT / "reel_assets" / "roentgen_name_origin_samples"
OUT_DIR = ROOT / "reel_assets" / "roentgen_name_origin_telop_frames"
CONTACT_SHEET = OUT_DIR / "contact_sheet_telop_frames.png"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (8, 30, 54, 255)
WHITE = (255, 255, 255, 240)
SHADOW = (16, 26, 38, 74)
ACCENT_BLUE = (54, 137, 168, 255)
ACCENT_YELLOW = (255, 211, 82, 255)


FRAMES = [
    ("frame_01_opening_roentgen_portrait.png", "frame_01_telop.png", ["レントゲンは", "人の名前"], "bottom", "yellow"),
    ("frame_02_patient_surprised_xray_room.png", "frame_02_telop.png", ["検査名じゃないの？"], "top", "yellow"),
    ("frame_03_roentgen_historical_lab.png", "frame_03_telop.png", ["ドイツの物理学者", "レントゲンさん"], "top", "blue"),
    ("frame_04_wife_hand_xray.png", "frame_04_telop.png", ["X線を発見した人"], "top", "blue"),
    ("frame_05_rt_explains_monitor.png", "frame_05_telop.png", ["本来の正式名では", "ありません"], "top", "blue"),
    ("frame_06_generic_order_screen_blank.png", "frame_06_telop.png", ["正確には", "X線写真・X線検査"], "top", "blue"),
    ("frame_07_hospital_reception_xray_area.png", "frame_07_telop.png", ["日本では", "レントゲンが定着"], "top", "yellow"),
    ("frame_08_rt_explains_to_patient.png", "frame_08_telop.png", ["伝わりやすく", "現場でも使います"], "top", "blue"),
    ("frame_09_rt_reviews_xray.png", "frame_09_telop.png", ["正式には", "X線写真"], "top", "blue"),
    ("frame_10_roentgen_to_modern_xray.png", "frame_10_telop.png", ["人名が", "検査名として広まった"], "bottom", "yellow"),
    ("frame_11_patient_reassured.png", "frame_11_telop.png", ["次に聞いたら", "思い出してみて"], "top", "yellow"),
    ("frame_12_save_cta_phone_ui.png", "frame_12_telop.png", ["保存して", "見返してください"], "top", "yellow"),
    ("frame_13_follow_cta_rt_bow.png", "frame_13_telop.png", ["診療放射線技師の発信", "フォローで応援お願いします"], "top", "blue"),
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
    for size in range(72, 38, -2):
        gap = max(10, int(size * 0.22))
        fnt = font(size)
        width, height, _ = text_box(draw, lines, fnt, gap)
        if width <= max_w and height <= max_h:
            return fnt, gap
    return font(38), 10


def panel_position(position: str, panel_h: int):
    x0, x1 = 74, 1006
    if position == "bottom":
        y0 = 1240
    elif position == "center":
        y0 = (H - panel_h) // 2
    else:
        y0 = 210
    return x0, y0, x1, y0 + panel_h


def draw_telop(img: Image.Image, lines: list[str], position: str, accent_kind: str) -> Image.Image:
    base = cover_resize(img).convert("RGBA")
    panel_h = 172 if len(lines) == 1 else 232
    x0, y0, x1, y1 = panel_position(position, panel_h)

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((x0 + 10, y0 + 14, x1 + 10, y1 + 14), radius=34, fill=SHADOW)
    base.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(13)))

    draw = ImageDraw.Draw(base, "RGBA")
    draw.rounded_rectangle((x0, y0, x1, y1), radius=34, fill=WHITE)
    accent = ACCENT_YELLOW if accent_kind == "yellow" else ACCENT_BLUE
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
        src = SRC_DIR / src_name
        out = OUT_DIR / out_name
        if not src.exists():
            raise FileNotFoundError(src)
        draw_telop(Image.open(src), lines, position, accent_kind).save(out, quality=95)
        outputs.append(out)
        manifest.append(
            {
                "source": str(src),
                "output": str(out),
                "telop": lines,
                "position": position,
                "accent": accent_kind,
            }
        )

    make_contact_sheet(outputs)
    (OUT_DIR / "telop_manifest.json").write_text(
        json.dumps(
            {
                "title": "レントゲンって、実は人の名前だった？",
                "font": str(FONT_PATH),
                "style": "M PLUS Rounded 1c Bold, dark navy text, white rounded rectangle, short key-point telop",
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
