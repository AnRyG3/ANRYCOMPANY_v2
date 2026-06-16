from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "bone_density_series" / "03_dxa_lumbar_femur_reason"
BG_DIR = ASSET_DIR / "background_frames"
OUT_DIR = ASSET_DIR / "final_text_frames"
SIZE = (1080, 1920)

TEXTS = [
    ["DXA法って", "どんな検査？"],
    ["骨密度を", "弱いX線で測る検査です"],
    ["よく測る場所は", "腰椎と大腿骨近位部"],
    ["理由は", "骨折した時の影響が", "大きい場所だから"],
    ["腰椎は", "背骨の変化を", "見やすい場所"],
    ["大腿骨近位部は", "転倒後の骨折リスクと", "関係しやすい場所"],
    ["かかとの検査は", "入口として使われることも"],
    ["気になる結果は", "医療機関で確認を"],
    ["不安をあおらず", "知って安心する検査へ"],
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
        widths = [draw.textbbox((0, 0), line, font=font, stroke_width=3)[2] for line in lines]
        if max(widths) <= max_width:
            return font
        size -= 3
    return choose_font(min_size)


def text_config(index):
    cfg = {
        "max_width": 930,
        "start_size": 88,
        "min_size": 44,
        "line_gap": 22,
        "y_center": 425,
    }
    if index in {2, 3, 4, 5, 6, 7, 8, 9}:
        cfg["start_size"] = 74
        cfg["max_width"] = 970
        cfg["line_gap"] = 18
    if index in {4, 6}:
        cfg["start_size"] = 66
    if index in {4, 5, 6}:
        cfg["y_center"] = 405
    if index in {9, 10}:
        cfg["y_center"] = 460
    return cfg


def draw_text(im, lines, index):
    draw = ImageDraw.Draw(im, "RGBA")
    cfg = text_config(index)
    font = fit_font(draw, lines, cfg["max_width"], cfg["start_size"], cfg["min_size"])
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
    cols = 5
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
        "title": "DXA法って何？なぜ腰と大腿骨で測るの？",
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
