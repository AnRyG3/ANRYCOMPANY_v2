from pathlib import Path
import json
import shutil

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "echo_series" / "03_pain_fear"
BG_DIR = ASSET_DIR / "generated_backgrounds_v2"
OUT_DIR = ASSET_DIR / "final_text_frames_v2_varied"
CTA = ROOT / "reel_assets" / "common" / "reel_end_card_save.png"

SIZE = (1080, 1920)

TEXTS = [
    ["エコー検査", "痛い？怖い？"],
    ["はじめてだと", "不安になりますよね"],
    ["基本的には", "強い痛みを伴う", "検査ではありません"],
    ["体に器具を当てて", "音で中を確認します"],
    ["ただし", "少し押される感覚は", "あります"],
    ["画像を見えやすくするために", "向きや強さを", "調整します"],
    ["もともと痛い場所では", "押されたときに", "痛むこともあります"],
    ["そのときは", "我慢しなくて", "大丈夫です"],
    ["不安を伝えることは", "検査の迷惑では", "ありません"],
    ["少し痛いです", "つらいです", "途中で伝えてください"],
    ["検査前の不安が減る情報を", "発信しています。", "チャンネル登録しておくと、", "次の検査のときに役立ちます。"],
]

BG_FILES = [
    BG_DIR / "01_patient_anxiety.png",
    BG_DIR / "05_patient_alone_anxiety.png",
    ASSET_DIR / "bg_03.png",
    BG_DIR / "02_probe_closeup.png",
    ASSET_DIR / "bg_05.png",
    BG_DIR / "03_probe_adjustment.png",
    BG_DIR / "08_navy_exam_monitor.png",
    BG_DIR / "06_reassure_patient.png",
    BG_DIR / "09_navy_listening.png",
    BG_DIR / "07_patient_speaks_up.png",
    ASSET_DIR / "bg_04.png",
]

FONT_BOLD = [
    r"C:\Windows\Fonts\YuGothB.ttc",
    r"C:\Windows\Fonts\YuGothM.ttc",
    r"C:\Windows\Fonts\meiryob.ttc",
    r"C:\Windows\Fonts\meiryo.ttc",
]


def choose_font(size):
    for path in FONT_BOLD:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def cover_image(path, focus_x=0.5, focus_y=0.5):
    im = Image.open(path).convert("RGB")
    scale = max(SIZE[0] / im.width, SIZE[1] / im.height)
    new_size = (round(im.width * scale), round(im.height * scale))
    im = im.resize(new_size, Image.LANCZOS)
    left = round((im.width - SIZE[0]) * focus_x)
    top = round((im.height - SIZE[1]) * focus_y)
    return im.crop((left, top, left + SIZE[0], top + SIZE[1]))


def fit_font(draw, lines, max_width, start_size, min_size):
    size = start_size
    while size >= min_size:
        font = choose_font(size)
        widths = [draw.textbbox((0, 0), line, font=font, stroke_width=3)[2] for line in lines]
        if max(widths) <= max_width:
            return font
        size -= 3
    return choose_font(min_size)


def draw_center_text(im, lines, index):
    draw = ImageDraw.Draw(im, "RGBA")
    max_width = 920
    start_size = 88
    min_size = 48
    line_gap = 22
    y_center = 650 if index in (1, 2) else 720

    if index == 1:
        start_size = 98
    if index in (3, 6, 7, 10):
        start_size = 72
        max_width = 970
    if index == 11:
        start_size = 58
        min_size = 42
        max_width = 980
        line_gap = 18
        y_center = 650

    font = fit_font(draw, lines, max_width, start_size, min_size)
    bboxes = [draw.textbbox((0, 0), line, font=font, stroke_width=4) for line in lines]
    heights = [b[3] - b[1] for b in bboxes]
    widths = [b[2] - b[0] for b in bboxes]

    total_h = sum(heights) + line_gap * (len(lines) - 1)
    y = y_center - total_h // 2
    text_w = max(widths)
    pad_x = 54
    pad_y = 42
    box = (
        (SIZE[0] - text_w) // 2 - pad_x,
        y - pad_y,
        (SIZE[0] + text_w) // 2 + pad_x,
        y + total_h + pad_y,
    )
    draw.rounded_rectangle(box, radius=34, fill=(255, 255, 255, 222))

    yy = y
    for line, height, bbox in zip(lines, heights, bboxes):
        x = (SIZE[0] - (bbox[2] - bbox[0])) // 2
        draw.text((x + 3, yy + 3), line, font=font, fill=(255, 255, 255, 180), stroke_width=5, stroke_fill=(255, 255, 255, 180))
        draw.text((x, yy), line, font=font, fill=(18, 58, 88, 255), stroke_width=2, stroke_fill=(255, 255, 255, 255))
        yy += height + line_gap
    return im


def make_contact_sheet(paths):
    thumb_w, thumb_h = 270, 480
    label_h = 32
    cols = 6
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (thumb_w * cols, (thumb_h + label_h) * rows), (245, 247, 250))
    font = ImageFont.load_default()
    for idx, path in enumerate(paths):
        im = Image.open(path).convert("RGB")
        im.thumbnail((thumb_w, thumb_h), Image.LANCZOS)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), "white")
        tile.paste(im, ((thumb_w - im.width) // 2, 0))
        ImageDraw.Draw(tile).text((8, thumb_h + 9), Path(path).name, fill=(0, 0, 0), font=font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
    sheet.save(ASSET_DIR / "_contact_sheet_final_text_frames_v2_varied.png")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    for i, (lines, bg_file) in enumerate(zip(TEXTS, BG_FILES), start=1):
        bg = cover_image(bg_file, focus_y=0.45 if i in (1, 2, 8, 9, 10) else 0.5)
        frame = draw_center_text(bg, lines, i)
        out = OUT_DIR / f"frame_{i:02d}.png"
        frame.save(out)
        outputs.append(out)

    cta_out = OUT_DIR / "frame_12.png"
    shutil.copy2(CTA, cta_out)
    outputs.append(cta_out)
    make_contact_sheet(outputs)
    manifest = {
        "title": "エコー検査、痛くないの？怖くないの？",
        "asset_dir": str(ASSET_DIR),
        "final_text_frames": [str(path) for path in outputs],
        "contact_sheet": str(ASSET_DIR / "_contact_sheet_final_text_frames_v2_varied.png"),
        "size": {"width": SIZE[0], "height": SIZE[1]},
        "note": "v2 varied backgrounds: generated patient/probe/staff scenes plus existing medical detail backgrounds",
    }
    (OUT_DIR / "frame_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(ASSET_DIR / "_contact_sheet_final_text_frames_v2_varied.png")


if __name__ == "__main__":
    main()
