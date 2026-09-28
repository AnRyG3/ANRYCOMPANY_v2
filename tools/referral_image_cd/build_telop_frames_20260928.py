from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
BASE = ROOT / "reel_assets" / "referral_image_cd_20260928_images"
OUT = ROOT / "reel_assets" / "referral_image_cd_20260928_telop_frames"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (16, 36, 55, 255)
BLUE = (0, 104, 150, 255)
PANEL = (255, 255, 255, 179)
SHADOW = (0, 0, 0, 38)


# One screen, one message. Horizontal alignment remains centered throughout.
# Frame 4 uses lower center only because center would hide both the face and CD.
FRAMES = [
    ("image_01_reception_arrival.png", "telop_01_when_to_show_cd.png", [["画像CD", " いつ出す？"]], {"画像CD"}, "center"),
    ("image_02_present_cd.png", "telop_02_tell_reception_first.png", [["受付で"], ["最初に", "伝える"]], {"最初に"}, "center"),
    ("image_03_wait_for_guidance.png", "telop_03_follow_reception_guidance.png", [["渡すタイミングは"], ["受付の案内", "に従う"]], {"受付の案内"}, "center"),
    ("image_04_cd_and_referral_together.png", "telop_04_varies_by_facility.png", [["施設によって"], ["扱いが違うことも"]], {"施設によって"}, "bottom"),
    ("image_05_check_appointment_guidance.png", "telop_05_prioritize_guidance.png", [["事前の案内を"], ["優先してください"]], {"事前の案内"}, "center"),
    ("image_06_ask_reception.png", "telop_06_ask_if_unsure.png", [["迷ったら"], ["「今、お渡ししますか？」"]], {"迷ったら"}, "center"),
    ("image_07_reassured.png", "telop_07_asking_is_ok.png", [["確認するのは"], ["失礼ではありません"]], {"失礼ではありません"}, "center"),
    ("image_08_prepare_before_visit.png", "telop_08_save_before_reception.png", [["紹介先の受付前に"], ["見返せるよう ", "保存"]], {"保存"}, "center"),
    ("image_09_cta_background.png", "telop_09_follow_cta.png", [["フォロー", "して"], ["「これどうする？」を"], ["一緒に減らそう"]], {"フォロー"}, "center"),
]


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size)


def cover(image: Image.Image, size: tuple[int, int] = (W, H)) -> Image.Image:
    image = image.convert("RGB")
    scale = max(size[0] / image.width, size[1] / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - size[0]) // 2
    top = (resized.height - size[1]) // 2
    return resized.crop((left, top, left + size[0], top + size[1]))


def text_width(draw: ImageDraw.ImageDraw, value: str, current_font: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), value, font=current_font)
    return box[2] - box[0]


def row_width(draw: ImageDraw.ImageDraw, row: list[str], current_font: ImageFont.FreeTypeFont) -> int:
    gap = round(current_font.size * 0.08)
    return sum(text_width(draw, piece, current_font) for piece in row) + gap * (len(row) - 1)


def fitted_font(draw: ImageDraw.ImageDraw, rows: list[list[str]]) -> ImageFont.FreeTypeFont:
    for size in range(68, 39, -2):
        candidate = font(size)
        if max(row_width(draw, row, candidate) for row in rows) <= 790:
            return candidate
    return font(38)


def y_position(position: str, box_height: int) -> int:
    if position == "bottom":
        return H - 260 - box_height
    return (H - box_height) // 2


def draw_frame(source: Image.Image, rows: list[list[str]], highlights: set[str], position: str) -> Image.Image:
    base = cover(source).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    current_font = fitted_font(draw, rows)
    row_height = round(current_font.size * 1.16)
    pad_x, pad_y = 56, 34
    box_width = min(920, max(row_width(draw, row, current_font) for row in rows) + pad_x * 2)
    box_height = row_height * len(rows) + pad_y * 2
    x0 = (W - box_width) // 2
    y0 = y_position(position, box_height)
    x1, y1 = x0 + box_width, y0 + box_height

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((x0 + 6, y0 + 8, x1 + 6, y1 + 8), radius=30, fill=SHADOW)
    overlay.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(7)))
    draw.rounded_rectangle((x0, y0, x1, y1), radius=30, fill=PANEL)

    first_y = y0 + pad_y + round(current_font.size * 0.06)
    gap = round(current_font.size * 0.08)
    for row_index, row in enumerate(rows):
        x = (W - row_width(draw, row, current_font)) // 2
        y = first_y + row_index * row_height
        for piece in row:
            color = BLUE if piece in highlights else NAVY
            draw.text((x, y), piece, font=current_font, fill=color)
            x += text_width(draw, piece, current_font) + gap

    base.alpha_composite(overlay)
    return base.convert("RGB")


def contact_sheet(paths: list[Path]) -> None:
    columns, thumb_w, thumb_h, label_h = 3, 216, 384, 36
    rows = math.ceil(len(paths) / columns)
    sheet = Image.new("RGB", (columns * thumb_w, rows * (thumb_h + label_h)), (246, 248, 250))
    draw = ImageDraw.Draw(sheet)
    label_font = font(20)
    for index, path in enumerate(paths):
        x = (index % columns) * thumb_w
        y = (index // columns) * (thumb_h + label_h)
        sheet.paste(cover(Image.open(path), (thumb_w, thumb_h)), (x, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill=(255, 255, 255))
        draw.text((x + 8, y + thumb_h + 7), f"{index + 1:02d}", font=label_font, fill=NAVY)
    sheet.save(OUT / "contact_sheet_telop.png")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    outputs, manifest = [], []
    for index, (source_name, output_name, rows, highlights, position) in enumerate(FRAMES, start=1):
        source = BASE / source_name
        output = OUT / output_name
        draw_frame(Image.open(source), rows, highlights, position).save(output, quality=95)
        outputs.append(output)
        manifest.append({
            "index": index,
            "source": str(source.relative_to(ROOT)),
            "output": str(output.relative_to(ROOT)),
            "telop": rows,
            "highlights": sorted(highlights),
            "position": position,
            "font": str(FONT_PATH),
            "panel_opacity": "70%",
        })
    contact_sheet(outputs)
    (OUT / "telop_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(f"created {len(outputs)} telop frames")


if __name__ == "__main__":
    main()
