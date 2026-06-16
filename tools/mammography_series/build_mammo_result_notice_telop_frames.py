from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "mammography_series" / "mammo_result_notice_v1"
BG_DIR = ASSET_DIR / "final_frames"
OUT_DIR = ASSET_DIR / "final_text_frames"
CONTACT_SHEET = ASSET_DIR / "_contact_sheet_final_text_frames.png"

W, H = 1080, 1920
FONT_BOLD = Path(r"C:\Windows\Fonts\BIZ-UDGothicB.ttc")
FONT_REG = Path(r"C:\Windows\Fonts\BIZ-UDGothicR.ttc")

NAVY = (12, 55, 82, 255)
WHITE_BOX = (255, 255, 255, 238)
BOX_OUTLINE = (226, 234, 238, 255)
SHADOW = (30, 60, 80, 70)
HOME_ACCENT = (179, 91, 112, 255)
CLINIC_ACCENT = (74, 134, 166, 255)


FRAMES = [
    {
        "lines": ["マンモの結果通知", "この言葉があったら受診"],
        "y": 245,
        "font": 64,
        "accent": HOME_ACCENT,
    },
    {
        "lines": ["「要精密検査」＝", "乳がん確定ではありません"],
        "y": 270,
        "font": 58,
        "accent": HOME_ACCENT,
    },
    {
        "lines": ["でも", "放置していい言葉でも", "ありません"],
        "y": 255,
        "font": 58,
        "accent": HOME_ACCENT,
    },
    {
        "lines": ["「要精検」と書かれていても", "同じ意味です"],
        "y": 270,
        "font": 56,
        "accent": CLINIC_ACCENT,
    },
    {
        "lines": ["症状がなくても", "精密検査を受けてください"],
        "y": 280,
        "font": 58,
        "accent": CLINIC_ACCENT,
    },
    {
        "lines": ["追加撮影や乳腺エコーなどで", "詳しく確認します"],
        "y": 250,
        "font": 54,
        "accent": CLINIC_ACCENT,
    },
    {
        "lines": ["「精密検査不要」でも", "症状があれば受診"],
        "y": 265,
        "font": 58,
        "accent": CLINIC_ACCENT,
    },
    {
        "lines": ["しこり・ひきつれ", "血が混じる分泌物は", "待たない"],
        "y": 250,
        "font": 56,
        "accent": CLINIC_ACCENT,
    },
    {
        "lines": ["「高濃度乳房」「石灰化」だけで", "自己判断しない"],
        "y": 260,
        "font": 52,
        "accent": CLINIC_ACCENT,
    },
    {
        "lines": ["迷ったら", "結果通知を持って", "医療機関へ"],
        "y": 250,
        "font": 60,
        "accent": CLINIC_ACCENT,
    },
    {
        "lines": ["結果が届いた時に", "見返せるように保存"],
        "y": 270,
        "font": 60,
        "accent": CLINIC_ACCENT,
    },
    {
        "lines": ["検査前後の不安を減らす", "情報を発信中"],
        "y": 285,
        "font": 60,
        "accent": CLINIC_ACCENT,
    },
]


def fit_cover(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")
    scale = max(W / img.width, H / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - W) // 2
    top = (nh - H) // 2
    return img.crop((left, top, left + W, top + H))


def font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REG), size=size)


def text_box(draw: ImageDraw.ImageDraw, lines, fnt, spacing):
    boxes = [draw.textbbox((0, 0), line, font=fnt, stroke_width=0) for line in lines]
    widths = [box[2] - box[0] for box in boxes]
    heights = [box[3] - box[1] for box in boxes]
    return max(widths), sum(heights) + spacing * (len(lines) - 1), heights


def fit_font(draw: ImageDraw.ImageDraw, lines, start_size: int, max_width: int):
    for size in range(start_size, 39, -2):
        fnt = font(size, True)
        spacing = int(size * 0.30)
        text_w, _, _ = text_box(draw, lines, fnt, spacing)
        if text_w <= max_width:
            return fnt, spacing
    size = 40
    return font(size, True), int(size * 0.30)


def draw_caption(base: Image.Image, spec: dict) -> Image.Image:
    base = base.convert("RGBA")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    lines = spec["lines"]
    fnt, spacing = fit_font(draw, lines, spec["font"], max_width=W - 180)
    text_w, text_h, heights = text_box(draw, lines, fnt, spacing)
    pad_x, pad_y = 46, 34
    box_w = min(W - 110, text_w + pad_x * 2)
    box_h = text_h + pad_y * 2
    x = (W - box_w) // 2
    y = spec["y"]
    radius = 24

    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(
        (x + 8, y + 8, x + box_w + 8, y + box_h + 8),
        radius=radius,
        fill=SHADOW,
    )
    overlay.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(8)))

    draw.rounded_rectangle(
        (x, y, x + box_w, y + box_h),
        radius=radius,
        fill=WHITE_BOX,
        outline=BOX_OUTLINE,
        width=2,
    )
    draw.rounded_rectangle(
        (x, y, x + 18, y + box_h),
        radius=9,
        fill=spec["accent"],
    )

    cy = y + pad_y
    for line, line_h in zip(lines, heights):
        bbox = draw.textbbox((0, 0), line, font=fnt, stroke_width=0)
        line_w = bbox[2] - bbox[0]
        draw.text(((W - line_w) // 2, cy), line, font=fnt, fill=NAVY)
        cy += line_h + spacing

    return Image.alpha_composite(base, overlay).convert("RGB")


def make_contact_sheet(paths):
    thumb_w, thumb_h = 270, 480
    cols = 4
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (thumb_w * cols, thumb_h * rows), (245, 248, 250))
    label_font = font(20, True)
    draw = ImageDraw.Draw(sheet)
    for idx, path in enumerate(paths):
        img = Image.open(path).convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (idx % cols) * thumb_w
        y = (idx // cols) * thumb_h
        sheet.paste(img, (x, y))
        draw.text((x + 8, y + 8), f"{idx + 1:02d}", font=label_font, fill=(40, 70, 90))
    return sheet


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []

    for idx, spec in enumerate(FRAMES, start=1):
        bg = BG_DIR / f"frame_{idx:02d}.png"
        if not bg.exists():
            raise FileNotFoundError(bg)
        final = draw_caption(fit_cover(Image.open(bg)), spec)
        out = OUT_DIR / f"final_{idx:02d}.png"
        final.save(out, "PNG", optimize=True)
        outputs.append(out)

    make_contact_sheet(outputs).save(CONTACT_SHEET, "PNG", optimize=True)

    manifest = {
        "title": "マンモの結果、何と書いてあったら受診が必要？",
        "asset_dir": str(ASSET_DIR),
        "background_frames": [str(BG_DIR / f"frame_{idx:02d}.png") for idx in range(1, 13)],
        "final_text_frames": [str(path) for path in outputs],
        "contact_sheet": str(CONTACT_SHEET),
        "size": {"width": W, "height": H},
        "text_policy": "No medical worker title on frames. Keep diagnosis wording non-definitive.",
    }
    (ASSET_DIR / "telop_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(CONTACT_SHEET)


if __name__ == "__main__":
    main()
