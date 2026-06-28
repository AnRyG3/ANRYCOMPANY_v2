from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "ct_series" / "ct_contrast_kidney_function_v1"
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
        "src": "s01_waiting_room_anxiety.png",
        "out": "s01_waiting_room_anxiety_telop.png",
        "lines": ["腎臓が悪いと", "造影剤は使えない？"],
        "box": (74, 140, 1006, 370),
    },
    {
        "src": "s02_concerned_closeup.png",
        "out": "s02_concerned_closeup_telop.png",
        "lines": ["検査できないの？", "と不安な方へ"],
        "box": (88, 140, 948, 370),
    },
    {
        "src": "s03_rt_tech_ct_room.png",
        "out": "s03_rt_tech_ct_room_telop.png",
        "lines": ["腎機能が低下しても", "使える場合があります"],
        "box": (58, 136, 1022, 370),
    },
    {
        "src": "s04_water_kidney_model.png",
        "out": "s04_water_kidney_model_telop.png",
        "lines": ["造影剤は腎臓から", "尿へ排泄されます"],
        "box": (70, 140, 1010, 370),
    },
    {
        "src": "s05_doctor_lab_result_explanation.png",
        "out": "s05_doctor_lab_result_explanation_telop.png",
        "lines": ["血液検査で", "腎機能を確認します"],
        "box": (104, 140, 920, 370),
    },
    {
        "src": "s06_iv_hydration_support.png",
        "out": "s06_iv_hydration_support_telop.png",
        "lines": ["状態に応じて", "対策をとります"],
        "box": (126, 140, 900, 370),
    },
    {
        "src": "s07_modern_ct_scanner.png",
        "out": "s07_modern_ct_scanner_telop.png",
        "lines": ["必要最小限の量を", "検討しやすく"],
        "box": (88, 140, 960, 370),
    },
    {
        "src": "s08_doctor_reviewing_chart.png",
        "out": "s08_doctor_reviewing_chart_telop.png",
        "lines": ["難しい場合も", "別の検査方法を検討"],
        "box": (78, 140, 1002, 370),
    },
    {
        "src": "s09_dialysis_patient.png",
        "out": "s09_dialysis_patient_telop.png",
        "lines": ["透析中も", "状態に合わせて判断"],
        "box": (102, 140, 936, 370),
    },
    {
        "src": "s10_team_support_corridor.png",
        "out": "s10_team_support_corridor_telop.png",
        "lines": ["何もできない、ではなく", "チームで考えます"],
        "box": (50, 136, 1030, 370),
    },
    {
        "src": "s11_cta_save_smartphone.png",
        "out": "s11_cta_save_smartphone_telop.png",
        "lines": ["保存して", "後で見返せます"],
        "box": (154, 140, 860, 370),
    },
    {
        "src": "s12_cta_follow_home_phone.png",
        "out": "s12_cta_follow_home_phone_telop.png",
        "lines": ["フォローして", "次の投稿も受け取る"],
        "box": (78, 140, 1002, 370),
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
    while size >= 44:
        font = choose_font(size, True)
        width, height, _ = text_size(draw, lines, font, spacing)
        if width <= max_w and height <= max_h:
            return font, spacing
        size -= 2
    return choose_font(44, True), 14


def draw_soft_safety_layers(img: Image.Image):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, W, 470), fill=(255, 255, 255, 18))
    draw.rectangle((0, H - 260, W, H), fill=(0, 0, 0, 24))
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
        "title": "腎機能が低下していると、造影剤は使えないの？",
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
