from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(r"F:\ANRYCAMPANY")
SRC = ROOT / "reel_assets" / "pre_exam_series" / "01_day_before" / "generated_images"
COMMON = ROOT / "reel_assets" / "common"
OUT_ROOT = ROOT / "reel_assets" / "pre_exam_series" / "02_fasting_why"
OUT_BG = OUT_ROOT / "backgrounds"
OUT = OUT_ROOT / "final_text_frames"

W, H = 1080, 1920


def font(size, bold=False):
    candidates = [
        r"C:\Windows\Fonts\YuGothB.ttc" if bold else r"C:\Windows\Fonts\YuGothR.ttc",
        r"C:\Windows\Fonts\meiryob.ttc" if bold else r"C:\Windows\Fonts\meiryo.ttc",
        r"C:\Windows\Fonts\msgothic.ttc",
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


FONT_TITLE = font(86, True)
FONT_MAIN = font(76, True)
FONT_SUB = font(42, False)
FONT_SMALL = font(34, False)


def cover(img):
    img = img.convert("RGB")
    scale = max(W / img.width, H / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - W) // 2
    top = (nh - H) // 2
    return img.crop((left, top, left + W, top + H))


def overlay_scrim(img, strength=138):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, strength))
    grad = Image.new("L", (1, H))
    px = grad.load()
    for y in range(H):
        v = int(70 + 120 * abs((y / H) - 0.5) * 1.4)
        px[0, y] = min(190, v)
    grad = grad.resize((W, H))
    vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vignette.putalpha(grad)
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGBA")


def rounded_rect(draw, xy, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def text_size(draw, text, fnt):
    box = draw.multiline_textbbox((0, 0), text, font=fnt, spacing=16, align="center")
    return box[2] - box[0], box[3] - box[1]


def draw_center_text(img, title, subtitle=None, badge=None, y=740):
    draw = ImageDraw.Draw(img)
    if badge:
        bf = FONT_SMALL
        bw = int(draw.textlength(badge, font=bf)) + 54
        bx = (W - bw) // 2
        by = y - 118
        rounded_rect(draw, (bx, by, bx + bw, by + 54), 27, (18, 111, 123, 220))
        draw.text((W // 2, by + 27), badge, font=bf, fill=(255, 255, 255, 255), anchor="mm")

    tw, th = text_size(draw, title, FONT_TITLE if "\n" in title and len(title) < 18 else FONT_MAIN)
    pad_x, pad_y = 58, 42
    x1 = max(64, (W - tw) // 2 - pad_x)
    x2 = min(W - 64, (W + tw) // 2 + pad_x)
    y1 = y - pad_y
    y2 = y + th + pad_y
    rounded_rect(draw, (x1, y1, x2, y2), 34, (12, 36, 43, 205), (255, 255, 255, 70), 2)
    draw.multiline_text((W // 2, y), title, font=FONT_TITLE if "\n" in title and len(title) < 18 else FONT_MAIN,
                        fill=(255, 255, 255, 255), anchor="ma", spacing=16, align="center",
                        stroke_width=3, stroke_fill=(0, 0, 0, 110))
    if subtitle:
        draw.multiline_text((W // 2, y2 + 54), subtitle, font=FONT_SUB, fill=(255, 255, 255, 238),
                            anchor="ma", spacing=12, align="center",
                            stroke_width=2, stroke_fill=(0, 0, 0, 120))


def draw_number_pill(img, num, label):
    draw = ImageDraw.Draw(img)
    x, y = 84, 310
    rounded_rect(draw, (x, y, x + 190, y + 74), 37, (244, 176, 68, 238))
    draw.text((x + 95, y + 37), f"{num}つ目", font=FONT_SUB, fill=(20, 36, 38), anchor="mm")
    draw.text((84, 425), label, font=FONT_TITLE, fill=(255, 255, 255), anchor="la",
              stroke_width=3, stroke_fill=(0, 0, 0, 120))


def make_frame(source, out_name, title, subtitle=None, badge=None, y=760, number=None, reason_label=None):
    img = cover(Image.open(source))
    img = overlay_scrim(img)
    if number:
        draw_number_pill(img, number, reason_label)
        draw_center_text(img, title, subtitle, None, y=y)
    else:
        draw_center_text(img, title, subtitle, badge, y=y)
    img.convert("RGB").save(OUT / out_name, quality=95)


def copy_cover(source, out_name):
    img = cover(Image.open(source))
    img.save(OUT / out_name, quality=95)


def create_contact_sheet(frame_files):
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
        draw.text((x + 12, y + 5), f"{i + 1:02d}", font=label_font, fill=(255, 255, 255))
    sheet.save(OUT / "_contact_sheet.png", quality=92)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    OUT_BG.mkdir(parents=True, exist_ok=True)

    sources_to_copy = {
        "00_character_reference.png": SRC / "00_character_reference.png",
        "01_opening_night_phone.png": SRC / "01_opening_night_phone.png",
        "04_food_water_check.png": SRC / "04_food_water_check.png",
        "07_sofa_relief.png": SRC / "07_sofa_relief.png",
        "reel_end_card_save.png": COMMON / "reel_end_card_save.png",
    }
    for name, src in sources_to_copy.items():
        if src.exists():
            cover(Image.open(src)).save(OUT_BG / name, quality=95)

    frames = [
        ("01_hook.png", SRC / "00_character_reference.png", "検査前の絶食\nなんで必要？", None, None, 1160, None, None, 4.0),
        ("02_empathy.png", SRC / "01_opening_night_phone.png", "つらいですよね", "でも、ただ我慢させたい\nわけではありません", None, 1080, None, None, 3.5),
        ("03_radiographer.png", SRC / "07_sofa_relief.png", "現場の放射線技師が\n説明します", None, None, 1080, None, None, 3.5),
        ("04_three_reasons.png", SRC / "00_character_reference.png", "理由は大きく\n3つあります", None, None, 1160, None, None, 3.0),
        ("05_reason_image.png", SRC / "04_food_water_check.png", "画像に影響が\n出るから", "食後は胃や腸が動きます", None, 1120, 1, "画像への影響", 4.5),
        ("06_gas_contents.png", SRC / "04_food_water_check.png", "ガスや内容物が\n写り込むことも", None, None, 1120, None, None, 4.0),
        ("07_reason_contrast.png", SRC / "00_character_reference.png", "造影剤検査の\n備え", "気分が悪くなった時に備えます", None, 1120, 2, "造影剤検査", 4.5),
        ("08_nausea.png", SRC / "00_character_reference.png", "吐き気などは\nゼロではありません", None, None, 1120, None, None, 4.5),
        ("09_reason_gallbladder.png", SRC / "04_food_water_check.png", "胆のうを\nきれいに見るため", "食後は胆のうが縮むことがあります", None, 1120, 3, "エコー検査", 4.5),
        ("10_depends_exam.png", SRC / "07_sofa_relief.png", "絶食が必要かは\n検査で違います", "案内用紙をまず確認", None, 1080, None, None, 4.0),
        ("11_ask_staff.png", SRC / "07_sofa_relief.png", "迷ったことは\n病院に聞いて大丈夫", "絶食できたか不安なら\n検査前にスタッフへ", None, 1080, None, None, 5.0),
        ("12_common_end.png", COMMON / "reel_end_card_save.png", None, None, None, 0, None, None, 3.0),
        ("13_next_episode.png", SRC / "07_sofa_relief.png", "次回\n当日の持ち物と\n確認リスト", None, None, 1080, None, None, 3.0),
    ]

    manifest = []
    frame_files = []
    for out_name, src, title, subtitle, badge, y, number, reason_label, duration in frames:
        if title is None:
            copy_cover(src, out_name)
        else:
            make_frame(src, out_name, title, subtitle, badge, y, number, reason_label)
        frame_files.append(out_name)
        manifest.append({
            "file": out_name,
            "source": str(src),
            "caption": title.replace("\n", " / ") if title else "あとで見返せるように 保存して また見よう",
            "duration_sec": duration,
        })

    (OUT / "frame_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    create_contact_sheet(frame_files)


if __name__ == "__main__":
    main()
