from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "ct_series" / "ct_duration_v1"
BG_DIR = ASSET_DIR / "backgrounds"
OUT_DIR = ASSET_DIR / "telop_frames"
CONTACT_SHEET = ASSET_DIR / "contact_sheet_telop_frames.png"

W, H = 1080, 1920
NAVY = (12, 46, 78, 255)
ACCENT = (50, 123, 154, 255)
WHITE = (255, 255, 255, 238)
WHITE_SOLID = (255, 255, 255, 255)
SHADOW = (18, 28, 38, 76)

FONT_BOLD = [
    r"C:\Windows\Fonts\YuGothB.ttc",
    r"C:\Windows\Fonts\NotoSansJP-VF.ttf",
    r"C:\Windows\Fonts\meiryob.ttc",
    r"C:\Windows\Fonts\BIZ-UDGothicB.ttc",
]
FONT_REG = [
    r"C:\Windows\Fonts\YuGothM.ttc",
    r"C:\Windows\Fonts\NotoSansJP-VF.ttf",
    r"C:\Windows\Fonts\meiryo.ttc",
    r"C:\Windows\Fonts\BIZ-UDGothicR.ttc",
]


FRAMES = [
    {
        "src": "slide01_bg.png",
        "out": "slide01_telop.png",
        "lines": ["CTって", "何分くらい？"],
        "box": (112, 132, 968, 382),
        "accent": True,
    },
    {
        "src": "slide02_bg.png",
        "out": "slide02_telop.png",
        "lines": ["時間がわからないと", "予定も不安に"],
        "box": (86, 132, 994, 382),
    },
    {
        "src": "slide03_bg.png",
        "out": "slide03_telop.png",
        "lines": ["撮影自体は", "数秒〜1分程度が多い"],
        "box": (58, 132, 1022, 382),
    },
    {
        "src": "slide04_bg.png",
        "out": "slide04_telop.png",
        "lines": ["単純CTは", "5〜10分程度が目安"],
        "box": (64, 132, 1016, 382),
    },
    {
        "src": "slide05_bg.png",
        "out": "slide05_telop.png",
        "lines": ["造影CTは", "準備に時間がかかります"],
        "box": (54, 132, 1026, 382),
    },
    {
        "src": "slide06_bg.png",
        "out": "slide06_telop.png",
        "lines": ["造影CTは", "30分前後が目安"],
        "box": (94, 132, 986, 382),
    },
    {
        "src": "slide07_bg.png",
        "out": "slide07_telop.png",
        "lines": ["追加撮影があると", "待ち時間が長めに"],
        "box": (70, 132, 1010, 382),
    },
    {
        "src": "slide08_bg.png",
        "out": "slide08_telop.png",
        "lines": ["血液検査の結果待ちが", "加わることも"],
        "box": (52, 132, 1028, 382),
    },
    {
        "src": "slide09_bg.png",
        "out": "slide09_telop.png",
        "lines": ["検査時間と待ち時間は", "別で考えると安心"],
        "box": (44, 132, 1036, 382),
    },
    {
        "src": "slide10_bg.png",
        "out": "slide10_telop.png",
        "lines": ["気になる時は", "事前に聞いてOK"],
        "box": (112, 132, 968, 382),
    },
    {
        "src": "slide11_bg.png",
        "out": "slide11_telop.png",
        "lines": ["だいたいの時間を知ると", "当日が少し楽に"],
        "box": (46, 132, 1034, 382),
    },
    {
        "src": "slide12_bg.png",
        "out": "slide12_telop.png",
        "lines": ["参考になったら保存", "次の投稿もフォローで"],
        "box": (48, 132, 1032, 382),
        "accent": True,
    },
]


def choose_font(size: int, bold: bool = True):
    for font_path in FONT_BOLD if bold else FONT_REG:
        if Path(font_path).exists():
            return ImageFont.truetype(font_path, size=size)
    return ImageFont.load_default()


def cover_resize(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")
    scale = max(W / img.width, H / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - W) // 2
    top = (nh - H) // 2
    return resized.crop((left, top, left + W, top + H))


def text_size(draw: ImageDraw.ImageDraw, lines, font, spacing):
    boxes = [draw.textbbox((0, 0), line, font=font) for line in lines]
    widths = [box[2] - box[0] for box in boxes]
    heights = [box[3] - box[1] for box in boxes]
    return max(widths), sum(heights) + spacing * (len(lines) - 1), heights


def fit_font(draw: ImageDraw.ImageDraw, lines, max_w: int, max_h: int):
    size = 80
    spacing = 18
    while size >= 42:
        font = choose_font(size, True)
        width, height, _ = text_size(draw, lines, font, spacing)
        if width <= max_w and height <= max_h:
            return font, spacing
        size -= 2
    return choose_font(42, True), 14


def draw_soft_safety_layers(img: Image.Image):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, W, 470), fill=(255, 255, 255, 20))
    draw.rectangle((0, H - 260, W, H), fill=(0, 0, 0, 24))
    img.alpha_composite(overlay)


def draw_telop(img: Image.Image, frame: dict):
    x0, y0, x1, y1 = frame["box"]
    lines = frame["lines"]

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(
        (x0 + 10, y0 + 12, x1 + 10, y1 + 12),
        radius=36,
        fill=SHADOW,
    )
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(12)))

    draw = ImageDraw.Draw(img, "RGBA")
    draw.rounded_rectangle((x0, y0, x1, y1), radius=34, fill=WHITE)
    draw.rounded_rectangle(
        (x0 + 10, y0 + 10, x1 - 10, y1 - 10),
        radius=26,
        outline=WHITE_SOLID,
        width=6,
    )
    if frame.get("accent"):
        draw.rounded_rectangle((x0 + 62, y1 - 34, x1 - 62, y1 - 24), radius=5, fill=ACCENT)

    font, spacing = fit_font(draw, lines, (x1 - x0) - 92, (y1 - y0) - 80)
    _, total_h, heights = text_size(draw, lines, font, spacing)
    yy = y0 + ((y1 - y0) - total_h) // 2 - 5
    for line, line_h in zip(lines, heights):
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        draw.text(((x0 + x1 - line_w) // 2, yy), line, font=font, fill=NAVY)
        yy += line_h + spacing


def make_contact_sheet(paths: list[Path]):
    cols = 4
    thumb_w, thumb_h = 216, 384
    label_h = 36
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (245, 247, 250))
    label_font = ImageFont.load_default()
    for idx, path in enumerate(paths):
        img = Image.open(path).convert("RGB")
        img.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), "white")
        tile.paste(img, ((thumb_w - img.width) // 2, 0))
        ImageDraw.Draw(tile).text((8, thumb_h + 10), path.name[:32], fill=(0, 0, 0), font=label_font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
    sheet.save(CONTACT_SHEET, quality=94)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    for frame in FRAMES:
        src = BG_DIR / frame["src"]
        out = OUT_DIR / frame["out"]
        img = cover_resize(Image.open(src)).convert("RGBA")
        draw_soft_safety_layers(img)
        draw_telop(img, frame)
        img.convert("RGB").save(out, quality=95)
        outputs.append(out)

    make_contact_sheet(outputs)
    manifest = {
        "title": "CTって何分くらいかかるの？",
        "size": {"width": W, "height": H},
        "style": "white rounded telop box with navy bold Japanese text",
        "asset_dir": str(ASSET_DIR),
        "background_dir": str(BG_DIR),
        "output_dir": str(OUT_DIR),
        "contact_sheet": str(CONTACT_SHEET),
        "frames": [
            {
                "source": frame["src"],
                "output": str(OUT_DIR / frame["out"]),
                "telop": frame["lines"],
            }
            for frame in FRAMES
        ],
    }
    (OUT_DIR / "telop_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8-sig",
    )
    print(OUT_DIR)
    print(CONTACT_SHEET)


if __name__ == "__main__":
    main()
