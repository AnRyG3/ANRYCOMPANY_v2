from pathlib import Path
import json
import shutil

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "bone_density_series" / "01_heel_ultrasound_reason"
OUT_DIR = ASSET_DIR / "final_text_frames"
CTA = ROOT / "reel_assets" / "common" / "reel_end_card_save.png"
SIZE = (1080, 1920)

TEXTS = [
    ["健診で", "かかとに音波", "なぜ？"],
    ["あれは", "骨の状態を見る", "検査のひとつです"],
    ["かかとの骨に", "超音波を通して"],
    ["骨の強さの", "目安を調べます"],
    ["かかとは", "測りやすい場所なので"],
    ["健診などで", "使われることがあります"],
    ["しかも", "放射線を使いません"],
    ["ただし", "これだけで診断が", "決まるわけではありません"],
    ["気になる結果なら", "腰や足のつけ根を測る検査へ", "進むことがあります"],
    ["かかとの検査は", "骨の健康に気づく", "入口です"],
    ["検査前の不安を", "安心に変える情報を発信中"],
]

BG_FILES = [
    "bg_01_health_check_heel_ultrasound.png",
    "bg_04_result_explanation_no_logo.png",
    "bg_03_heel_device_closeup_no_logo.png",
    "bg_03_heel_device_closeup_no_logo.png",
    "bg_05_easy_to_measure_heel_no_logo.png",
    "bg_06_no_radiation_ultrasound_no_logo.png",
    "bg_06_no_radiation_ultrasound_no_logo.png",
    "bg_07_followup_exam_consult_no_logo.png",
    "bg_07_followup_exam_consult_no_logo.png",
    "bg_08_reassuring_save_cta_no_logo.png",
    "bg_08_reassuring_save_cta_no_logo.png",
]

FONT_BOLD = [
    r"C:\Windows\Fonts\YuGothB.ttc",
    r"C:\Windows\Fonts\meiryob.ttc",
    r"C:\Windows\Fonts\YuGothM.ttc",
    r"C:\Windows\Fonts\meiryo.ttc",
]


def choose_font(size):
    for path in FONT_BOLD:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def cover_image(path):
    im = Image.open(path).convert("RGB")
    scale = max(SIZE[0] / im.width, SIZE[1] / im.height)
    new_size = (round(im.width * scale), round(im.height * scale))
    im = im.resize(new_size, Image.Resampling.LANCZOS)
    left = (im.width - SIZE[0]) // 2
    top = (im.height - SIZE[1]) // 2
    return im.crop((left, top, left + SIZE[0], top + SIZE[1]))


def fit_font(draw, lines, max_width, start_size, min_size):
    size = start_size
    while size >= min_size:
        font = choose_font(size)
        widths = [
            draw.textbbox((0, 0), line, font=font, stroke_width=3)[2]
            for line in lines
        ]
        if max(widths) <= max_width:
            return font
        size -= 3
    return choose_font(min_size)


def draw_text(im, lines, index):
    draw = ImageDraw.Draw(im, "RGBA")
    max_width = 930
    start_size = 92
    min_size = 48
    line_gap = 22
    y_center = 470

    if index in {2, 8, 9, 11}:
        start_size = 72
        max_width = 980
        line_gap = 18
    if index == 9:
        start_size = 58
        min_size = 40
        line_gap = 16
    if index == 12:
        start_size = 78

    font = fit_font(draw, lines, max_width, start_size, min_size)
    metrics = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=4)
        metrics.append((bbox[2] - bbox[0], bbox[3] - bbox[1]))

    total_h = sum(h for _, h in metrics) + line_gap * (len(lines) - 1)
    y = y_center - total_h // 2
    text_w = max(w for w, _ in metrics)
    pad_x = 52
    pad_y = 38
    box = (
        (SIZE[0] - text_w) // 2 - pad_x,
        y - pad_y,
        (SIZE[0] + text_w) // 2 + pad_x,
        y + total_h + pad_y,
    )
    draw.rounded_rectangle(box, radius=32, fill=(255, 255, 255, 225))

    yy = y
    for line, (_, height) in zip(lines, metrics):
        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=4)
        line_w = bbox[2] - bbox[0]
        x = (SIZE[0] - line_w) // 2
        draw.text(
            (x, yy),
            line,
            font=font,
            fill=(18, 58, 88, 255),
            stroke_width=3,
            stroke_fill=(255, 255, 255, 255),
        )
        yy += height + line_gap
    return im


def make_contact_sheet(paths):
    thumb_w, thumb_h = 270, 480
    label_h = 32
    cols = 4
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (thumb_w * cols, (thumb_h + label_h) * rows), (245, 247, 250))
    font = ImageFont.load_default()
    for idx, path in enumerate(paths):
        im = Image.open(path).convert("RGB")
        im.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), "white")
        tile.paste(im, ((thumb_w - im.width) // 2, 0))
        ImageDraw.Draw(tile).text((8, thumb_h + 9), Path(path).name, fill=(0, 0, 0), font=font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
    sheet.save(ASSET_DIR / "_contact_sheet_final_text_frames.png")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    for i, (lines, bg_file) in enumerate(zip(TEXTS, BG_FILES), start=1):
        frame = cover_image(ASSET_DIR / bg_file)
        frame = draw_text(frame, lines, i)
        out = OUT_DIR / f"frame_{i:02d}.png"
        frame.save(out)
        outputs.append(out)

    cta_out = OUT_DIR / "frame_12.png"
    shutil.copy2(CTA, cta_out)
    outputs.append(cta_out)

    make_contact_sheet(outputs)
    manifest = {
        "title": "健診で、かかとに音波を当てるのはなぜ？",
        "asset_dir": str(ASSET_DIR),
        "final_text_frames": [str(path) for path in outputs],
        "backgrounds": BG_FILES,
        "size": {"width": SIZE[0], "height": SIZE[1]},
        "contact_sheet": str(ASSET_DIR / "_contact_sheet_final_text_frames.png"),
    }
    (OUT_DIR / "frame_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(ASSET_DIR / "_contact_sheet_final_text_frames.png")


if __name__ == "__main__":
    main()
