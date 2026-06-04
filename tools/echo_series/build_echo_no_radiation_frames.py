from pathlib import Path
import json
import shutil

from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "echo_series" / "04_no_radiation"
OUT_DIR = ASSET_DIR / "final_text_frames"
CTA = ROOT / "reel_assets" / "common" / "reel_end_card_save.png"

ECHO_01 = ROOT / "reel_assets" / "echo_series" / "01_what_ultrasound_sees"
ECHO_02 = ROOT / "reel_assets" / "echo_series" / "02_gel_reason"
ECHO_03 = ROOT / "reel_assets" / "echo_series" / "03_pain_fear"
ECHO_03_GEN = ECHO_03 / "generated_backgrounds_v2"

SIZE = (1080, 1920)

TEXTS = [
    ["被ばくが不安な人へ", "エコーはここが違います"],
    ["エコーは", "放射線を使わない", "検査です"],
    ["使っているのは", "放射線ではなく", "音です"],
    ["体に音を当てて", "跳ね返った音を", "画像にします"],
    ["だからエコーでは", "放射線被ばくは", "ありません"],
    ["でも", "放射線を使う検査が", "悪いわけではありません"],
    ["レントゲン CT MRI エコーは", "見たいものが", "違います"],
    ["エコーは", "動きや血流を見るのが", "得意です"],
    ["でも", "空気や骨の奥は", "苦手です"],
    ["怖い検査ではなく", "目的に合わせた", "検査です"],
    ["検査前の不安が減る情報を", "発信しています。", "チャンネル登録しておくと、", "次の検査のときに役立ちます。"],
]

BG_FILES = [
    ECHO_03_GEN / "01_patient_anxiety.png",
    ECHO_01 / "bg_02.png",
    ECHO_01 / "bg_03.png",
    ECHO_03_GEN / "02_probe_closeup.png",
    ECHO_03_GEN / "03_probe_adjustment.png",
    ECHO_03_GEN / "09_navy_listening.png",
    ECHO_03_GEN / "08_navy_exam_monitor.png",
    ECHO_03_GEN / "08_navy_exam_monitor.png",
    ECHO_03_GEN / "03_probe_adjustment.png",
    ECHO_03_GEN / "06_reassure_patient.png",
    ECHO_03 / "bg_04.png",
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


def add_readability_layer(im):
    draw = ImageDraw.Draw(im, "RGBA")
    overlay = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle((0, 0, SIZE[0], SIZE[1]), fill=(255, 255, 255, 18))
    od.rectangle((0, 0, SIZE[0], 260), fill=(13, 48, 74, 34))
    od.rectangle((0, 1500, SIZE[0], SIZE[1]), fill=(13, 48, 74, 30))
    im = Image.alpha_composite(im.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(im, "RGBA")
    return im


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
    im = add_readability_layer(im)
    draw = ImageDraw.Draw(im, "RGBA")
    max_width = 930
    start_size = 88
    min_size = 46
    line_gap = 22
    y_center = 705

    if index == 1:
        start_size = 86
        max_width = 980
        y_center = 670
    if index in (2, 4, 5, 6, 7, 8, 10):
        start_size = 74
        max_width = 990
    if index == 11:
        start_size = 58
        min_size = 42
        max_width = 990
        line_gap = 18
        y_center = 640
    if index in (5, 9):
        y_center = 430
    if index in (1, 6, 7, 8, 10):
        y_center = 500

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
    shadow = (box[0] + 8, box[1] + 10, box[2] + 8, box[3] + 10)
    draw.rounded_rectangle(shadow, radius=34, fill=(8, 35, 56, 86))
    draw.rounded_rectangle(box, radius=34, fill=(255, 255, 255, 226))

    yy = y
    for line, height, bbox in zip(lines, heights, bboxes):
        x = (SIZE[0] - (bbox[2] - bbox[0])) // 2
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
    sheet.save(ASSET_DIR / "_contact_sheet_final_text_frames.png")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    for i, (lines, bg_file) in enumerate(zip(TEXTS, BG_FILES), start=1):
        bg = cover_image(bg_file, focus_y=0.45 if i in (1, 6, 10) else 0.5)
        frame = draw_center_text(bg, lines, i)
        out = OUT_DIR / f"frame_{i:02d}.png"
        frame.save(out)
        outputs.append(out)

    cta_out = OUT_DIR / "frame_12.png"
    shutil.copy2(CTA, cta_out)
    outputs.append(cta_out)
    make_contact_sheet(outputs)

    manifest = {
        "title": "放射線を使わない検査ってどういうこと？",
        "asset_dir": str(ASSET_DIR),
        "final_text_frames": [str(path) for path in outputs],
        "contact_sheet": str(ASSET_DIR / "_contact_sheet_final_text_frames.png"),
        "size": {"width": SIZE[0], "height": SIZE[1]},
        "note": "12-frame text images only. Backgrounds reused from existing echo series for visual consistency.",
    }
    (OUT_DIR / "frame_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(ASSET_DIR / "_contact_sheet_final_text_frames.png")


if __name__ == "__main__":
    main()
