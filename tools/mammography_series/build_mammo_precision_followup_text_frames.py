from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "mammography_series" / "mammo_result_notice_v1"
SAMPLE_DIR = ASSET_DIR / "samples"
OUT_DIR = ASSET_DIR / "final_text_frames_precision_followup_20260623"
CONTACT_SHEET = ASSET_DIR / "_contact_sheet_precision_followup_text_20260623.png"
MANIFEST = ASSET_DIR / "telop_manifest_precision_followup_20260623.json"

W, H = 1080, 1920
FONT_BOLD = Path(r"C:\Windows\Fonts\BIZ-UDGothicB.ttc")
FONT_FALLBACK_BOLD = Path(r"C:\Windows\Fonts\YuGothB.ttc")
FONT_REG = Path(r"C:\Windows\Fonts\YuGothM.ttc")

NAVY = (4, 32, 52, 255)
ACCENT_HOME = (176, 94, 118, 255)
ACCENT_CLINIC = (48, 112, 145, 255)
ACCENT_CTA = (30, 102, 120, 255)
WHITE_BOX = (255, 255, 255, 247)
PAPER_WHITE = (255, 255, 255, 242)
OUTLINE = (214, 225, 232, 255)
SHADOW = (20, 40, 58, 90)


FRAMES = [
    {
        "bg": "sample_s1_review_20260623_v2.png",
        "lines": ["マンモで", "要精密検査？"],
        "y": 1130,
        "font": 86,
        "accent": ACCENT_HOME,
    },
    {
        "bg": "sample_s2_review_20260623.png",
        "lines": ["がん確定では", "ありません"],
        "y": 1130,
        "font": 84,
        "accent": ACCENT_HOME,
    },
    {
        "bg": "sample_s3_review_20260623.png",
        "lines": ["詳しく見ましょう", "という案内です"],
        "y": 1130,
        "font": 76,
        "accent": ACCENT_HOME,
        "paper_label": "要精密検査",
    },
    {
        "bg": "sample_s4_review_20260623.png",
        "lines": ["カテゴリー3は", "念のため確認"],
        "y": 1130,
        "font": 82,
        "accent": ACCENT_CLINIC,
        "paper_label": "カテゴリー3",
    },
    {
        "bg": "sample_s5_review_20260623.png",
        "lines": ["次は", "乳腺外来へ受診"],
        "y": 1130,
        "font": 88,
        "accent": ACCENT_CLINIC,
    },
    {
        "bg": "sample_s6_review_20260623.png",
        "lines": ["乳腺エコーなどで", "詳しく確認します"],
        "y": 245,
        "font": 76,
        "accent": ACCENT_CLINIC,
    },
    {
        "bg": "sample_s7_review_20260623.png",
        "lines": ["同じエコーでも", "目的が違うことがあります"],
        "y": 245,
        "font": 76,
        "accent": ACCENT_CLINIC,
    },
    {
        "bg": "sample_s8_review_20260623.png",
        "lines": ["不安になるのは", "自然なことです"],
        "y": 255,
        "font": 82,
        "accent": ACCENT_CLINIC,
    },
    {
        "bg": "sample_s9_review_20260623.png",
        "lines": ["検査前の不安を", "安心に変える情報を発信中"],
        "y": 805,
        "font": 78,
        "accent": ACCENT_CTA,
    },
    {
        "bg": "sample_s10_review_20260623.png",
        "lines": ["あとで見返せるように", "保存しておいてください"],
        "y": 650,
        "font": 82,
        "accent": ACCENT_CTA,
    },
]


def font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    path = FONT_BOLD if bold and FONT_BOLD.exists() else FONT_FALLBACK_BOLD
    if not bold:
        path = FONT_REG
    return ImageFont.truetype(str(path), size=size)


def fit_cover(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")
    scale = max(W / img.width, H / img.height)
    nw, nh = round(img.width * scale), round(img.height * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - W) // 2
    top = (nh - H) // 2
    return img.crop((left, top, left + W, top + H))


def text_metrics(draw: ImageDraw.ImageDraw, lines, fnt, spacing):
    boxes = [draw.textbbox((0, 0), line, font=fnt, stroke_width=1) for line in lines]
    widths = [box[2] - box[0] for box in boxes]
    heights = [box[3] - box[1] for box in boxes]
    return max(widths), sum(heights) + spacing * (len(lines) - 1), heights, boxes


def fit_font(draw: ImageDraw.ImageDraw, lines, start_size: int, max_width: int):
    for size in range(start_size, 43, -2):
        fnt = font(size, True)
        spacing = int(size * 0.28)
        text_w, _, _, _ = text_metrics(draw, lines, fnt, spacing)
        if text_w <= max_width:
            return fnt, spacing
    return font(44, True), 12


def draw_caption(base: Image.Image, spec: dict) -> Image.Image:
    base = base.convert("RGBA")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    lines = spec["lines"]
    fnt, spacing = fit_font(draw, lines, spec["font"], W - 165)
    text_w, text_h, heights, boxes = text_metrics(draw, lines, fnt, spacing)
    pad_x, pad_y = 44, 32
    box_w = min(W - 95, text_w + pad_x * 2)
    box_h = text_h + pad_y * 2
    x = (W - box_w) // 2
    y = spec["y"]

    shadow_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)
    shadow_draw.rounded_rectangle(
        (x + 8, y + 10, x + box_w + 8, y + box_h + 10),
        radius=24,
        fill=SHADOW,
    )
    overlay.alpha_composite(shadow_layer.filter(ImageFilter.GaussianBlur(8)))

    draw.rounded_rectangle(
        (x, y, x + box_w, y + box_h),
        radius=24,
        fill=WHITE_BOX,
        outline=OUTLINE,
        width=2,
    )
    draw.rounded_rectangle((x, y, x + 18, y + box_h), radius=9, fill=spec["accent"])

    cy = y + pad_y
    for line, height, box in zip(lines, heights, boxes):
        line_w = box[2] - box[0]
        draw.text(
            ((W - line_w) // 2, cy),
            line,
            font=fnt,
            fill=NAVY,
            stroke_width=1,
            stroke_fill=NAVY,
        )
        cy += height + spacing

    return Image.alpha_composite(base, overlay).convert("RGBA")


def draw_document_label(img: Image.Image, spec: dict) -> Image.Image:
    draw = ImageDraw.Draw(img, "RGBA")
    for poly in spec.get("cover_polys", []):
        draw.polygon(poly, fill=(245, 232, 236, 244))
    if "paper_label" in spec:
        text = spec["paper_label"]
        fnt = font(52, True)
        draw.rounded_rectangle((300, 642, 780, 728), radius=8, fill=PAPER_WHITE, outline=(185, 195, 202, 255), width=2)
        bbox = draw.textbbox((0, 0), text, font=fnt, stroke_width=1)
        draw.text(
            ((W - (bbox[2] - bbox[0])) // 2, 654),
            text,
            font=fnt,
            fill=NAVY,
            stroke_width=1,
            stroke_fill=NAVY,
        )
    return img


def make_contact_sheet(paths):
    thumb_w, thumb_h = 270, 480
    cols = 5
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (thumb_w * cols, thumb_h * rows), (245, 248, 250))
    label_font = font(20, True)
    draw = ImageDraw.Draw(sheet)
    for idx, path in enumerate(paths):
        img = Image.open(path).convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (idx % cols) * thumb_w
        y = (idx // cols) * thumb_h
        sheet.paste(img, (x, y))
        draw.text((x + 8, y + 8), f"S{idx + 1}", font=label_font, fill=NAVY)
    return sheet


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    for idx, spec in enumerate(FRAMES, start=1):
        bg_path = SAMPLE_DIR / spec["bg"]
        if not bg_path.exists():
            raise FileNotFoundError(bg_path)
        img = fit_cover(Image.open(bg_path))
        img = draw_document_label(img.convert("RGBA"), spec)
        img = draw_caption(img, spec).convert("RGB")
        out = OUT_DIR / f"frame_{idx:02d}.png"
        img.save(out, "PNG", optimize=True)
        outputs.append(out)

    make_contact_sheet(outputs).save(CONTACT_SHEET, "PNG", optimize=True)
    manifest = {
        "title": "マンモで要精密検査、次に何をする？",
        "asset_dir": str(ASSET_DIR),
        "background_frames": [str(SAMPLE_DIR / spec["bg"]) for spec in FRAMES],
        "final_text_frames": [str(path) for path in outputs],
        "contact_sheet": str(CONTACT_SHEET),
        "size": {"width": W, "height": H},
        "text_policy": "Shorter bold text. S1 paper label removed. S10 centered.",
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(CONTACT_SHEET)


if __name__ == "__main__":
    main()
