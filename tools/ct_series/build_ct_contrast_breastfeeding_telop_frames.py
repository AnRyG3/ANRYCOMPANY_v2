from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "ct_series" / "ct_contrast_breastfeeding_v1_images"
OUT_DIR = ROOT / "reel_assets" / "ct_series" / "ct_contrast_breastfeeding_v1_telop_frames"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"
CONTACT_SHEET = OUT_DIR / "contact_sheet_telop_frames.png"
MANIFEST = OUT_DIR / "telop_manifest.json"

W, H = 1080, 1920
NAVY = (8, 30, 54, 255)
BLUE = (35, 119, 204, 255)
WHITE = (255, 255, 255, 235)
PANEL_EDGE = (255, 255, 255, 255)
SHADOW = (16, 26, 38, 72)

# X is always centered. Values keep clear of the Reels top/bottom UI zones.
POSITION_Y = {"top": 245, "center": 860, "bottom": 1370}

FRAMES = [
    {
        "src": "01_hook_baby_carrier.png",
        "out": "01_hook_baby_carrier_telop.png",
        "lines": [[("造影CT", "blue"), ("のあと", "navy")], [("授乳して大丈夫？", "navy")]],
        "position": "center",
    },
    {
        "src": "02_question_baby_carrier.png",
        "out": "02_question_baby_carrier_telop.png",
        "lines": [[("赤ちゃんのことだから", "navy")], [("気になりますよね", "navy")]],
        "position": "center",
    },
    {
        "src": "03_ask_before_leaving.png",
        "out": "03_ask_before_leaving_telop.png",
        "lines": [[("迷ったら", "navy")], [("帰る前に", "navy"), ("確認", "blue")]],
        "position": "center",
    },
    {
        "src": "04_empathy_after_exam.png",
        "out": "04_empathy_after_exam_telop.png",
        "lines": [[("慎重になるのは", "navy")], [("自然なことです", "navy")]],
        "position": "center",
    },
    {
        "src": "05_reassuring_explanation.png",
        "out": "05_reassuring_explanation_telop.png",
        "lines": [[("多くの場合", "blue")], [("授乳を続けられます", "navy")]],
        "position": "center",
    },
    {
        "src": "06_calm_ct_room.png",
        "out": "06_calm_ct_room_telop.png",
        "lines": [[("赤ちゃんに届く量は", "navy")], [("ごくわずか", "blue"), ("です", "navy")]],
        "position": "center",
    },
    {
        "src": "07_ask_staff.png",
        "out": "07_ask_staff_telop.png",
        "lines": [[("個別の状況は", "navy")], [("担当スタッフに", "navy"), ("確認", "blue")]],
        "position": "center",
    },
    {
        "src": "08_leave_reassured.png",
        "out": "08_leave_reassured_telop.png",
        "lines": [[("自分で時間を", "navy")], [("決めなくて", "navy"), ("大丈夫", "blue")]],
        "position": "center",
    },
    {
        "src": "09_save_cta.png",
        "out": "09_save_cta_telop.png",
        "lines": [[("検査日に見返せるよう", "navy")], [("保存", "blue")]],
        "position": "center",
    },
    {
        "src": "10_follow_cta.png",
        "out": "10_follow_cta_telop.png",
        "lines": [[("次の検査に備えて", "navy")], [("フォロー", "blue")]],
        "position": "center",
    },
]


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size=size)


def cover_resize(image: Image.Image) -> Image.Image:
    image = image.convert("RGB")
    scale = max(W / image.width, H / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = (resized.width - W) // 2
    top = (resized.height - H) // 2
    return resized.crop((left, top, left + W, top + H))


def measure_line(draw: ImageDraw.ImageDraw, line, fnt):
    width, height = 0, 0
    for text, _ in line:
        box = draw.textbbox((0, 0), text, font=fnt)
        width += box[2] - box[0]
        height = max(height, box[3] - box[1])
    return width, height


def fit_font(draw: ImageDraw.ImageDraw, lines):
    for size in range(74, 43, -2):
        fnt = font(size)
        gap = max(12, round(size * 0.2))
        sizes = [measure_line(draw, line, fnt) for line in lines]
        total_h = sum(height for _, height in sizes) + gap * (len(lines) - 1)
        if max(width for width, _ in sizes) <= 820 and total_h <= 180:
            return fnt, gap, sizes
    fnt = font(44)
    return fnt, 12, [measure_line(draw, line, fnt) for line in lines]


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
    y0 = POSITION_Y[frame["position"]]
    x1, y1 = x0 + box_w, y0 + box_h

    shadow_draw.rounded_rectangle(
        (x0 + 8, y0 + 12, x1 + 8, y1 + 12), radius=34, fill=SHADOW
    )
    overlay.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(12)))
    draw.rounded_rectangle((x0, y0, x1, y1), radius=34, fill=WHITE)
    draw.rounded_rectangle(
        (x0 + 7, y0 + 7, x1 - 7, y1 - 7), radius=28, outline=PANEL_EDGE, width=4
    )

    yy = y0 + pad_y
    for line, (line_w, line_h) in zip(frame["lines"], sizes):
        xx = x0 + (box_w - line_w) // 2
        for text, kind in line:
            box = draw.textbbox((0, 0), text, font=fnt)
            draw.text((xx, yy - box[1]), text, font=fnt, fill=BLUE if kind == "blue" else NAVY)
            xx += box[2] - box[0]
        yy += line_h + gap
    return Image.alpha_composite(base, overlay).convert("RGB")


def make_contact_sheet(paths: list[Path]) -> None:
    cols, thumb_w, thumb_h, label_h = 5, 216, 384, 36
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (245, 247, 250))
    label_font = ImageFont.load_default()
    for i, path in enumerate(paths):
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), "white")
        tile.paste(image, ((thumb_w - image.width) // 2, 0))
        ImageDraw.Draw(tile).text((8, thumb_h + 10), path.name[:30], fill=(0, 0, 0), font=label_font)
        sheet.paste(tile, ((i % cols) * thumb_w, (i // cols) * (thumb_h + label_h)))
    sheet.save(CONTACT_SHEET, quality=94)


def main() -> None:
    if not FONT_PATH.exists():
        raise FileNotFoundError(FONT_PATH)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs, manifest_frames = [], []
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
                "telop": ["".join(text for text, _ in line) for line in frame["lines"]],
                "position": f'{frame["position"]}-center',
            }
        )
    make_contact_sheet(outputs)
    MANIFEST.write_text(
        json.dumps(
            {
                "title": "造影CTのあと、授乳はどうすればいい？",
                "font": str(FONT_PATH),
                "style": "X-axis centered; top/center/bottom only; white rounded rectangle 92% opacity; dark navy text; blue key words only",
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
