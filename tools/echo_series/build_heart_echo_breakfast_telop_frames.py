from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
UNIT = ROOT / "reel_assets" / "echo_series" / "09_heart_echo_breakfast_v1_samples"
BASE = UNIT / "images"
OUT = UNIT / "telop_frames"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
PANEL_W = 800
NAVY = (12, 34, 58, 255)
BLUE = (0, 104, 150, 255)
PANEL = (255, 255, 255, 178)
PANEL_EDGE = (255, 255, 255, 220)
SHADOW = (0, 0, 0, 42)


FRAMES = [
    (
        "image_01_breakfast_check.png",
        "telop_01.png",
        [["心臓エコーの朝"], ["朝ごはん", "は食べていい？"]],
        {"朝ごはん"},
        "top",
    ),
    (
        "image_02_same_day_tests.png",
        "telop_02.png",
        [["同じ日の", "別の検査", "で"], ["案内が変わることも"]],
        {"別の検査"},
        "center",
    ),
    (
        "image_03_call_to_ask.png",
        "telop_03.png",
        [["予約時", "に聞いて大丈夫"], ["「朝食は食べて"], ["いいですか？」"]],
        {"予約時"},
        "top",
    ),
    (
        "image_04_morning_hesitation.png",
        "telop_04.png",
        [["食べる？ 抜く？"], ["迷いますよね"]],
        {"迷いますよね"},
        "center",
    ),
    (
        "image_05_cardiac_echo_room.png",
        "telop_05.png",
        [["心臓の動きや形を"], ["胸から", "見る検査"]],
        {"胸から"},
        "center",
    ),
    (
        "image_06_food_guidance_varies.png",
        "telop_06.png",
        [["食事制限", "がない"], ["病院もあります"]],
        {"食事制限"},
        "center",
    ),
    (
        "image_07_other_exam_instruction.png",
        "telop_07.png",
        [["同じ日に"], ["腹部エコー", "などを"], ["受けると"], ["指示が変わることも"]],
        {"腹部エコー"},
        "center",
    ),
    (
        "image_08_transesophageal_probe.png",
        "telop_08.png",
        [["経食道心エコー", "は"], ["別の検査"], ["事前に"], ["食事制限", "があります"]],
        {"経食道心エコー", "食事制限"},
        "center",
    ),
    (
        "image_09_check_guidance.png",
        "telop_09.png",
        [["病院ごとの", "案内票", "を"], ["確認してください"]],
        {"案内票"},
        "top",
    ),
    (
        "image_10_two_check_items.png",
        "telop_10.png",
        [["確認するのは"], ["心エコーの種類"], ["同じ日に受ける検査"]],
        {"心エコーの種類", "同じ日に受ける検査"},
        "center",
    ),
    (
        "image_11_save_night_before.png",
        "telop_11.png",
        [["前日の夜に見返せるよう"], ["保存", "しておいてください"]],
        {"保存"},
        "top",
    ),
]


def font(size: int) -> ImageFont.FreeTypeFont:
    if not FONT_PATH.exists():
        raise FileNotFoundError(FONT_PATH)
    return ImageFont.truetype(str(FONT_PATH), size)


def text_width(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def line_width(draw: ImageDraw.ImageDraw, line: list[str], fnt: ImageFont.FreeTypeFont) -> int:
    gap = int(fnt.size * 0.035)
    return sum(text_width(draw, part, fnt) for part in line) + gap * (len(line) - 1)


def fit_font(draw: ImageDraw.ImageDraw, lines: list[list[str]]) -> tuple[ImageFont.FreeTypeFont, int]:
    for size in range(74, 43, -2):
        fnt = font(size)
        if max(line_width(draw, line, fnt) for line in lines) <= 680:
            return fnt, int(size * 1.22)
    return font(42), 52


def normalize_canvas(image: Image.Image) -> Image.Image:
    return image.convert("RGB").resize((W, H), Image.Resampling.LANCZOS)


def box_y(position: str, height: int) -> int:
    if position == "top":
        return 190
    if position == "bottom":
        return H - height - 250
    if position == "center":
        return (H - height) // 2
    raise ValueError(f"unsupported position: {position}")


def draw_telop(
    image: Image.Image,
    lines: list[list[str]],
    highlights: set[str],
    position: str,
) -> tuple[Image.Image, list[int], int]:
    image = normalize_canvas(image).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    fnt, line_h = fit_font(draw, lines)
    pad_y = 34
    height = line_h * len(lines) + pad_y * 2
    x0 = (W - PANEL_W) // 2
    y0 = box_y(position, height)
    x1, y1 = x0 + PANEL_W, y0 + height

    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(
        (x0 + 6, y0 + 8, x1 + 6, y1 + 8), radius=28, fill=SHADOW
    )
    overlay.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(7)))
    draw.rounded_rectangle((x0, y0, x1, y1), radius=28, fill=PANEL)
    draw.rounded_rectangle(
        (x0 + 7, y0 + 7, x1 - 7, y1 - 7),
        radius=22,
        outline=PANEL_EDGE,
        width=4,
    )

    first_y = y0 + pad_y + int(fnt.size * 0.05)
    gap = int(fnt.size * 0.035)
    for row, line in enumerate(lines):
        x = (W - line_width(draw, line, fnt)) // 2
        y = first_y + row * line_h
        for part in line:
            draw.text(
                (x, y),
                part,
                font=fnt,
                fill=BLUE if part in highlights else NAVY,
            )
            x += text_width(draw, part, fnt) + gap

    image.alpha_composite(overlay)
    return image.convert("RGB"), [x0, y0, x1, y1], fnt.size


def make_contact_sheet(paths: list[Path]) -> Path:
    thumb_w, thumb_h, label_h, cols = 270, 480, 36, 4
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new(
        "RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (246, 248, 250)
    )
    label_font = font(20)
    draw = ImageDraw.Draw(sheet)
    for index, path in enumerate(paths):
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (index % cols) * thumb_w
        y = (index // cols) * (thumb_h + label_h)
        sheet.paste(image, (x + (thumb_w - image.width) // 2, y))
        draw.rectangle(
            (x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill=(255, 255, 255)
        )
        draw.text((x + 8, y + thumb_h + 7), f"{index + 1:02d}", font=label_font, fill=NAVY)
    contact = OUT / "contact_sheet_telop_frames.png"
    sheet.save(contact)
    return contact


def validate_sources() -> None:
    expected = [item[0] for item in FRAMES]
    actual = sorted(path.name for path in BASE.glob("image_*.png"))
    if actual != expected:
        raise RuntimeError(f"source lock mismatch\nexpected={expected}\nactual={actual}")
    for source_name in expected:
        if not (BASE / source_name).is_file():
            raise FileNotFoundError(BASE / source_name)


def main() -> None:
    validate_sources()
    OUT.mkdir(parents=True, exist_ok=True)
    outputs = []
    manifest = []
    for index, (source_name, output_name, lines, highlights, position) in enumerate(
        FRAMES, start=1
    ):
        source = BASE / source_name
        output = OUT / output_name
        image, box, font_size = draw_telop(Image.open(source), lines, highlights, position)
        image.save(output, quality=95)
        outputs.append(output)
        manifest.append(
            {
                "index": index,
                "source": str(source.relative_to(ROOT)),
                "output": str(output.relative_to(ROOT)),
                "telop": ["".join(line) for line in lines],
                "highlights": sorted(highlights),
                "position": position,
                "box": box,
                "x_center": (box[0] + box[2]) // 2,
                "font": str(FONT_PATH),
                "font_size": font_size,
                "panel_opacity": "70%",
            }
        )

    contact = make_contact_sheet(outputs)
    (OUT / "telop_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig"
    )
    print(f"created {len(outputs)} telop frames")
    print(contact)


if __name__ == "__main__":
    main()
