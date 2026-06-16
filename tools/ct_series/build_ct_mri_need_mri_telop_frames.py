from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "ct_series" / "ct_mri_need_mri_v1"
IMAGE_DIR = ASSET_DIR / "images"
CHAR_DIR = ASSET_DIR / "images_with_characters"
OUT_DIR = ASSET_DIR / "telop_frames"
COMMON_DIR = ROOT / "reel_assets" / "common"

SIZE = (1080, 1920)
W, H = SIZE

FONT_BOLD = [
    r"C:\Windows\Fonts\YuGothB.ttc",
    r"C:\Windows\Fonts\NotoSansJP-VF.ttf",
    r"C:\Windows\Fonts\meiryob.ttc",
]
FONT_REG = [
    r"C:\Windows\Fonts\YuGothM.ttc",
    r"C:\Windows\Fonts\NotoSansJP-VF.ttf",
    r"C:\Windows\Fonts\meiryo.ttc",
]

NAVY = (12, 46, 78, 255)
WHITE_BOX = (255, 255, 255, 226)
ACCENT = (46, 119, 162, 255)


FRAMES = [
    {
        "src": IMAGE_DIR / "01_ct_mri_intro.png",
        "out": "01_ct_mri_intro_telop.png",
        "lines": ["CTを撮ったのに", "またMRI？"],
        "y": 300,
        "size": 92,
        "box": True,
    },
    {
        "src": CHAR_DIR / "02_question_corridor_patient.png",
        "out": "02_question_corridor_patient_telop.png",
        "lines": ["そう思うのは", "自然です"],
        "x": 690,
        "y": 360,
        "size": 76,
        "max_width": 620,
        "box": True,
    },
    {
        "src": IMAGE_DIR / "03_ct_mri_difference.png",
        "out": "03_ct_mri_difference_telop.png",
        "lines": ["CTとMRIは", "「見えるもの」が", "違う検査"],
        "y": 295,
        "size": 76,
        "box": True,
    },
    {
        "src": IMAGE_DIR / "04_ct_room.png",
        "out": "04_ct_room_telop.png",
        "title": "CTが得意なこと",
        "bullets": ["骨", "肺", "臓器の形", "全体を素早く確認"],
        "x": 520,
        "y": 380,
        "size": 58,
        "box": True,
    },
    {
        "src": IMAGE_DIR / "05_contrast_ct.png",
        "out": "05_contrast_ct_telop.png",
        "lines": ["造影CTでは", "血管を詳しく見ることも"],
        "y": 285,
        "size": 68,
        "box": True,
    },
    {
        "src": IMAGE_DIR / "06_mri_room.png",
        "out": "06_mri_room_telop.png",
        "title": "MRIが得意なこと",
        "bullets": ["神経・腱", "婦人科の臓器", "目立ちにくい骨折", "細かく確認"],
        "x": 455,
        "y": 415,
        "size": 52,
        "box": True,
    },
    {
        "src": IMAGE_DIR / "07_ct_overview.png",
        "out": "07_ct_overview_telop.png",
        "lines": ["CTで", "全体を見て"],
        "y": 315,
        "size": 86,
        "box": True,
    },
    {
        "src": IMAGE_DIR / "08_mri_detail.png",
        "out": "08_mri_detail_telop.png",
        "lines": ["MRIで", "気になる場所を", "詳しく見る"],
        "y": 290,
        "size": 78,
        "box": True,
    },
    {
        "src": CHAR_DIR / "09_waiting_anxiety_patient.png",
        "out": "09_waiting_anxiety_patient_telop.png",
        "lines": ["両方必要と言われると", "不安ですよね"],
        "x": 610,
        "y": 315,
        "size": 62,
        "max_width": 760,
        "box": True,
    },
    {
        "src": CHAR_DIR / "10_consultation_patient_rttech.png",
        "out": "10_consultation_patient_rttech_telop.png",
        "lines": ["理由が気になるときは", "聞いて大丈夫です"],
        "y": 245,
        "size": 62,
        "max_width": 820,
        "box": True,
    },
    {
        "src": None,
        "out": "11_fixed_message_telop.png",
        "lines": ["検査前の不安を", "安心に変える情報を発信中"],
        "y": 610,
        "size": 70,
        "box": False,
        "fixed_card": True,
    },
    {
        "src": COMMON_DIR / "reel_end_card_save.png",
        "out": "12_save_cta.png",
        "copy_only": True,
    },
]


def choose_font(size, bold=True):
    paths = FONT_BOLD if bold else FONT_REG
    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def cover_resize(img):
    img = img.convert("RGB")
    scale = max(W / img.width, H / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - W) // 2
    top = (nh - H) // 2
    return img.crop((left, top, left + W, top + H))


def fit_font(draw, lines, max_width, start_size, min_size=40):
    size = start_size
    while size >= min_size:
        font = choose_font(size, True)
        widths = [draw.textbbox((0, 0), line, font=font, stroke_width=3)[2] for line in lines]
        if max(widths) <= max_width:
            return font
        size -= 3
    return choose_font(min_size, True)


def draw_soft_vignette(img):
    overlay = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, W, 230), fill=(255, 255, 255, 28))
    draw.rectangle((0, H - 260, W, H), fill=(0, 0, 0, 34))
    img.alpha_composite(overlay)


def text_metrics(draw, lines, font, spacing):
    boxes = [draw.textbbox((0, 0), line, font=font, stroke_width=3) for line in lines]
    widths = [box[2] - box[0] for box in boxes]
    heights = [box[3] - box[1] for box in boxes]
    return max(widths), sum(heights) + spacing * (len(lines) - 1), heights


def draw_lines(img, lines, *, center_x=None, y=300, size=76, max_width=900, box=True):
    draw = ImageDraw.Draw(img, "RGBA")
    center_x = center_x or W // 2
    spacing = 18
    font = fit_font(draw, lines, max_width, size)
    text_w, text_h, heights = text_metrics(draw, lines, font, spacing)
    pad_x, pad_y = 52, 38
    x0 = center_x - text_w // 2 - pad_x
    x1 = center_x + text_w // 2 + pad_x
    y0 = y - pad_y
    y1 = y + text_h + pad_y
    if box:
        draw.rounded_rectangle((x0, y0, x1, y1), radius=34, fill=WHITE_BOX)
    yy = y
    for line, height in zip(lines, heights):
        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=3)
        line_w = bbox[2] - bbox[0]
        draw.text(
            (center_x - line_w // 2, yy),
            line,
            font=font,
            fill=NAVY,
            stroke_width=3,
            stroke_fill=(255, 255, 255, 255),
        )
        yy += height + spacing


def draw_bullet_box(img, title, bullets, *, center_x, y, size):
    draw = ImageDraw.Draw(img, "RGBA")
    title_font = choose_font(size, True)
    bullet_font = choose_font(size - 4, True)
    line_gap = 24
    title_box = draw.textbbox((0, 0), title, font=title_font, stroke_width=3)
    title_w = title_box[2] - title_box[0]
    bullet_boxes = [draw.textbbox((0, 0), bullet, font=bullet_font, stroke_width=3) for bullet in bullets]
    bullet_widths = [box[2] - box[0] for box in bullet_boxes]
    bullet_heights = [box[3] - box[1] for box in bullet_boxes]
    bullet_mark_w = 32
    content_w = max(title_w, max(bullet_widths) + bullet_mark_w + 20)
    content_h = (title_box[3] - title_box[1]) + 28 + sum(bullet_heights) + line_gap * (len(bullets) - 1)
    pad_x, pad_y = 54, 46
    x0 = center_x - content_w // 2 - pad_x
    x1 = center_x + content_w // 2 + pad_x
    y0 = y - pad_y
    y1 = y + content_h + pad_y
    draw.rounded_rectangle((x0, y0, x1, y1), radius=34, fill=WHITE_BOX)
    draw.text(
        (center_x - title_w // 2, y),
        title,
        font=title_font,
        fill=NAVY,
        stroke_width=3,
        stroke_fill=(255, 255, 255, 255),
    )
    accent_y = y + (title_box[3] - title_box[1]) + 18
    draw.rounded_rectangle((center_x - 155, accent_y, center_x + 155, accent_y + 8), radius=4, fill=ACCENT)
    yy = accent_y + 32
    text_x = center_x - content_w // 2 + 42
    for bullet, box, height in zip(bullets, bullet_boxes, bullet_heights):
        draw.ellipse((text_x - 34, yy + height // 2 - 9, text_x - 16, yy + height // 2 + 9), fill=ACCENT)
        draw.text(
            (text_x, yy),
            bullet,
            font=bullet_font,
            fill=NAVY,
            stroke_width=3,
            stroke_fill=(255, 255, 255, 255),
        )
        yy += height + line_gap


def make_fixed_card(lines):
    img = Image.new("RGBA", SIZE, (247, 250, 252, 255))
    draw = ImageDraw.Draw(img)
    for i in range(-H, W, 82):
        draw.line((i, 0, i + H, H), fill=(255, 255, 255, 180), width=9)
    draw.rounded_rectangle((96, 430, 984, 1250), radius=52, fill=(255, 255, 255, 235))
    draw.rounded_rectangle((96, 430, 984, 455), radius=8, fill=(82, 148, 184, 255))
    draw_lines(img, lines, center_x=W // 2, y=610, size=78, max_width=850, box=False)
    return img.convert("RGB")


def make_contact_sheet(paths):
    thumb_w, thumb_h = 216, 384
    label_h = 34
    cols = 4
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (thumb_w * cols, (thumb_h + label_h) * rows), (245, 247, 250))
    label_font = ImageFont.load_default()
    for idx, path in enumerate(paths):
        im = Image.open(path).convert("RGB")
        im.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), "white")
        tile.paste(im, ((thumb_w - im.width) // 2, 0))
        ImageDraw.Draw(tile).text((8, thumb_h + 10), path.name[:30], fill=(0, 0, 0), font=label_font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
    out = ASSET_DIR / "_contact_sheet_telop_frames.png"
    sheet.save(out)
    return out


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    for frame in FRAMES:
        out_path = OUT_DIR / frame["out"]
        if frame.get("copy_only"):
            img = cover_resize(Image.open(frame["src"]))
            img.save(out_path)
            outputs.append(out_path)
            continue
        if frame.get("fixed_card"):
            img = make_fixed_card(frame["lines"])
            img.save(out_path)
            outputs.append(out_path)
            continue

        img = cover_resize(Image.open(frame["src"])).convert("RGBA")
        draw_soft_vignette(img)
        if "title" in frame:
            draw_bullet_box(
                img,
                frame["title"],
                frame["bullets"],
                center_x=frame.get("x", W // 2),
                y=frame["y"],
                size=frame["size"],
            )
        else:
            draw_lines(
                img,
                frame["lines"],
                center_x=frame.get("x", W // 2),
                y=frame["y"],
                size=frame["size"],
                max_width=frame.get("max_width", 900),
                box=frame.get("box", True),
            )
        img.convert("RGB").save(out_path, quality=95)
        outputs.append(out_path)

    contact_sheet = make_contact_sheet(outputs)
    manifest = {
        "title": "CTを撮ったのに、なぜMRIも必要なの？",
        "asset_dir": str(ASSET_DIR),
        "telop_frames": [str(path) for path in outputs],
        "contact_sheet": str(contact_sheet),
        "size": {"width": W, "height": H},
    }
    (OUT_DIR / "frame_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(contact_sheet)


if __name__ == "__main__":
    main()
