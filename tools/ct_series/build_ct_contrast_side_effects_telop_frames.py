from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "ct_series" / "ct_contrast_side_effects_v1"
OUT_DIR = ASSET_DIR / "telop_frames"
CONTACT_SHEET = ASSET_DIR / "contact_sheet_telop_frames.png"

W, H = 1080, 1920
NAVY = (10, 45, 86, 255)
WHITE = (255, 255, 255, 242)
WHITE_SOLID = (255, 255, 255, 255)
SHADOW = (20, 30, 40, 70)

FONT_BOLD = [
    r"C:\Windows\Fonts\YuGothB.ttc",
    r"C:\Windows\Fonts\meiryob.ttc",
    r"C:\Windows\Fonts\NotoSansJP-Bold.otf",
    r"C:\Windows\Fonts\NotoSansJP-VF.ttf",
]
FONT_REG = [
    r"C:\Windows\Fonts\YuGothM.ttc",
    r"C:\Windows\Fonts\meiryo.ttc",
    r"C:\Windows\Fonts\NotoSansJP-Regular.otf",
    r"C:\Windows\Fonts\NotoSansJP-VF.ttf",
]


FRAMES = [
    {
        "src": "sample_s01_home_anxiety.png",
        "out": "s01_home_anxiety_telop.png",
        "lines": ["造影剤が", "怖い方へ"],
        "box": (92, 150, 720, 370),
    },
    {
        "src": "s02_reassurance_home.png",
        "out": "s02_reassurance_home_telop.png",
        "lines": ["不安になるのは", "自然です"],
        "box": (92, 150, 820, 370),
    },
    {
        "src": "s03_ct_room_overview.png",
        "out": "s03_ct_room_overview_telop.png",
        "lines": ["副作用には", "軽いものと重いもの"],
        "box": (92, 145, 950, 365),
    },
    {
        "src": "s04_iv_preparation.png",
        "out": "s04_iv_preparation_telop.png",
        "lines": ["軽い副作用", "吐き気・かゆみ・発疹"],
        "box": (84, 140, 996, 365),
    },
    {
        "src": "s05_staff_monitoring_patient.png",
        "out": "s05_staff_monitoring_patient_telop.png",
        "lines": ["重い副作用", "呼吸困難・血圧低下など"],
        "box": (74, 140, 1006, 365),
    },
    {
        "src": "s06_control_room_monitoring.png",
        "out": "s06_control_room_monitoring_telop.png",
        "lines": ["万が一に備えて", "確認しています"],
        "box": (88, 140, 930, 365),
    },
    {
        "src": "sample_s07_pre_exam_interview.png",
        "out": "s07_pre_exam_interview_telop.png",
        "lines": ["アレルギーやぜんそくは", "事前に相談"],
        "box": (64, 138, 1016, 365),
    },
    {
        "src": "s08_questionnaire_closeup.png",
        "out": "s08_questionnaire_closeup_telop.png",
        "lines": ["問診票は", "安全確認のため"],
        "box": (92, 140, 870, 360),
    },
    {
        "src": "s09_after_exam_phone_call.png",
        "out": "s09_after_exam_phone_call_telop.png",
        "lines": ["検査後の症状は", "医療機関へ連絡"],
        "box": (88, 140, 930, 365),
    },
    {
        "src": "s10_calm_after_understanding.png",
        "out": "s10_calm_after_understanding_telop.png",
        "lines": ["知ることが", "安心につながる"],
        "box": (92, 140, 890, 365),
    },
    {
        "src": "s11_pre_exam_staff_reassurance.png",
        "out": "s11_pre_exam_staff_reassurance_telop.png",
        "lines": ["あなたの安全のために", "準備しています"],
        "box": (72, 138, 1008, 365),
    },
    {
        "src": "s12_cta_smartphone.png",
        "out": "s12_cta_smartphone_telop.png",
        "lines": ["保存・フォローで", "次の解説へ"],
        "box": (92, 140, 920, 365),
    },
]


def choose_font(size: int, bold: bool = True):
    for path in FONT_BOLD if bold else FONT_REG:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def cover_resize(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")
    scale = max(W / img.width, H / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - W) // 2
    top = (nh - H) // 2
    return resized.crop((left, top, left + W, top + H))


def text_size(draw: ImageDraw.ImageDraw, lines, font, spacing):
    boxes = [draw.textbbox((0, 0), line, font=font) for line in lines]
    widths = [box[2] - box[0] for box in boxes]
    heights = [box[3] - box[1] for box in boxes]
    return max(widths), sum(heights) + spacing * (len(lines) - 1), heights


def fit_font(draw: ImageDraw.ImageDraw, lines, max_w: int, max_h: int):
    size = 82
    spacing = 18
    while size >= 46:
        font = choose_font(size, True)
        width, height, _ = text_size(draw, lines, font, spacing)
        if width <= max_w and height <= max_h:
            return font, spacing
        size -= 2
    return choose_font(46, True), 14


def draw_soft_safety_layers(img: Image.Image):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, W, 470), fill=(255, 255, 255, 18))
    draw.rectangle((0, H - 260, W, H), fill=(0, 0, 0, 26))
    img.alpha_composite(overlay)


def draw_telop(img: Image.Image, frame: dict):
    x0, y0, x1, y1 = frame["box"]
    lines = frame["lines"]
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((x0 + 10, y0 + 12, x1 + 10, y1 + 12), radius=36, fill=SHADOW)
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(12)))

    draw = ImageDraw.Draw(img, "RGBA")
    draw.rounded_rectangle((x0, y0, x1, y1), radius=34, fill=WHITE)
    draw.rounded_rectangle((x0 + 10, y0 + 10, x1 - 10, y1 - 10), radius=26, outline=WHITE_SOLID, width=6)

    font, spacing = fit_font(draw, lines, (x1 - x0) - 92, (y1 - y0) - 74)
    _, total_h, heights = text_size(draw, lines, font, spacing)
    yy = y0 + ((y1 - y0) - total_h) // 2 - 4
    for line, line_h in zip(lines, heights):
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        draw.text(
            ((x0 + x1 - line_w) // 2, yy),
            line,
            font=font,
            fill=NAVY,
        )
        yy += line_h + spacing


def make_contact_sheet(paths: list[Path]):
    cols = 4
    thumb_w, thumb_h = 216, 384
    label_h = 36
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (245, 247, 250))
    label_font = ImageFont.load_default()
    for idx, path in enumerate(paths):
        img = Image.open(path).convert("RGB")
        img.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), "white")
        tile.paste(img, ((thumb_w - img.width) // 2, 0))
        ImageDraw.Draw(tile).text((8, thumb_h + 10), path.name[:32], fill=(0, 0, 0), font=label_font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
    sheet.save(CONTACT_SHEET, quality=94)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    for frame in FRAMES:
        src = ASSET_DIR / frame["src"]
        out = OUT_DIR / frame["out"]
        img = cover_resize(Image.open(src)).convert("RGBA")
        draw_soft_safety_layers(img)
        draw_telop(img, frame)
        img.convert("RGB").save(out, quality=95)
        outputs.append(out)

    make_contact_sheet(outputs)
    manifest = {
        "title": "造影剤の副作用やアレルギーが怖いのですが大丈夫？",
        "size": {"width": W, "height": H},
        "style": "white rounded frame, navy bold key text",
        "asset_dir": str(ASSET_DIR),
        "output_dir": str(OUT_DIR),
        "contact_sheet": str(CONTACT_SHEET),
        "frames": [
            {"source": frame["src"], "output": str(OUT_DIR / frame["out"]), "telop": frame["lines"]}
            for frame in FRAMES
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
