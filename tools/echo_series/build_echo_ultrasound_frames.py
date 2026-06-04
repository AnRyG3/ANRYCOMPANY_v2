from pathlib import Path
import shutil

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "echo_series" / "01_what_ultrasound_sees"
OUT_DIR = ASSET_DIR / "final_text_frames"
CTA = ROOT / "reel_assets" / "common" / "reel_end_card_save.png"

SIZE = (1080, 1920)

TEXTS = [
    ["エコー", "被ばくする？"],
    ["実は", "放射線ゼロ"],
    ["見ているのは", "音の反射"],
    ["CTとは", "ここが違う"],
    ["形", "動き", "血流"],
    ["ここを", "見ています"],
    ["ゼリーの", "理由"],
    ["万能じゃない", "今必要な検査"],
    ["検査前の不安が減る情報を", "発信しています。", "チャンネル登録しておくと、", "次の検査のときに役立ちます。"],
]


def choose_font(candidates, size):
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


FONT_BOLD = [
    r"C:\Windows\Fonts\YuGothB.ttc",
    r"C:\Windows\Fonts\YuGothM.ttc",
    r"C:\Windows\Fonts\meiryob.ttc",
    r"C:\Windows\Fonts\meiryo.ttc",
]


def cover_image(path):
    im = Image.open(path).convert("RGB")
    scale = max(SIZE[0] / im.width, SIZE[1] / im.height)
    new_size = (round(im.width * scale), round(im.height * scale))
    im = im.resize(new_size, Image.LANCZOS)
    left = (im.width - SIZE[0]) // 2
    top = (im.height - SIZE[1]) // 2
    return im.crop((left, top, left + SIZE[0], top + SIZE[1]))


def fit_font(lines, max_width, start_size, min_size=54):
    size = start_size
    while size >= min_size:
        font = choose_font(FONT_BOLD, size)
        dummy = Image.new("RGB", (10, 10))
        draw = ImageDraw.Draw(dummy)
        widths = [draw.textbbox((0, 0), line, font=font, stroke_width=3)[2] for line in lines]
        if max(widths) <= max_width:
            return font
        size -= 4
    return choose_font(FONT_BOLD, min_size)


def draw_center_text(im, lines, index):
    draw = ImageDraw.Draw(im, "RGBA")
    max_width = 880 if index != 9 else 940
    start_size = 112 if index == 1 else 86
    if index == 8:
        start_size = 54
        max_width = 980
    if index == 9:
        start_size = 58
    font = fit_font(lines, max_width, start_size, min_size=38 if index == 8 else 54)
    line_gap = 26 if index != 9 else 18
    if index == 8:
        line_gap = 16
    bboxes = [draw.textbbox((0, 0), line, font=font, stroke_width=4) for line in lines]
    heights = [b[3] - b[1] for b in bboxes]
    total_h = sum(heights) + line_gap * (len(lines) - 1)
    y = 720 if index != 9 else 640
    if index == 8:
        y = 700
    y -= total_h // 2

    pad_x = 56
    pad_y = 42
    text_w = max(b[2] - b[0] for b in bboxes)
    box = (
        (SIZE[0] - text_w) // 2 - pad_x,
        y - pad_y,
        (SIZE[0] + text_w) // 2 + pad_x,
        y + total_h + pad_y,
    )
    draw.rounded_rectangle(box, radius=38, fill=(255, 255, 255, 218))

    yy = y
    for line, height in zip(lines, heights):
        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=4)
        x = (SIZE[0] - (bbox[2] - bbox[0])) // 2
        draw.text((x + 3, yy + 3), line, font=font, fill=(255, 255, 255, 180), stroke_width=5, stroke_fill=(255, 255, 255, 180))
        draw.text((x, yy), line, font=font, fill=(18, 58, 88, 255), stroke_width=2, stroke_fill=(255, 255, 255, 255))
        yy += height + line_gap

    return im


def make_contact_sheet(paths):
    thumb_w, thumb_h = 270, 480
    label_h = 32
    sheet = Image.new("RGB", (thumb_w * 5, (thumb_h + label_h) * 2), (245, 247, 250))
    font = ImageFont.load_default()
    for idx, path in enumerate(paths):
        im = Image.open(path).convert("RGB")
        im.thumbnail((thumb_w, thumb_h), Image.LANCZOS)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), "white")
        tile.paste(im, ((thumb_w - im.width) // 2, 0))
        ImageDraw.Draw(tile).text((8, thumb_h + 9), Path(path).name, fill=(0, 0, 0), font=font)
        sheet.paste(tile, ((idx % 5) * thumb_w, (idx // 5) * (thumb_h + label_h)))
    sheet.save(ASSET_DIR / "_contact_sheet_final_text_frames.png")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    for i, lines in enumerate(TEXTS, start=1):
        bg_path = ASSET_DIR / ("bg_07_v2.png" if i == 7 else f"bg_{i:02d}.png")
        bg = cover_image(bg_path)
        frame = draw_center_text(bg, lines, i)
        out = OUT_DIR / f"frame_{i:02d}.png"
        frame.save(out)
        outputs.append(out)

    cta_out = OUT_DIR / "frame_10.png"
    cta_img = cover_image(CTA)
    cta_img.save(cta_out)
    outputs.append(cta_out)
    make_contact_sheet(outputs)
    print(ASSET_DIR / "_contact_sheet_final_text_frames.png")


if __name__ == "__main__":
    main()
