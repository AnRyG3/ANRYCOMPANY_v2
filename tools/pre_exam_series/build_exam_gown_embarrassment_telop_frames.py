from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "pre_exam_series" / "08_exam_gown_embarrassment_v1"
BG_DIR = ASSET_DIR / "background_frames"
OUT_DIR = ASSET_DIR / "telop_frames"
CONTACT_SHEET = ASSET_DIR / "contact_sheet_telop_frames.png"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (7, 28, 54, 255)
PANEL = (255, 255, 255, 238)
PANEL_EDGE = (255, 255, 255, 255)
SHADOW = (16, 26, 38, 72)
ACCENT_YELLOW = (255, 215, 93, 255)
ACCENT_GREEN = (48, 145, 134, 255)

FRAMES = [
    {
        "src": "frame_01_patient_gown_hesitant.png",
        "out": "frame_01_patient_gown_hesitant_telop.png",
        "lines": ["検査着、", "少し恥ずかしい"],
        "box": (92, 1228, 988, 1468),
        "accent": "yellow",
    },
    {
        "src": "frame_02_patient_self_conscious_sleeve.png",
        "out": "frame_02_patient_self_conscious_sleeve_telop.png",
        "lines": ["気にするの、", "変かな？"],
        "box": (120, 1238, 960, 1468),
    },
    {
        "src": "frame_03_patient_natural_resistance.png",
        "out": "frame_03_patient_natural_resistance_telop.png",
        "lines": ["抵抗感は", "自然です"],
        "box": (150, 1240, 930, 1460),
    },
    {
        "src": "frame_04_patient_checks_gown_fabric.png",
        "out": "frame_04_patient_checks_gown_fabric_telop.png",
        "lines": ["透けないかな", "ラインが気になる"],
        "box": (82, 1224, 998, 1470),
    },
    {
        "src": "frame_05_patient_corridor_reserved.png",
        "out": "frame_05_patient_corridor_reserved_telop.png",
        "lines": ["担当者の性別が", "気になることも"],
        "box": (82, 1224, 998, 1470),
    },
    {
        "src": "frame_06_rt_reassures_patient.png",
        "out": "frame_06_rt_reassures_patient_telop.png",
        "lines": ["気になることは", "伝えて大丈夫"],
        "box": (98, 1228, 982, 1468),
        "accent": "green",
    },
    {
        "src": "frame_07_patient_relief_after_talking.png",
        "out": "frame_07_patient_relief_after_talking_telop.png",
        "lines": ["恥ずかしいと", "思わなくて大丈夫"],
        "box": (70, 1222, 1010, 1474),
    },
    {
        "src": "frame_08_patient_relaxed_corridor.png",
        "out": "frame_08_patient_relaxed_corridor_telop.png",
        "lines": ["気にしすぎなくて", "大丈夫です"],
        "box": (88, 1228, 992, 1468),
    },
    {
        "src": "frame_09_save_cta_background.png",
        "out": "frame_09_save_cta_background_telop.png",
        "lines": ["検査前の不安に", "保存して見返す"],
        "box": (82, 1224, 998, 1470),
        "accent": "yellow",
    },
    {
        "src": "frame_10_follow_cta_rt_tech.png",
        "out": "frame_10_follow_cta_rt_tech_telop.png",
        "lines": ["検査の不安を", "一緒に減らしましょう"],
        "box": (66, 1220, 1014, 1472),
        "accent": "green",
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
    for size in range(82, 43, -2):
        fnt = font(size)
        width, height, _ = measure(draw, lines, fnt, spacing)
        if width <= max_w and height <= max_h:
            return fnt, spacing
    return font(44), 12


def draw_soft_readability(img: Image.Image) -> None:
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 1080, W, 1580), fill=(255, 255, 255, 18))
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

    accent = frame.get("accent")
    if accent:
        color = ACCENT_YELLOW if accent == "yellow" else ACCENT_GREEN
        draw.rounded_rectangle((x0 + 62, y1 - 35, x1 - 62, y1 - 25), radius=5, fill=color)

    fnt, spacing = fit_font(draw, lines, (x1 - x0) - 96, (y1 - y0) - 82)
    _, total_h, heights = measure(draw, lines, fnt, spacing)
    yy = y0 + ((y1 - y0) - total_h) // 2 - 4
    for line, line_h in zip(lines, heights):
        bbox = draw.textbbox((0, 0), line, font=fnt)
        line_w = bbox[2] - bbox[0]
        draw.text(((x0 + x1 - line_w) // 2, yy), line, font=fnt, fill=NAVY)
        yy += line_h + spacing


def make_contact_sheet(paths: list[Path]) -> None:
    cols = 5
    thumb_w, thumb_h = 216, 384
    label_h = 34
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (245, 247, 250))
    label_font = ImageFont.load_default()
    for idx, path in enumerate(paths):
        img = Image.open(path).convert("RGB")
        img.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), "white")
        tile.paste(img, ((thumb_w - img.width) // 2, 0))
        ImageDraw.Draw(tile).text((8, thumb_h + 10), path.name[:28], fill=(0, 0, 0), font=label_font)
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
        "style": "short telop, white rounded rectangle backing, dark navy text, M PLUS Rounded 1c Bold",
        "asset_dir": str(ASSET_DIR),
        "background_dir": str(BG_DIR),
        "telop_dir": str(OUT_DIR),
        "contact_sheet": str(CONTACT_SHEET),
        "frames": manifest_frames,
    }
    (OUT_DIR / "telop_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8-sig",
    )
    print(OUT_DIR)
    print(CONTACT_SHEET)


if __name__ == "__main__":
    main()
