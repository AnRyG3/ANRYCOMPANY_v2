from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "name_dob_check_samples"
OUT_DIR = ROOT / "reel_assets" / "name_dob_check_telop_frames"
CONTACT_SHEET = OUT_DIR / "_contact_sheet_name_dob_telop.png"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (12, 46, 78, 255)
WHITE = (255, 255, 255, 238)
WHITE_OUTLINE = (255, 255, 255, 255)
SHADOW = (18, 28, 38, 74)


FRAMES = [
    {
        "src": "sample_01_patient_confused.png",
        "out": "frame_01_telop.png",
        "lines": ["名前、また聞かれた？"],
        "y0": 820,
    },
    {
        "src": "frame_02_tech_welcomes_patient.png",
        "out": "frame_02_telop.png",
        "lines": ["検査ごとに確認します"],
        "y0": 820,
    },
    {
        "src": "frame_03_chart_confirmation.png",
        "out": "frame_03_telop.png",
        "lines": ["取り違えを防ぐため"],
        "y0": 820,
    },
    {
        "src": "frame_04_explain_sequence.png",
        "out": "frame_04_telop.png",
        "lines": ["確認はこの順番"],
        "y0": 820,
    },
    {
        "src": "sample_02_identity_check_conversation.png",
        "out": "frame_05_telop.png",
        "lines": ["お名前と生年月日"],
    },
    {
        "src": "frame_06_body_part_confirmation.png",
        "out": "frame_06_telop.png",
        "lines": ["撮影部位も確認"],
        "y0": 820,
    },
    {
        "src": "frame_07_pain_location_check.png",
        "out": "frame_07_telop.png",
        "lines": ["痛い場所も確認"],
    },
    {
        "src": "frame_08_safety_procedure_nod.png",
        "out": "frame_08_telop.png",
        "lines": ["安全のための手順"],
        "y0": 820,
    },
    {
        "src": "frame_09_patient_relieved.png",
        "out": "frame_09_telop.png",
        "lines": ["大切にしている証拠"],
        "y0": 820,
    },
    {
        "src": "frame_10_cta_bow.png",
        "out": "frame_10_telop.png",
        "lines": ["保存・フォローで応援"],
        "y0": 820,
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


def text_metrics(draw: ImageDraw.ImageDraw, lines: list[str], fnt: ImageFont.FreeTypeFont, gap: int):
    boxes = [draw.textbbox((0, 0), line, font=fnt) for line in lines]
    widths = [box[2] - box[0] for box in boxes]
    heights = [box[3] - box[1] for box in boxes]
    return max(widths), sum(heights) + gap * (len(lines) - 1), heights


def fit_font(draw: ImageDraw.ImageDraw, lines: list[str], max_w: int, max_h: int):
    for size in range(74, 43, -2):
        fnt = font(size)
        gap = 16 if len(lines) > 1 else 0
        width, height, _ = text_metrics(draw, lines, fnt, gap)
        if width <= max_w and height <= max_h:
            return fnt, gap
    return font(44), 12


def add_readability_layer(img: Image.Image):
    overlay = Image.new("RGBA", (W, H), (255, 255, 255, 18))
    img.alpha_composite(overlay)


def draw_telop(img: Image.Image, lines: list[str], y0_override: int | None = None):
    draw = ImageDraw.Draw(img, "RGBA")
    max_w = 900
    box_h = 158 if len(lines) == 1 else 238
    x0 = 90
    x1 = W - 90
    y0 = y0_override if y0_override is not None else 238
    y1 = y0 + box_h

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((x0 + 10, y0 + 12, x1 + 10, y1 + 12), radius=34, fill=SHADOW)
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(12)))

    draw.rounded_rectangle((x0, y0, x1, y1), radius=34, fill=WHITE)
    draw.rounded_rectangle((x0 + 8, y0 + 8, x1 - 8, y1 - 8), radius=28, outline=WHITE_OUTLINE, width=5)

    fnt, gap = fit_font(draw, lines, max_w, box_h - 56)
    _, total_h, heights = text_metrics(draw, lines, fnt, gap)
    yy = y0 + (box_h - total_h) // 2 - 4
    for line, height in zip(lines, heights):
        bbox = draw.textbbox((0, 0), line, font=fnt)
        text_w = bbox[2] - bbox[0]
        draw.text(((W - text_w) // 2, yy), line, font=fnt, fill=NAVY)
        yy += height + gap


def make_contact_sheet(paths: list[Path]):
    cols = 5
    thumb_w, thumb_h = 216, 384
    label_h = 34
    rows = (len(paths) + cols - 1) // cols
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


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []

    for frame in FRAMES:
        src = ASSET_DIR / frame["src"]
        out = OUT_DIR / frame["out"]
        img = cover_resize(Image.open(src)).convert("RGBA")
        add_readability_layer(img)
        draw_telop(img, frame["lines"], frame.get("y0"))
        img.convert("RGB").save(out, quality=95)
        outputs.append(out)

    make_contact_sheet(outputs)
    manifest = {
        "title": "検査のたびに名前や生年月日を聞かれるのはなぜ？",
        "size": {"width": W, "height": H},
        "font": str(FONT_PATH),
        "style": "white rounded rectangle, dark navy, short telop only",
        "source_dir": str(ASSET_DIR),
        "output_dir": str(OUT_DIR),
        "contact_sheet": str(CONTACT_SHEET),
        "frames": [
            {"source": f["src"], "output": f["out"], "telop": f["lines"]}
            for f in FRAMES
        ],
    }
    (OUT_DIR / "telop_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8-sig",
    )

    print(OUT_DIR)
    print(CONTACT_SHEET)


if __name__ == "__main__":
    main()
