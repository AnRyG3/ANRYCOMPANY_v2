from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "bone_density_series" / "02_heel_vs_lumbar"
BG_DIR = ASSET_DIR / "background_frames"
OUT_DIR = ASSET_DIR / "final_text_frames"
SIZE = (1080, 1920)

TEXTS = [
    ["骨密度検査", "かかと？", "腰？"],
    ["どこで測るかは", "検査の目的で", "変わります"],
    ["健診では", "かかとで測る検査を", "見ることがあります"],
    ["かかとは", "音波で", "骨の状態の目安を見ます"],
    ["詳しく調べる時は", "腰や", "足のつけ根を", "測ることがあります"],
    ["ここは", "骨折すると", "生活に影響が大きい場所です"],
    ["DXA法では", "弱いX線を使って", "骨密度を測ります"],
    ["かかとは", "骨の健康に気づく", "入口"],
    ["腰や足のつけ根は", "より詳しく見る", "検査"],
    ["どちらが正解ではなく", "役割が違います"],
    ["検査前の不安を", "安心に変える情報を発信中"],
    ["骨密度検査の前に", "見返せるように保存"],
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


def text_config(index):
    cfg = {
        "max_width": 930,
        "start_size": 88,
        "min_size": 46,
        "line_gap": 22,
        "y_center": 430,
    }
    if index in {3, 4, 5, 6, 7, 9, 10, 11}:
        cfg["start_size"] = 72
        cfg["max_width"] = 980
        cfg["line_gap"] = 18
    if index == 5:
        cfg["start_size"] = 64
        cfg["line_gap"] = 14
    if index in {7, 9}:
        cfg["y_center"] = 390
    if index == 10:
        cfg["start_size"] = 66
        cfg["y_center"] = 430
    if index == 11:
        cfg["start_size"] = 70
        cfg["y_center"] = 470
    return cfg


def draw_text(im, lines, index):
    draw = ImageDraw.Draw(im, "RGBA")
    cfg = text_config(index)
    font = fit_font(
        draw,
        lines,
        cfg["max_width"],
        cfg["start_size"],
        cfg["min_size"],
    )
    metrics = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=4)
        metrics.append((bbox[2] - bbox[0], bbox[3] - bbox[1]))

    total_h = sum(h for _, h in metrics) + cfg["line_gap"] * (len(lines) - 1)
    y = cfg["y_center"] - total_h // 2
    text_w = max(w for w, _ in metrics)
    pad_x = 52
    pad_y = 38
    box = (
        (SIZE[0] - text_w) // 2 - pad_x,
        y - pad_y,
        (SIZE[0] + text_w) // 2 + pad_x,
        y + total_h + pad_y,
    )
    draw.rounded_rectangle(box, radius=32, fill=(255, 255, 255, 226))

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
        yy += height + cfg["line_gap"]
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
    for i, lines in enumerate(TEXTS, start=1):
        frame = Image.open(BG_DIR / f"bg_{i:02d}.png").convert("RGB")
        frame = draw_text(frame, lines, i)
        out = OUT_DIR / f"frame_{i:02d}.png"
        frame.save(out)
        outputs.append(out)

    make_contact_sheet(outputs)
    manifest = {
        "title": "骨密度検査、かかとで測るの？ 腰で測るの？",
        "asset_dir": str(ASSET_DIR),
        "background_dir": str(BG_DIR),
        "final_text_frames": [str(path) for path in outputs],
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
