from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
SAMPLES = ROOT / "reel_assets" / "chest_xray_chin_rest_20260930_samples"
IMAGES = ROOT / "reel_assets" / "chest_xray_chin_rest_20260930_images"
OUT = ROOT / "reel_assets" / "chest_xray_chin_rest_20260930_telop_frames"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (16, 36, 55, 255)
BLUE = (0, 104, 150, 255)
PANEL = (255, 255, 255, 179)
SHADOW = (0, 0, 0, 38)


# One message per frame. Text stays horizontally centered; no lateral offset is used.
FRAMES = [
    (SAMPLES / "sample_01_hook_chin_rest_high_reference_v3.png", "telop_01_hook.png", [["なんでこんなに", "高い", "の？"]], {"高い"}, "top"),
    (IMAGES / "frame_02_no_need_to_force_chin_v2_no_text.png", "telop_02_no_force.png", [["無理に", "乗せなくて大丈夫"]], {"無理に"}, "top"),
    (SAMPLES / "sample_03_shoulders_against_bucky_reference_v4.png", "telop_03_chest_shoulders.png", [["胸と両肩を", "板へ"]], {"胸と両肩"}, "top"),
    (IMAGES / "frame_04_height_adjustment_v3_no_text.png", "telop_04_height.png", [["肺全体", "が入る高さに"]], {"肺全体"}, "top"),
    (IMAGES / "frame_05_height_explanation_v2_no_text.png", "telop_05_upper_lung.png", [["肺の上", "が切れることも"]], {"肺の上"}, "top"),
    (IMAGES / "frame_06_patient_speaks_up_v3_no_text.png", "telop_06_speak_up.png", [["つらいときは", "教えてください"]], set(), "top"),
    (IMAGES / "frame_07_alternative_position_consultation_v2_no_text.png", "telop_07_alternative.png", [["撮り方", "を変えることも"]], {"撮り方"}, "top"),
    (IMAGES / "frame_08_patient_reassured_exit_no_text.png", "telop_08_reassurance.png", [["顎が乗らなくても"]], set(), "center"),
    (IMAGES / "frame_09_cta_background_no_text.png", "telop_09_save_share.png", [["検査前に", "保存"]], {"保存"}, "center"),
]


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size)


def cover(image: Image.Image, size: tuple[int, int] = (W, H)) -> Image.Image:
    image = image.convert("RGB")
    scale = max(size[0] / image.width, size[1] / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    x = (resized.width - size[0]) // 2
    y = (resized.height - size[1]) // 2
    return resized.crop((x, y, x + size[0], y + size[1]))


def text_width(draw: ImageDraw.ImageDraw, text: str, used_font: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=used_font)
    return box[2] - box[0]


def line_width(draw: ImageDraw.ImageDraw, line: list[str], used_font: ImageFont.FreeTypeFont) -> int:
    gap = round(used_font.size * 0.08)
    return sum(text_width(draw, part, used_font) for part in line) + gap * (len(line) - 1)


def choose_font(draw: ImageDraw.ImageDraw, lines: list[list[str]]) -> ImageFont.FreeTypeFont:
    for size in range(68, 39, -2):
        candidate = font(size)
        if max(line_width(draw, line, candidate) for line in lines) <= 820:
            return candidate
    return font(38)


def panel_y(panel_height: int, position: str) -> int:
    if position == "top":
        return 250  # Below Instagram's top UI safe zone.
    if position == "bottom":
        return H - panel_height - 280
    return (H - panel_height) // 2


def draw_frame(source: Image.Image, lines: list[list[str]], highlights: set[str], position: str) -> Image.Image:
    base = cover(source).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    used_font = choose_font(draw, lines)
    line_height = round(used_font.size * 1.18)
    pad_x, pad_y = 58, 36
    panel_width = min(930, max(line_width(draw, line, used_font) for line in lines) + pad_x * 2)
    panel_height = line_height * len(lines) + pad_y * 2
    x0 = (W - panel_width) // 2
    y0 = panel_y(panel_height, position)
    x1, y1 = x0 + panel_width, y0 + panel_height

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((x0 + 6, y0 + 8, x1 + 6, y1 + 8), radius=30, fill=SHADOW)
    overlay.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(7)))
    draw.rounded_rectangle((x0, y0, x1, y1), radius=30, fill=PANEL)

    y = y0 + pad_y + round(used_font.size * 0.06)
    gap = round(used_font.size * 0.08)
    for line in lines:
        x = (W - line_width(draw, line, used_font)) // 2
        for part in line:
            draw.text((x, y), part, font=used_font, fill=BLUE if part in highlights else NAVY)
            x += text_width(draw, part, used_font) + gap
        y += line_height

    base.alpha_composite(overlay)
    return base.convert("RGB")


def make_contact_sheet(outputs: list[Path]) -> None:
    thumb_w, thumb_h, label_h, columns = 216, 384, 36, 3
    rows = math.ceil(len(outputs) / columns)
    sheet = Image.new("RGB", (columns * thumb_w, rows * (thumb_h + label_h)), (246, 248, 250))
    draw = ImageDraw.Draw(sheet)
    label_font = font(20)
    for index, path in enumerate(outputs):
        x = (index % columns) * thumb_w
        y = (index // columns) * (thumb_h + label_h)
        sheet.paste(cover(Image.open(path), (thumb_w, thumb_h)), (x, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill=(255, 255, 255))
        draw.text((x + 8, y + thumb_h + 7), f"{index + 1:02d}", font=label_font, fill=NAVY)
    sheet.save(OUT / "contact_sheet_telop_frames.png")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    outputs, manifest = [], []
    for index, (source, output_name, lines, highlights, position) in enumerate(FRAMES, start=1):
        if not source.exists():
            raise FileNotFoundError(source)
        output = OUT / output_name
        draw_frame(Image.open(source), lines, highlights, position).save(output, quality=95)
        outputs.append(output)
        manifest.append({
            "index": index,
            "source": str(source.relative_to(ROOT)),
            "output": str(output.relative_to(ROOT)),
            "text": ["".join(line) for line in lines],
            "highlights": sorted(highlights),
            "position": position,
            "font": str(FONT_PATH),
            "panel_opacity": "70%",
        })
    make_contact_sheet(outputs)
    (OUT / "telop_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(f"created {len(outputs)} telop frames")


if __name__ == "__main__":
    main()
