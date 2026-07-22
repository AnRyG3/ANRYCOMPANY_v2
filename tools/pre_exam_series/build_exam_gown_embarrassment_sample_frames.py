from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "pre_exam_series" / "08_exam_gown_embarrassment_v1"
BG_DIR = ASSET_DIR / "sample_backgrounds"
OUT_DIR = ASSET_DIR / "sample_frames"
CONTACT_SHEET = OUT_DIR / "contact_sheet_sample_frames.png"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (7, 28, 54, 255)
PANEL = (255, 255, 255, 238)
PANEL_EDGE = (255, 255, 255, 255)
SHADOW = (16, 26, 38, 72)
ACCENT = (255, 215, 93, 255)

FRAMES = [
    {
        "src": "frame_01_patient_gown_hesitant.png",
        "out": "frame_01_patient_gown_hesitant_telop.png",
        "lines": ["検査着に着替えるの、", "少し恥ずかしい。"],
        "box": (70, 1210, 1010, 1484),
        "accent": True,
    },
    {
        "src": "frame_06_rt_reassures_patient.png",
        "out": "frame_06_rt_reassures_patient_telop.png",
        "lines": ["気になることは", "診療放射線技師やスタッフに", "伝えて大丈夫です。"],
        "box": (58, 1168, 1022, 1518),
        "accent": False,
    },
]


def font(size: int) -> ImageFont.FreeTypeFont:
    if not FONT_PATH.exists():
        raise FileNotFoundError(f"Required telop font not found: {FONT_PATH}")
    return ImageFont.truetype(str(FONT_PATH), size=size)


def cover_resize(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")
    scale = max(W / img.width, H / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - W) // 2
    top = (nh - H) // 2
    return resized.crop((left, top, left + W, top + H))


def measure(draw: ImageDraw.ImageDraw, lines: list[str], fnt: ImageFont.FreeTypeFont, spacing: int):
    boxes = [draw.textbbox((0, 0), line, font=fnt) for line in lines]
    widths = [box[2] - box[0] for box in boxes]
    heights = [box[3] - box[1] for box in boxes]
    return max(widths), sum(heights) + spacing * (len(lines) - 1), heights


def fit_font(draw: ImageDraw.ImageDraw, lines: list[str], max_w: int, max_h: int):
    spacing = 18
    for size in range(78, 39, -2):
        fnt = font(size)
        width, height, _ = measure(draw, lines, fnt, spacing)
        if width <= max_w and height <= max_h:
            return fnt, spacing
    return font(40), 12


def draw_soft_readability(img: Image.Image) -> None:
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 1080, W, 1600), fill=(255, 255, 255, 18))
    img.alpha_composite(overlay)


def draw_telop(img: Image.Image, frame: dict) -> None:
    x0, y0, x1, y1 = frame["box"]
    lines = frame["lines"]

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x0 + 10, y0 + 12, x1 + 10, y1 + 12), radius=34, fill=SHADOW)
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(12)))

    draw = ImageDraw.Draw(img, "RGBA")
    draw.rounded_rectangle((x0, y0, x1, y1), radius=34, fill=PANEL)
    draw.rounded_rectangle((x0 + 8, y0 + 8, x1 - 8, y1 - 8), radius=28, outline=PANEL_EDGE, width=5)
    if frame.get("accent"):
        draw.rounded_rectangle((x0 + 62, y1 - 35, x1 - 62, y1 - 25), radius=5, fill=ACCENT)

    fnt, spacing = fit_font(draw, lines, (x1 - x0) - 96, (y1 - y0) - 88)
    _, total_h, heights = measure(draw, lines, fnt, spacing)
    yy = y0 + ((y1 - y0) - total_h) // 2 - 4
    for line, line_h in zip(lines, heights):
        bbox = draw.textbbox((0, 0), line, font=fnt)
        line_w = bbox[2] - bbox[0]
        draw.text(((x0 + x1 - line_w) // 2, yy), line, font=fnt, fill=NAVY)
        yy += line_h + spacing


def make_contact_sheet(paths: list[Path]) -> None:
    cols = 2
    thumb_w, thumb_h = 300, 533
    label_h = 36
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (245, 247, 250))
    label_font = ImageFont.load_default()
    for idx, path in enumerate(paths):
        img = Image.open(path).convert("RGB")
        img.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), "white")
        tile.paste(img, ((thumb_w - img.width) // 2, 0))
        ImageDraw.Draw(tile).text((8, thumb_h + 10), path.name[:34], fill=(0, 0, 0), font=label_font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
    sheet.save(CONTACT_SHEET, quality=95)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    manifest_frames = []
    for frame in FRAMES:
        src = BG_DIR / frame["src"]
        out = OUT_DIR / frame["out"]
        img = cover_resize(Image.open(src)).convert("RGBA")
        draw_soft_readability(img)
        draw_telop(img, frame)
        img.convert("RGB").save(out, quality=95)
        outputs.append(out)
        manifest_frames.append(
            {
                "source": str(src),
                "output": str(out),
                "telop": frame["lines"],
                "box": frame["box"],
            }
        )

    make_contact_sheet(outputs)
    manifest = {
        "title": "検査着に着替えるの、少し恥ずかしい",
        "size": {"width": W, "height": H},
        "style": "white rounded rectangle backing, dark navy text, M PLUS Rounded 1c Bold",
        "asset_dir": str(ASSET_DIR),
        "sample_frames": manifest_frames,
        "contact_sheet": str(CONTACT_SHEET),
    }
    (OUT_DIR / "sample_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8-sig",
    )
    print(OUT_DIR)
    print(CONTACT_SHEET)


if __name__ == "__main__":
    main()
