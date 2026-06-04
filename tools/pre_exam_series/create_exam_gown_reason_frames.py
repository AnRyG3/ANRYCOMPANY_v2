from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(r"F:\ANRYCAMPANY")
SRC = ROOT / "reel_assets" / "pre_exam_series" / "04_exam_gown_reason" / "generated_backgrounds"
COMMON = ROOT / "reel_assets" / "common"
OUT = ROOT / "reel_assets" / "pre_exam_series" / "04_exam_gown_reason" / "final_text_frames"

W, H = 1080, 1920
FONT_BOLD = r"C:\Windows\Fonts\YuGothB.ttc"
FONT_REG = r"C:\Windows\Fonts\YuGothM.ttc"

NAVY = (7, 38, 58, 218)
NAVY_DARK = (3, 18, 31, 178)
WHITE = (255, 255, 255, 255)
YELLOW = (255, 216, 111, 255)


def font(size: int, bold: bool = True):
    path = FONT_BOLD if bold else FONT_REG
    if Path(path).exists():
        return ImageFont.truetype(path, size)
    return ImageFont.truetype(r"C:\Windows\Fonts\meiryob.ttc", size)


def cover(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")
    scale = max(W / img.width, H / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    return img.crop(((nw - W) // 2, (nh - H) // 2, (nw + W) // 2, (nh + H) // 2))


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, spacing: int = 18):
    box = draw.multiline_textbbox((0, 0), text, font=fnt, spacing=spacing, align="center")
    return box[2] - box[0], box[3] - box[1]


def fit_font(draw: ImageDraw.ImageDraw, text: str, max_w: int, max_h: int, start: int = 78, min_size: int = 46):
    for size in range(start, min_size - 1, -2):
        fnt = font(size, True)
        tw, th = text_size(draw, text, fnt)
        if tw <= max_w and th <= max_h:
            return fnt
    return font(min_size, True)


def add_top_readability(img: Image.Image) -> Image.Image:
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, W, 560), fill=(255, 255, 255, 24))
    draw.rectangle((0, 0, W, 420), fill=(0, 0, 0, 32))
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def draw_caption(img: Image.Image, lines: list[str], badge: str | None = None, accent: bool = False):
    text = "\n".join(lines)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Instagram UI避け: 最上部には置かず、顔より上の安全域に固定する。
    top = 250
    if badge:
        bf = font(34, True)
        bw = int(draw.textlength(badge, font=bf)) + 56
        bx = (W - bw) // 2
        draw.rounded_rectangle((bx, top, bx + bw, top + 58), radius=29, fill=(22, 116, 128, 235))
        draw.text((W // 2, top + 29), badge, font=bf, fill=WHITE, anchor="mm")
        top += 82

    max_w = 900
    max_h = 310 if len(lines) <= 2 else 380
    fnt = fit_font(draw, text, max_w - 100, max_h - 82, start=82 if len(lines) <= 2 else 70)
    tw, th = text_size(draw, text, fnt)
    pad_x, pad_y = 50, 34
    box_w = min(960, max(760, tw + pad_x * 2))
    box_h = th + pad_y * 2
    x1 = (W - box_w) // 2
    y1 = top
    x2 = x1 + box_w
    y2 = y1 + box_h

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x1 + 8, y1 + 10, x2 + 8, y2 + 10), radius=34, fill=(0, 0, 0, 72))
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    overlay = Image.alpha_composite(shadow, overlay)
    draw = ImageDraw.Draw(overlay)

    draw.rounded_rectangle((x1, y1, x2, y2), radius=34, fill=NAVY, outline=(255, 255, 255, 78), width=2)
    if accent:
        draw.rounded_rectangle((x1, y1, x1 + 18, y2), radius=9, fill=YELLOW)
    draw.multiline_text(
        (W // 2, y1 + pad_y - 4),
        text,
        font=fnt,
        fill=WHITE,
        anchor="ma",
        align="center",
        spacing=18,
        stroke_width=3,
        stroke_fill=(0, 0, 0, 110),
    )
    return Image.alpha_composite(img, overlay)


def draw_disclaimer(img: Image.Image):
    draw = ImageDraw.Draw(img)
    fnt = font(28, False)
    text = "※検査内容により対応は異なります"
    y = H - 70
    for dx, dy in ((2, 2), (-2, 2), (2, -2), (-2, -2)):
        draw.text((W // 2 + dx, y + dy), text, font=fnt, fill=(0, 0, 0, 150), anchor="mm")
    draw.text((W // 2, y), text, font=fnt, fill=(255, 255, 255, 238), anchor="mm")


def make_frame(bg_name: str, out_name: str, lines: list[str], duration: float, badge=None, accent=False):
    img = cover(Image.open(SRC / bg_name))
    img = add_top_readability(img)
    img = draw_caption(img, lines, badge=badge, accent=accent)
    img.convert("RGB").save(OUT / out_name, quality=95)
    return {
        "file": out_name,
        "background": bg_name,
        "text": lines,
        "duration_sec": duration,
        "text_position": "upper safe area, above faces",
    }


def copy_common_cta(out_name: str):
    img = cover(Image.open(COMMON / "reel_end_card_save.png"))
    img.save(OUT / out_name, quality=95)
    return {
        "file": out_name,
        "source": str(COMMON / "reel_end_card_save.png"),
        "text": ["保存CTA"],
        "duration_sec": 3.0,
        "text_position": "common CTA image",
    }


def create_contact_sheet(frame_files: list[str]):
    thumb_w, thumb_h = 270, 480
    cols = 4
    rows = math.ceil(len(frame_files) / cols)
    sheet = Image.new("RGB", (thumb_w * cols, thumb_h * rows), (28, 31, 33))
    draw = ImageDraw.Draw(sheet)
    label_font = font(22, True)
    for i, frame_file in enumerate(frame_files):
        img = Image.open(OUT / frame_file).convert("RGB")
        img.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (i % cols) * thumb_w
        y = (i // cols) * thumb_h
        sheet.paste(img, (x + (thumb_w - img.width) // 2, y + (thumb_h - img.height) // 2))
        draw.rectangle((x, y, x + 64, y + 34), fill=(10, 31, 36))
        draw.text((x + 12, y + 5), f"{i + 1:02d}", font=label_font, fill=WHITE)
    sheet.save(OUT / "_contact_sheet.png", quality=92)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    frames = [
        ("01_hook_no_metal.png", "01_hook.png", ["金具なしで", "大丈夫？"], 3.0, None, True),
        ("02_hidden_metal_parts.png", "02_hidden_metal.png", ["実は", "見落とす金具"], 3.0, None, True),
        ("02_hidden_metal_parts.png", "03_examples.png", ["ボタン", "ファスナー", "ホック"], 3.2, None, False),
        ("03_xray_artifacts.png", "04_artifact.png", ["画像に", "写ることも"], 3.0, None, False),
        ("04_thick_clothes_wrinkles.png", "05_wrinkles.png", ["厚手の服", "シワも影に"], 3.2, None, True),
        ("03_xray_artifacts.png", "06_overlap.png", ["見たい部分と", "重なることも"], 3.2, None, False),
        ("05_exam_gown_ready.png", "07_exam_gown.png", ["検査着は", "正確な検査のため"], 3.2, None, True),
        ("06_reassuring_closing.png", "08_reassurance.png", ["安心して", "受けてください"], 2.8, None, False),
        ("06_reassuring_closing.png", "09_fixed_ending.png", ["検査前の不安が減る情報を", "発信しています", "チャンネル登録しておくと", "次の検査のときに役立ちます"], 4.5, None, False),
    ]

    manifest = []
    frame_files = []
    for bg, out, lines, duration, badge, accent in frames:
        manifest.append(make_frame(bg, out, lines, duration, badge=badge, accent=accent))
        frame_files.append(out)
    manifest.append(copy_common_cta("10_common_save_cta.png"))
    frame_files.append("10_common_save_cta.png")

    (OUT / "frame_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    create_contact_sheet(frame_files)
    print(OUT)


if __name__ == "__main__":
    main()
