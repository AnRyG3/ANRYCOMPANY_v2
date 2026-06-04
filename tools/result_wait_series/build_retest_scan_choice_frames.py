from pathlib import Path
import json
import shutil

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "result_wait_series" / "05_scan_choice"
OUT_DIR = ASSET_DIR / "final_text_frames"
CTA = ROOT / "reel_assets" / "common" / "reel_end_card_save.png"

RESULT_WAIT = ROOT / "reel_assets" / "result_wait_series" / "01_result_wait_mri_ct" / "sources"
CT_BG = ROOT / "reel_assets" / "ct_series" / "ct_contrast_v1" / "generated_backgrounds" / "bg_02_ct_room.png"
MRI_BG = ROOT / "reel_assets" / "mri_series" / "mri_cannot_take_v1" / "generated_backgrounds_v2" / "bg_02_mri_magnet_field.png"
ECHO_BG = ROOT / "reel_assets" / "echo_series" / "03_pain_fear" / "generated_backgrounds_v2" / "02_probe_closeup.png"

SIZE = (1080, 1920)

TEXTS = [
    ["再検査と言われたら", "次はどの検査？"],
    ["CT？ MRI？ エコー？", "不安になりますよね"],
    ["でも", "「悪い結果だから」", "とは限りません"],
    ["もう少し詳しく見るために", "検査を追加することがあります"],
    ["CTは", "体の中を断面で", "広く確認"],
    ["MRIは", "磁石と電波で", "詳しく確認"],
    ["エコーは", "音を使って", "動きや状態を確認"],
    ["医師が", "一番見やすい方法を", "選んでいます"],
    ["検査前の不安を", "安心に変える情報を発信中"],
]

BG_FILES = [
    RESULT_WAIT / "02_waiting_area.png",
    RESULT_WAIT / "01_after_exam.png",
    RESULT_WAIT / "04_doctor_judgement.png",
    RESULT_WAIT / "03_radiologist.png",
    CT_BG,
    MRI_BG,
    ECHO_BG,
    RESULT_WAIT / "04_doctor_judgement.png",
    RESULT_WAIT / "05_closing.png",
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
    max_width = 960
    start_size = 86
    min_size = 48
    line_gap = 24
    y_center = 500

    if index == 1:
        y_center = 540
    if index in (5, 6, 7):
        y_center = 390
        start_size = 94
    if index == 8:
        y_center = 440
    if index == 9:
        y_center = 460
        start_size = 82

    font = fit_font(draw, lines, max_width, start_size, min_size)
    bboxes = [draw.textbbox((0, 0), line, font=font, stroke_width=4) for line in lines]
    heights = [box[3] - box[1] for box in bboxes]
    widths = [box[2] - box[0] for box in bboxes]

    total_h = sum(heights) + line_gap * (len(lines) - 1)
    y = y_center - total_h // 2
    text_w = max(widths)
    pad_x = 48
    pad_y = 42
    box = (
        (SIZE[0] - text_w) // 2 - pad_x,
        y - pad_y,
        (SIZE[0] + text_w) // 2 + pad_x,
        y + total_h + pad_y,
    )
    shadow = (box[0] + 8, box[1] + 10, box[2] + 8, box[3] + 10)
    draw.rounded_rectangle(shadow, radius=34, fill=(8, 35, 56, 92))
    draw.rounded_rectangle(box, radius=34, fill=(255, 255, 255, 232))

    yy = y
    for line, height, bbox in zip(lines, heights, bboxes):
        x = (SIZE[0] - (bbox[2] - bbox[0])) // 2
        draw.text(
            (x, yy),
            line,
            font=font,
            fill=(18, 58, 88, 255),
            stroke_width=2,
            stroke_fill=(255, 255, 255, 255),
        )
        yy += height + line_gap
    return im


def make_contact_sheet(paths):
    thumb_w, thumb_h = 270, 480
    label_h = 32
    cols = 5
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
    sheet.save(ASSET_DIR / "_contact_sheet_final_text_frames.png")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    for i, (lines, bg_file) in enumerate(zip(TEXTS, BG_FILES), start=1):
        focus_y = 0.55 if i in (3, 8) else 0.5
        bg = cover_image(bg_file, focus_y=focus_y)
        frame = draw_center_text(bg, lines, i)
        out = OUT_DIR / f"frame_{i:02d}.png"
        frame.save(out)
        outputs.append(out)

    cta_out = OUT_DIR / "frame_10.png"
    shutil.copy2(CTA, cta_out)
    outputs.append(cta_out)
    make_contact_sheet(outputs)

    manifest = {
        "title": "再検査と言われたら、CT・MRI・エコーどれになるの？",
        "asset_dir": str(ASSET_DIR),
        "final_text_frames": [str(path) for path in outputs],
        "contact_sheet": str(ASSET_DIR / "_contact_sheet_final_text_frames.png"),
        "size": {"width": SIZE[0], "height": SIZE[1]},
        "note": "10-frame reel. Existing approved visual assets reused. No new person model generated.",
    }
    (OUT_DIR / "frame_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(ASSET_DIR / "_contact_sheet_final_text_frames.png")


if __name__ == "__main__":
    main()
