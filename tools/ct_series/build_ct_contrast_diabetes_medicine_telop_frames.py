from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "ct_series" / "ct_contrast_diabetes_medicine_v1"
OUT_DIR = ASSET_DIR / "telop_frames"
CONTACT_SHEET = OUT_DIR / "contact_sheet_telop_frames.png"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (8, 30, 54, 255)
BLUE = (35, 119, 204, 255)
WHITE = (255, 255, 255, 235)
PANEL_EDGE = (255, 255, 255, 255)
SHADOW = (16, 26, 38, 72)

POSITION_Y = {
    "top": 160,
    "center": 850,
    "bottom": 1370,
}


# One concise message per frame. X is always centered. Vertical placement is
# restricted to top, center, or bottom. Blue is limited to short key terms.
FRAMES = [
    {
        "src": "01_hook_morning_medicine.png",
        "out": "01_hook_morning_medicine_telop.png",
        "lines": [
            [("この", "navy"), ("糖尿病の薬", "blue")],
            [("今朝も飲んでいい？", "navy")],
        ],
        "position": "top",
    },
    {
        "src": "02_check_appointment_guidance.png",
        "out": "02_check_appointment_guidance_telop.png",
        "lines": [
            [("まず", "navy")],
            [("予約時の案内", "blue"), ("を確認", "navy")],
        ],
        "position": "top",
    },
    {
        "src": "03_reassured_no_self_decision.png",
        "out": "03_reassured_no_self_decision_telop.png",
        "lines": [
            [("自己判断しなくて", "navy")],
            [("大丈夫", "blue"), ("です", "navy")],
        ],
        "position": "top",
    },
    {
        "src": "04_compare_medicine_types.png",
        "out": "04_compare_medicine_types_telop.png",
        "lines": [
            [("糖尿病薬の", "navy"), ("一部", "blue"), ("は", "navy")],
            [("休むことがあります", "navy")],
        ],
        "position": "top",
    },
    {
        "src": "05_check_medicine_details.png",
        "out": "05_check_medicine_details_telop.png",
        "lines": [
            [("薬の種類や状態で", "navy")],
            [("対応", "blue"), ("は変わります", "navy")],
        ],
        "position": "top",
    },
    {
        "src": "06_call_medical_facility.png",
        "out": "06_call_medical_facility_telop.png",
        "lines": [
            [("不明なときは", "navy")],
            [("医療機関へ", "navy"), ("確認", "blue")],
        ],
        "position": "top",
    },
    {
        "src": "07_bring_medication_notebook.png",
        "out": "07_bring_medication_notebook_telop.png",
        "lines": [
            [("当日は", "navy")],
            [("お薬手帳", "blue"), ("を持参", "navy")],
        ],
        "position": "bottom",
    },
    {
        "src": "08_show_medication_notebook.png",
        "out": "08_show_medication_notebook_telop.png",
        "lines": [
            [("受付で", "navy"), ("自分から", "blue")],
            [("見せて大丈夫です", "navy")],
        ],
        "position": "bottom",
    },
    {
        "src": "09_prepare_night_before.png",
        "out": "09_prepare_night_before_telop.png",
        "lines": [
            [("造影CTの", "navy"), ("前日", "blue"), ("に", "navy")],
            [("見返せるよう", "navy"), ("保存", "blue")],
        ],
        "position": "bottom",
    },
    {
        "src": "10_save_share_on_phone.png",
        "out": "10_save_share_on_phone_telop.png",
        "lines": [
            [("付き添うご家族にも", "navy")],
            [("この安心を", "navy"), ("共有", "blue")],
        ],
        "position": "bottom",
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
    for size in range(74, 43, -2):
        fnt = font(size)
        gap = max(12, round(size * 0.2))
        sizes = [measure_line(draw, line, fnt) for line in lines]
        total_h = sum(height for _, height in sizes) + gap * (len(lines) - 1)
        if max(width for width, _ in sizes) <= 820 and total_h <= 180:
            return fnt, gap, sizes
    fallback = font(44)
    return fallback, 12, [measure_line(draw, line, fallback) for line in lines]


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
        (x0 + 7, y0 + 7, x1 - 7, y1 - 7),
        radius=28,
        outline=PANEL_EDGE,
        width=4,
    )

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
    sheet = Image.new(
        "RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (245, 247, 250)
    )
    label_font = ImageFont.load_default()
    for index, path in enumerate(paths):
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), "white")
        tile.paste(image, ((thumb_w - image.width) // 2, 0))
        ImageDraw.Draw(tile).text(
            (8, thumb_h + 10), path.name[:30], fill=(0, 0, 0), font=label_font
        )
        sheet.paste(
            tile,
            ((index % cols) * thumb_w, (index // cols) * (thumb_h + label_h)),
        )
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
                "position": f'{frame["position"]}-center',
            }
        )

    make_contact_sheet(outputs)
    (OUT_DIR / "telop_manifest.json").write_text(
        json.dumps(
            {
                "title": "造影CT前、糖尿病の薬はいつも通りでいい？",
                "font": str(FONT_PATH),
                "style": "X-axis centered; top/center/bottom only; white rounded backing; dark navy text; blue key words only",
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
