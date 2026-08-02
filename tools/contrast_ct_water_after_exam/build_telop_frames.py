from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "contrast_ct_water_after_exam_images"
OUT_DIR = ROOT / "reel_assets" / "contrast_ct_water_after_exam_telop_frames"
CONTACT_SHEET = OUT_DIR / "contact_sheet_telop_frames.png"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (8, 30, 54, 255)
ACCENT = (28, 122, 142, 255)
WARN = (215, 133, 34, 255)
WHITE = (255, 255, 255, 240)
PANEL_EDGE = (255, 255, 255, 255)
SHADOW = (16, 26, 38, 76)


FRAMES = [
    {
        "src": "frame_01_opening_patient_water.png",
        "out": "frame_01_opening_patient_water_telop.png",
        "lines": [[("水分", "accent"), ("って、そんなに大事？", "navy")]],
        "y": 315,
    },
    {
        "src": "frame_02_rt_explains_water.png",
        "out": "frame_02_rt_explains_water_telop.png",
        "lines": [[("何度も言われると", "navy")], [("少し気になりますよね", "navy")]],
        "centered": True,
    },
    {
        "src": "frame_03_patient_reassured.png",
        "out": "frame_03_patient_reassured_telop.png",
        "lines": [[("その気持ち", "accent")], [("おかしくありません", "navy")]],
        "y": 330,
    },
    {
        "src": "frame_04_rt_ct_explanation.png",
        "out": "frame_04_rt_ct_explanation_telop.png",
        "lines": [[("造影剤", "accent"), ("は少しずつ", "navy")], [("体の外へ出ていきます", "navy")]],
        "y": 315,
    },
    {
        "src": "frame_05_patient_drinks_water.png",
        "out": "frame_05_patient_drinks_water_telop.png",
        "lines": [[("主に", "navy"), ("尿", "accent"), ("として", "navy")], [("出ていきます", "navy")]],
        "y": 315,
    },
    {
        "src": "frame_06_more_water_explanation.png",
        "out": "frame_06_more_water_explanation_telop.png",
        "lines": [[("水分", "accent"), ("をとることは", "navy")], [("排出の助けになります", "navy")]],
        "y": 340,
    },
    {
        "src": "frame_07_usual_hydration.png",
        "out": "frame_07_usual_hydration_telop.png",
        "lines": [[("特別なことではなく", "navy")], [("少し意識するだけ", "accent")]],
        "y": 350,
    },
    {
        "src": "frame_08_mild_concern.png",
        "out": "frame_08_mild_concern_telop.png",
        "lines": [[("不安になるのも", "navy")], [("自然なことです", "accent")]],
        "y": 340,
    },
    {
        "src": "frame_09_reassuring_close.png",
        "out": "frame_09_reassuring_close_telop.png",
        "lines": [[("危険という意味では", "navy")], [("ありません", "warn")]],
        "y": 315,
    },
    {
        "src": "frame_10_cta_end_card.png",
        "out": "frame_10_cta_end_card_telop.png",
        "lines": [[("保存", "accent"), ("して", "navy")], [("見返してください", "navy")]],
        "y": 330,
    },
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


def color(kind: str) -> tuple[int, int, int, int]:
    if kind == "accent":
        return ACCENT
    if kind == "warn":
        return WARN
    return NAVY


def measure_line(draw: ImageDraw.ImageDraw, segments, fnt) -> tuple[int, int]:
    width = 0
    height = 0
    for text, _ in segments:
        box = draw.textbbox((0, 0), text, font=fnt)
        width += box[2] - box[0]
        height = max(height, box[3] - box[1])
    return width, height


def measure_lines(draw: ImageDraw.ImageDraw, lines, fnt, gap: int):
    sizes = [measure_line(draw, line, fnt) for line in lines]
    return max(width for width, _ in sizes), sum(height for _, height in sizes) + gap * (len(lines) - 1), sizes


def fit_font(draw: ImageDraw.ImageDraw, lines):
    for size in range(72, 42, -2):
        fnt = font(size)
        gap = max(12, int(size * 0.22))
        width, height, sizes = measure_lines(draw, lines, fnt, gap)
        if width <= 840 and height <= 178:
            return fnt, gap, sizes, width, height
    fnt = font(42)
    gap = 12
    width, height, sizes = measure_lines(draw, lines, fnt, gap)
    return fnt, gap, sizes, width, height


def draw_telop(source: Path, frame: dict) -> Image.Image:
    base = cover_resize(Image.open(source)).convert("RGBA")

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    shadow_draw = ImageDraw.Draw(shadow)

    lines = frame["lines"]
    fnt, gap, sizes, text_w, text_h = fit_font(draw, lines)
    pad_x, pad_y = 52, 32
    box_w = min(W - 150, text_w + pad_x * 2)
    box_h = text_h + pad_y * 2
    x0 = (W - box_w) // 2
    y0 = (H - box_h) // 2 if frame.get("centered") else frame.get("y", 315)
    x1, y1 = x0 + box_w, y0 + box_h

    shadow_draw.rounded_rectangle((x0 + 8, y0 + 12, x1 + 8, y1 + 12), radius=34, fill=SHADOW)
    overlay.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(12)))
    draw.rounded_rectangle((x0, y0, x1, y1), radius=34, fill=WHITE)
    draw.rounded_rectangle((x0 + 7, y0 + 7, x1 - 7, y1 - 7), radius=28, outline=PANEL_EDGE, width=4)

    yy = y0 + pad_y
    for line, (line_w, line_h) in zip(lines, sizes):
        xx = x0 + (box_w - line_w) // 2
        for text, kind in line:
            box = draw.textbbox((0, 0), text, font=fnt)
            draw.text((xx, yy - box[1]), text, font=fnt, fill=color(kind))
            xx += box[2] - box[0]
        yy += line_h + gap

    return Image.alpha_composite(base, overlay).convert("RGB")


def make_contact_sheet(paths: list[Path]) -> None:
    cols, thumb_w, thumb_h, label_h = 5, 180, 320, 34
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (245, 247, 250))
    label_font = ImageFont.load_default()
    for idx, path in enumerate(paths):
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), "white")
        tile.paste(image, ((thumb_w - image.width) // 2, 0))
        ImageDraw.Draw(tile).text((8, thumb_h + 9), path.name[:26], fill=(0, 0, 0), font=label_font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
    sheet.save(CONTACT_SHEET, quality=94)


def plain_lines(lines) -> list[str]:
    return ["".join(text for text, _ in line) for line in lines]


def main() -> None:
    if not FONT_PATH.exists():
        raise FileNotFoundError(FONT_PATH)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    outputs = []
    manifest_frames = []
    for frame in FRAMES:
        source = ASSET_DIR / frame["src"]
        output = OUT_DIR / frame["out"]
        if not source.exists():
            raise FileNotFoundError(source)
        image = draw_telop(source, frame)
        image.save(output, quality=95)
        outputs.append(output)
        manifest_frames.append(
            {
                "source": str(source),
                "output": str(output),
                "telop": plain_lines(frame["lines"]),
            }
        )

    make_contact_sheet(outputs)
    (OUT_DIR / "telop_manifest.json").write_text(
        json.dumps(
            {
                "title": "造影剤の検査後、水分をとるように言われる理由",
                "font": str(FONT_PATH),
                "style": "white rounded rectangle backing, dark navy M PLUS Rounded 1c Bold, key words accented",
                "size": {"width": W, "height": H},
                "frames": manifest_frames,
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
