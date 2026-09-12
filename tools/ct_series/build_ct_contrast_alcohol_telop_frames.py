from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "ct_series" / "ct_contrast_alcohol_v1"
OUT_DIR = ASSET_DIR / "telop_frames"
CONTACT_SHEET = OUT_DIR / "contact_sheet_telop_frames.png"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (8, 30, 54, 255)
BLUE = (35, 119, 204, 255)
WHITE = (255, 255, 255, 235)
PANEL_EDGE = (255, 255, 255, 255)
SHADOW = (16, 26, 38, 72)


# Each frame has one message. All telops are centered on the X axis and placed
# in the lower safe area, above the Reels bottom UI.
FRAMES = [
    {
        "src": "01_hook_convenience_store.png",
        "out": "01_hook_convenience_store_telop.png",
        "lines": [[("今日、", "navy"), ("造影CT", "blue"), ("だった", "navy")], [("お酒、飲んでいい？", "navy")]],
        "position": "top",
    },
    {
        "src": "02_hesitation_at_shelf.png",
        "out": "02_hesitation_at_shelf_telop.png",
        "lines": [[("検査のとき", "navy")], [("聞きそびれた…", "navy")]],
        "position": "top",
    },
    {
        "src": "03_check_instructions.png",
        "out": "03_check_instructions_telop.png",
        "lines": [[("案内は", "navy"), ("医療機関", "blue"), ("で", "navy")], [("違うこともあります", "navy")]],
        "position": "top",
    },
    {
        "src": "04_pour_water.png",
        "out": "04_pour_water_telop.png",
        "lines": [[("造影剤の多くは", "navy")], [("", "navy"), ("尿", "blue"), ("から出ていきます", "navy")]],
        "position": "top",
    },
    {
        "src": "05_choose_water.png",
        "out": "05_choose_water_telop.png",
        "lines": [[("水分制限がなければ", "navy")], [("水やお茶で水分補給", "navy")]],
        "position": "top",
    },
    {
        "src": "06_water_not_alcohol.png",
        "out": "06_water_not_alcohol_telop.png",
        "lines": [[("", "navy"), ("お酒", "blue"), ("は", "navy")], [("水分補給の代わりにはなりません", "navy")]],
        "position": "top",
    },
    {
        "src": "07_check_facility_guidance.png",
        "out": "07_check_facility_guidance_telop.png",
        "lines": [[("当日の", "navy"), ("飲酒", "blue"), ("を控えるよう", "navy")], [("案内する施設もあります", "navy")]],
        "position": "top",
    },
    {
        "src": "08_follow_individual_guidance.png",
        "out": "08_follow_individual_guidance_telop.png",
        "lines": [[("腎臓の病気・水分制限がある方は", "navy")], [("個別の", "navy"), ("説明", "blue"), ("を優先", "navy")]],
        "position": "top",
    },
    {
        "src": "09_call_facility.png",
        "out": "09_call_facility_telop.png",
        "lines": [[("迷ったら", "navy")], [("受けた医療機関へ", "navy"), ("確認", "blue")]],
        "position": "top",
    },
    {
        "src": "10_cta_home.png",
        "out": "10_cta_home_telop.png",
        "lines": [[("帰宅後に見返すなら", "navy")], [("保存", "blue"), ("・", "navy"), ("フォロー", "blue")]],
        "position": "top",
    },
]


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size=size)


def cover_resize(image: Image.Image) -> Image.Image:
    image = image.convert("RGB")
    scale = max(W / image.width, H / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS
    )
    left = (resized.width - W) // 2
    top = (resized.height - H) // 2
    return resized.crop((left, top, left + W, top + H))


def fill(kind: str) -> tuple[int, int, int, int]:
    return BLUE if kind == "blue" else NAVY


def measure_line(draw: ImageDraw.ImageDraw, line, fnt):
    width, height = 0, 0
    for text, _ in line:
        box = draw.textbbox((0, 0), text, font=fnt)
        width += box[2] - box[0]
        height = max(height, box[3] - box[1])
    return width, height


def fit_font(draw: ImageDraw.ImageDraw, lines):
    for size in range(70, 40, -2):
        fnt = font(size)
        gap = max(12, round(size * 0.2))
        sizes = [measure_line(draw, line, fnt) for line in lines]
        total_h = sum(height for _, height in sizes) + gap * (len(lines) - 1)
        if max(width for width, _ in sizes) <= 820 and total_h <= 180:
            return fnt, gap, sizes
    return font(40), 12, [measure_line(draw, line, font(40)) for line in lines]


def draw_telop(source: Path, frame: dict) -> Image.Image:
    base = cover_resize(Image.open(source)).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    shadow_draw = ImageDraw.Draw(shadow)

    fnt, gap, sizes = fit_font(draw, frame["lines"])
    text_w = max(width for width, _ in sizes)
    text_h = sum(height for _, height in sizes) + gap * (len(sizes) - 1)
    pad_x, pad_y = 52, 30
    box_w = min(W - 150, text_w + pad_x * 2)
    box_h = text_h + pad_y * 2
    x0 = (W - box_w) // 2
    y0 = 1360
    x1, y1 = x0 + box_w, y0 + box_h

    shadow_draw.rounded_rectangle((x0 + 8, y0 + 12, x1 + 8, y1 + 12), radius=34, fill=SHADOW)
    overlay.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(12)))
    draw.rounded_rectangle((x0, y0, x1, y1), radius=34, fill=WHITE)
    draw.rounded_rectangle((x0 + 7, y0 + 7, x1 - 7, y1 - 7), radius=28, outline=PANEL_EDGE, width=4)

    yy = y0 + pad_y
    for line, (line_w, line_h) in zip(frame["lines"], sizes):
        xx = x0 + (box_w - line_w) // 2
        for text, kind in line:
            box = draw.textbbox((0, 0), text, font=fnt)
            draw.text((xx, yy - box[1]), text, font=fnt, fill=fill(kind))
            xx += box[2] - box[0]
        yy += line_h + gap
    return Image.alpha_composite(base, overlay).convert("RGB")


def make_contact_sheet(paths: list[Path]) -> None:
    cols, thumb_w, thumb_h, label_h = 5, 216, 384, 36
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (245, 247, 250))
    label_font = ImageFont.load_default()
    for index, path in enumerate(paths):
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), "white")
        tile.paste(image, ((thumb_w - image.width) // 2, 0))
        ImageDraw.Draw(tile).text((8, thumb_h + 10), path.name[:30], fill=(0, 0, 0), font=label_font)
        sheet.paste(tile, ((index % cols) * thumb_w, (index // cols) * (thumb_h + label_h)))
    sheet.save(CONTACT_SHEET, quality=94)


def plain_lines(lines) -> list[str]:
    return ["".join(text for text, _ in line) for line in lines]


def main() -> None:
    if not FONT_PATH.exists():
        raise FileNotFoundError(FONT_PATH)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    manifest_frames = []
    for frame in FRAMES:
        source = ASSET_DIR / frame["src"]
        output = OUT_DIR / frame["out"]
        if not source.exists():
            raise FileNotFoundError(source)
        draw_telop(source, frame).save(output, quality=95)
        outputs.append(output)
        manifest_frames.append(
            {
                "source": str(source),
                "output": str(output),
                "telop": plain_lines(frame["lines"]),
                "position": "bottom-center",
            }
        )
    make_contact_sheet(outputs)
    (OUT_DIR / "telop_manifest.json").write_text(
        json.dumps(
            {
                "title": "造影CTのあと、お酒は飲んでもいい？",
                "font": str(FONT_PATH),
                "style": "bottom-center; white rounded backing; dark navy text; blue key words only",
                "size": {"width": W, "height": H},
                "frames": manifest_frames,
                "contact_sheet": str(CONTACT_SHEET),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8-sig",
    )
    print(CONTACT_SHEET)


if __name__ == "__main__":
    main()
