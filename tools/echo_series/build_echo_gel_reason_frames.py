from pathlib import Path
import json
import shutil

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "echo_series" / "02_gel_reason"
OUT_DIR = ASSET_DIR / "final_text_frames"
CTA = ROOT / "reel_assets" / "common" / "reel_end_card_save.png"

SIZE = (1080, 1920)

TEXTS = [
    ["エコーのゼリー", "なんで塗るの？"],
    ["冷たく感じることも", "ありますよね"],
    ["結論", "音を体に", "伝えやすくするためです"],
    ["エコーは", "音を使う検査です"],
    ["でも 空気があると", "音はうまく", "伝わりません"],
    ["ゼリーは", "肌と機械のすき間を", "埋めます"],
    ["音が通りやすくなり", "画像が見えやすくなります"],
    ["検査も", "進めやすくなります"],
    ["冷たく感じるときや", "肌が心配なときは", "遠慮なく伝えてください"],
    ["あなたの不安を", "伝えることは", "迷惑じゃありません"],
    ["検査前の不安が減る情報を", "発信しています。", "チャンネル登録しておくと、", "次の検査のときに役立ちます。"],
]

BG_FILES = [
    "bg_01.png",
    "bg_02.png",
    "bg_03.png",
    "bg_04.png",
    "bg_05.png",
    "bg_06.png",
    "bg_07.png",
    "bg_07.png",
    "bg_08.png",
    "bg_10.png",
    "bg_09.png",
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


def cover_image(path):
    im = Image.open(path).convert("RGB")
    scale = max(SIZE[0] / im.width, SIZE[1] / im.height)
    new_size = (round(im.width * scale), round(im.height * scale))
    im = im.resize(new_size, Image.LANCZOS)
    left = (im.width - SIZE[0]) // 2
    top = (im.height - SIZE[1]) // 2
    return im.crop((left, top, left + SIZE[0], top + SIZE[1]))


def fit_font(draw, lines, max_width, start_size, min_size):
    size = start_size
    visible = [line for line in lines if line]
    while size >= min_size:
        font = choose_font(size)
        widths = [draw.textbbox((0, 0), line, font=font, stroke_width=3)[2] for line in visible]
        if max(widths) <= max_width:
            return font
        size -= 3
    return choose_font(min_size)


def draw_center_text(im, lines, index):
    draw = ImageDraw.Draw(im, "RGBA")
    max_width = 900
    start_size = 96
    min_size = 50
    line_gap = 24
    y_center = 720

    if index == 2:
        start_size = 78
    if index == 6:
        start_size = 76
        max_width = 960
    if index == 9:
        start_size = 52
        min_size = 38
        max_width = 980
        line_gap = 14
        y_center = 760
    if index == 10:
        start_size = 70
        max_width = 900
        y_center = 720
    if index == 11:
        start_size = 58
        min_size = 42
        max_width = 980
        line_gap = 18
        y_center = 650

    font = fit_font(draw, lines, max_width, start_size, min_size)
    heights = []
    widths = []
    for line in lines:
        if not line:
            heights.append(34)
            widths.append(0)
            continue
        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=4)
        heights.append(bbox[3] - bbox[1])
        widths.append(bbox[2] - bbox[0])
    total_h = sum(heights) + line_gap * (len(lines) - 1)
    y = y_center - total_h // 2

    pad_x = 54
    pad_y = 42
    text_w = max(widths)
    box = (
        (SIZE[0] - text_w) // 2 - pad_x,
        y - pad_y,
        (SIZE[0] + text_w) // 2 + pad_x,
        y + total_h + pad_y,
    )
    draw.rounded_rectangle(box, radius=34, fill=(255, 255, 255, 220))

    yy = y
    for line, height in zip(lines, heights):
        if line:
            bbox = draw.textbbox((0, 0), line, font=font, stroke_width=4)
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
    sheet.save(ASSET_DIR / "_contact_sheet_final_text_frames.png")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    for i, (lines, bg_file) in enumerate(zip(TEXTS, BG_FILES), start=1):
        bg_path = ASSET_DIR / bg_file
        bg = cover_image(bg_path)
        frame = draw_center_text(bg, lines, i)
        out = OUT_DIR / f"frame_{i:02d}.png"
        frame.save(out)
        outputs.append(out)

    cta_out = OUT_DIR / "frame_12.png"
    shutil.copy2(CTA, cta_out)
    outputs.append(cta_out)
    make_contact_sheet(outputs)
    manifest = {
        "title": "エコーのゼリーは何のため？",
        "asset_dir": str(ASSET_DIR),
        "final_text_frames": [str(path) for path in outputs],
        "contact_sheet": str(ASSET_DIR / "_contact_sheet_final_text_frames.png"),
        "size": {"width": SIZE[0], "height": SIZE[1]},
    }
    (OUT_DIR / "frame_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(ASSET_DIR / "_contact_sheet_final_text_frames.png")


if __name__ == "__main__":
    main()
