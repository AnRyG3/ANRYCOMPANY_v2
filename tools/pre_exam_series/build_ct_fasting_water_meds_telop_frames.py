from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "pre_exam_series" / "05_ct_fasting_water_meds_v1"
OUT = ASSET_DIR / "final_text_frames"

W, H = 1080, 1920
NAVY = (2, 24, 48, 255)
NAVY_SHADOW = (0, 0, 0, 58)
WHITE = (255, 255, 255, 255)
PANEL = (255, 255, 255, 238)
PANEL_EDGE = (2, 24, 48, 210)
ACCENT = (255, 216, 111, 255)


def font(size: int, bold: bool = True):
    candidates = [
        r"C:\Windows\Fonts\BIZ-UDGothicB.ttc" if bold else r"C:\Windows\Fonts\BIZ-UDGothicR.ttc",
        r"C:\Windows\Fonts\YuGothB.ttc" if bold else r"C:\Windows\Fonts\YuGothM.ttc",
        r"C:\Windows\Fonts\NotoSansJP-VF.ttf",
        r"C:\Windows\Fonts\meiryob.ttc" if bold else r"C:\Windows\Fonts\meiryo.ttc",
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def cover(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")
    scale = max(W / img.width, H / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    return img.crop(((nw - W) // 2, (nh - H) // 2, (nw + W) // 2, (nh + H) // 2))


def text_box_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, spacing: int):
    box = draw.multiline_textbbox((0, 0), text, font=fnt, spacing=spacing, align="center")
    return box[2] - box[0], box[3] - box[1]


def fit_font(draw: ImageDraw.ImageDraw, text: str, max_w: int, max_h: int, start: int = 78, minimum: int = 42):
    for size in range(start, minimum - 1, -2):
        fnt = font(size, True)
        tw, th = text_box_size(draw, text, fnt, 18)
        if tw <= max_w and th <= max_h:
            return fnt
    return font(minimum, True)


def add_readability(img: Image.Image) -> Image.Image:
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, W, 610), fill=(0, 0, 0, 20))
    draw.rectangle((0, H - 390, W, H), fill=(0, 0, 0, 24))
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def draw_telop(img: Image.Image, lines: list[str], y: int = 245, accent: bool = False) -> Image.Image:
    text = "\n".join(lines)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    draw = ImageDraw.Draw(overlay)

    max_w = 920
    max_h = 300
    fnt = fit_font(draw, text, max_w - 104, max_h - 76, start=96 if len(lines) <= 2 else 84)
    tw, th = text_box_size(draw, text, fnt, 18)
    pad_x, pad_y = 54, 34
    box_w = min(972, max(730, tw + pad_x * 2))
    box_h = th + pad_y * 2
    x1 = (W - box_w) // 2
    y1 = y
    x2 = x1 + box_w
    y2 = y1 + box_h

    sd.rounded_rectangle((x1 + 10, y1 + 12, x2 + 10, y2 + 12), radius=30, fill=NAVY_SHADOW)
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    overlay = Image.alpha_composite(shadow, overlay)
    draw = ImageDraw.Draw(overlay)

    draw.rounded_rectangle((x1, y1, x2, y2), radius=30, fill=PANEL, outline=PANEL_EDGE, width=4)
    if accent:
        draw.rounded_rectangle((x1, y1, x1 + 18, y2), radius=9, fill=ACCENT)
    text_pos = (W // 2, y1 + pad_y - 5)
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        draw.multiline_text(
            (text_pos[0] + dx, text_pos[1] + dy),
            text,
            font=fnt,
            fill=NAVY,
            anchor="ma",
            align="center",
            spacing=18,
        )
    draw.multiline_text(
        text_pos,
        text,
        font=fnt,
        fill=NAVY,
        anchor="ma",
        align="center",
        spacing=18,
        stroke_width=1,
        stroke_fill=NAVY,
    )
    return Image.alpha_composite(img, overlay)


def make_contact_sheet(frame_files: list[str]):
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
        ("sample_s01_reception.png", "01_reception.png", ["絶食は", "なぜ必要？"], 3.2, True, 245),
        ("sample_s02_reading.png", "02_reassure.png", ["理由がわかると", "安心できます"], 3.0, False, 245),
        ("sample_s03_ct_contrast_prep.png", "03_contrast_nausea.png", ["造影剤で", "気分不快が起こることも"], 4.0, False, 245),
        ("sample_s04_safety_iv_scene.png", "04_airway_risk.png", ["嘔吐した時の", "誤嚥を防ぐため"], 4.2, True, 245),
        ("sample_s05_waiting_ready.png", "05_for_safety.png", ["安全のための", "準備です"], 2.6, True, 245),
        ("sample_s06_water_explain.png", "06_water_depends.png", ["水分の指示は", "検査で変わります"], 3.2, False, 245),
        ("sample_s07_asking_staff.png", "07_ask_water.png", ["水分は飲んでいい？", "確認して大丈夫"], 3.6, False, 245),
        ("sample_s08_home_medicine_water.png", "08_medicine_water.png", ["普段の薬は", "事前に確認"], 4.0, False, 110),
        ("sample_s09_medicine_notebook_unsure.png", "09_medicine_separate.png", ["薬と食事の指示は", "別物です"], 4.0, True, 110),
        ("sample_s10_instruction_paper.png", "10_follow_instruction.png", ["絶食時間は", "施設で異なります"], 3.4, False, 245),
        ("sample_s11_question_reassurance.png", "11_ask_before_exam.png", ["不安なことは", "検査前に確認を"], 3.2, False, 245),
        ("sample_s12_cta_smartphone.png", "12_save_follow.png", ["保存とフォローで", "次の解説も"], 4.0, True, 245),
    ]

    manifest = []
    output_files = []
    for src_name, out_name, lines, duration, accent, y in frames:
        img = cover(Image.open(ASSET_DIR / src_name))
        img = add_readability(img)
        img = draw_telop(img, lines, y=y, accent=accent)
        img.convert("RGB").save(OUT / out_name, quality=95)
        output_files.append(out_name)
        manifest.append(
            {
                "file": out_name,
                "source": src_name,
                "text": lines,
                "duration_sec": duration,
                "text_position": "upper safe area",
            }
        )

    (OUT / "frame_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    make_contact_sheet(output_files)
    print(OUT)


if __name__ == "__main__":
    main()
