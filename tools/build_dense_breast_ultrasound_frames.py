from pathlib import Path
import json
import shutil

from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(r"F:\ANRYCAMPANY")
OUT_DIR = ROOT / "reel_assets" / "mammography_series" / "04_dense_breast_ultrasound_question"
BG_DIR = OUT_DIR / "generated_backgrounds"
FRAME_DIR = OUT_DIR / "final_text_frames"
COMMON_SAVE = ROOT / "reel_assets" / "common" / "reel_end_card_save.png"
PREV_BG_DIR = ROOT / "reel_assets" / "mammography_series" / "03_dense_breasts" / "generated_backgrounds"

W, H = 1080, 1920
FONT_BOLD = Path(r"C:\Windows\Fonts\BIZ-UDGothicB.ttc")
FONT_REG = Path(r"C:\Windows\Fonts\BIZ-UDGothicR.ttc")


frames = [
    {
        "text": ["高濃度乳房の方なら", "エコーを受ける？"],
        "bg": BG_DIR / "01_mammo_ultrasound_consult.png",
        "box_y": 300,
        "font": 64,
    },
    {
        "text": ["結論", "人によって違います"],
        "bg": PREV_BG_DIR / "03_consultation.png",
        "box_y": 310,
        "font": 60,
    },
    {
        "text": ["マンモで", "見えにくいことがあります"],
        "bg": PREV_BG_DIR / "02_density_display.png",
        "box_y": 285,
        "font": 54,
    },
    {
        "text": ["エコーが", "役立つことがあります"],
        "bg": BG_DIR / "01_mammo_ultrasound_consult.png",
        "box_y": 320,
        "font": 58,
    },
    {
        "text": ["でも", "エコーだけとは限りません"],
        "bg": BG_DIR / "01_mammo_ultrasound_consult.png",
        "box_y": 315,
        "font": 58,
    },
    {
        "text": ["マンモは", "石灰化や左右差が得意"],
        "bg": PREV_BG_DIR / "02_density_display.png",
        "box_y": 300,
        "font": 56,
    },
    {
        "text": ["エコーは", "しこりの性質が得意"],
        "bg": BG_DIR / "01_mammo_ultrasound_consult.png",
        "box_y": 320,
        "font": 56,
    },
    {
        "text": ["どちらか一つではなく", "目的で使い分けます"],
        "bg": PREV_BG_DIR / "03_consultation.png",
        "box_y": 315,
        "font": 54,
    },
    {
        "text": ["症状がある時は", "検診を待たず相談"],
        "bg": PREV_BG_DIR / "03_consultation.png",
        "box_y": 310,
        "font": 56,
    },
    {
        "text": ["検診結果で迷ったら", "医療機関に聞いて大丈夫"],
        "bg": PREV_BG_DIR / "03_consultation.png",
        "box_y": 305,
        "font": 52,
    },
    {
        "text": ["検査前の不安を", "安心に変える情報を発信中"],
        "bg": PREV_BG_DIR / "01_exam_room_density.png",
        "box_y": 310,
        "font": 54,
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


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont):
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def draw_caption(base: Image.Image, lines, y: int, font_size: int) -> Image.Image:
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = ImageFont.truetype(str(FONT_BOLD), font_size)
    line_gap = int(font_size * 0.35)
    widths = [text_size(draw, line, font)[0] for line in lines]
    heights = [text_size(draw, line, font)[1] for line in lines]
    text_w = max(widths)
    text_h = sum(heights) + line_gap * (len(lines) - 1)
    pad_x, pad_y = 52, 34
    box_w = min(W - 110, text_w + pad_x * 2)
    box_h = text_h + pad_y * 2
    x = (W - box_w) // 2
    radius = 24
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((x + 8, y + 8, x + box_w + 8, y + box_h + 8), radius=radius, fill=(30, 60, 80, 72))
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    overlay.alpha_composite(shadow)
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle((x, y, x + box_w, y + box_h), radius=radius, fill=(255, 255, 255, 238), outline=(226, 234, 238, 255), width=2)
    cy = y + pad_y
    for line, h in zip(lines, heights):
        tw, _ = text_size(draw, line, font)
        draw.text(((W - tw) // 2, cy), line, font=font, fill=(12, 55, 82))
        cy += h + line_gap
    return Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")


def make_contact_sheet(paths):
    thumb_w = 270
    thumb_h = 480
    cols = 4
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (thumb_w * cols, thumb_h * rows), (245, 248, 250))
    for i, path in enumerate(paths):
        img = Image.open(path).convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (i % cols) * thumb_w
        y = (i // cols) * thumb_h
        sheet.paste(img, (x, y))
    return sheet


def main():
    FRAME_DIR.mkdir(parents=True, exist_ok=True)
    output_paths = []

    for i, spec in enumerate(frames, start=1):
        base = fit_cover(Image.open(spec["bg"]))
        final = draw_caption(base, spec["text"], spec["box_y"], spec["font"])
        path = FRAME_DIR / f"frame_{i:02d}.png"
        final.save(path, "PNG", optimize=True)
        output_paths.append(path)

    frame_12 = FRAME_DIR / "frame_12.png"
    shutil.copy2(COMMON_SAVE, frame_12)
    output_paths.append(frame_12)

    contact = OUT_DIR / "_contact_sheet_final_text_frames.png"
    make_contact_sheet(output_paths).save(contact, "PNG", optimize=True)

    manifest = {
        "title": "高濃度乳房なら、エコーを受ければいい？",
        "asset_dir": str(OUT_DIR),
        "generated_backgrounds": [str(BG_DIR / "01_mammo_ultrasound_consult.png")],
        "final_text_frames": [str(p) for p in output_paths],
        "contact_sheet": str(contact),
        "size": {"width": W, "height": H},
    }
    (OUT_DIR / "frame_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(contact)


if __name__ == "__main__":
    main()
