from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
INPUT_DIR = ROOT / "reel_assets" / "bone_density_series" / "artificial_hip_dxa_20261006_images"
OUTPUT_DIR = ROOT / "reel_assets" / "bone_density_series" / "artificial_hip_dxa_20261006_telop_frames"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"
SIZE = (1080, 1920)

# Each tuple is (text, emphasize_with_blue). Blue is limited to the keyword itself.
FRAMES = [
    (
        "01_hook_dxa_measurement.png",
        [
            [("人工股関節", True), ("があっても", False)],
            [("検査はできます", True)],
        ],
    ),
    (
        "02_dxa_lumbar_and_hip.png",
        [
            [("DXAは", False)],
            [("腰椎", True), ("・", False), ("股関節", True), ("を測定", False)],
        ],
    ),
    (
        "03_measurement_position.png",
        [
            [("人工股関節側", True), ("は", False)],
            [("通常評価に使いません", False)],
        ],
    ),
    (
        "04_position_check.png",
        [
            [("片側なら", False)],
            [("反対側", True), ("を測定", False)],
        ],
    ),
    (
        "05_calm_confirmation.png",
        [
            [("両側", True), ("なら", False)],
            [("股関節は測れません", False)],
        ],
    ),
    (
        "06_tell_radiologic_technologist.png",
        [
            [("診療放射線技師に", False)],
            [("左右", True), ("を伝える", False)],
        ],
    ),
    (
        "07_cta_space.png",
        [
            [("検査前に", False)],
            [("保存", True), ("しておく", False)],
        ],
    ),
]

NAVY = (16, 58, 88, 255)
BLUE = (42, 126, 194, 255)
BACKING = (255, 255, 255, 179)  # 70% opacity
# Center is the default. Only frames whose center band would cover a person's head move lower.
TELLOP_CENTER_Y = {1: 1280, 2: 1280, 3: 1280, 4: 1280}


def cover_to_size(path: Path) -> Image.Image:
    image = Image.open(path).convert("RGB")
    scale = max(SIZE[0] / image.width, SIZE[1] / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS
    )
    left = (resized.width - SIZE[0]) // 2
    top = (resized.height - SIZE[1]) // 2
    return resized.crop((left, top, left + SIZE[0], top + SIZE[1]))


def font_for(draw: ImageDraw.ImageDraw, lines, max_width=900) -> ImageFont.FreeTypeFont:
    for size in range(78, 43, -2):
        font = ImageFont.truetype(FONT_PATH, size=size)
        widths = []
        for line in lines:
            width = sum(draw.textlength(text, font=font) for text, _ in line)
            widths.append(width)
        if max(widths) <= max_width:
            return font
    return ImageFont.truetype(FONT_PATH, size=42)


def line_height(draw: ImageDraw.ImageDraw, font: ImageFont.FreeTypeFont) -> int:
    top, bottom = draw.textbbox((0, 0), "あいうえお", font=font)[1::2]
    return bottom - top


def draw_centered_telop(background: Image.Image, lines, frame_number: int) -> Image.Image:
    canvas = background.convert("RGBA")
    draw = ImageDraw.Draw(canvas, "RGBA")
    font = font_for(draw, lines)
    h = line_height(draw, font)
    line_gap = 20
    total_h = h * len(lines) + line_gap * (len(lines) - 1)
    center_y = TELLOP_CENTER_Y.get(frame_number, SIZE[1] // 2)
    y = center_y - total_h // 2
    line_widths = [sum(draw.textlength(text, font=font) for text, _ in line) for line in lines]
    box_width = max(line_widths) + 96
    box = (
        (SIZE[0] - box_width) // 2,
        y - 42,
        (SIZE[0] + box_width) // 2,
        y + total_h + 42,
    )
    draw.rounded_rectangle(box, radius=30, fill=BACKING)

    for line, width in zip(lines, line_widths):
        x = (SIZE[0] - width) / 2
        for text, emphasized in line:
            draw.text((x, y), text, font=font, fill=BLUE if emphasized else NAVY)
            x += draw.textlength(text, font=font)
        y += h + line_gap
    return canvas.convert("RGB")


def make_contact_sheet(outputs):
    thumb = (216, 384)
    sheet = Image.new("RGB", (thumb[0] * 4, (thumb[1] + 38) * 2), (245, 247, 250))
    draw = ImageDraw.Draw(sheet)
    label_font = ImageFont.truetype(FONT_PATH, size=20)
    for index, path in enumerate(outputs):
        image = Image.open(path).convert("RGB").resize(thumb, Image.Resampling.LANCZOS)
        x = (index % 4) * thumb[0]
        y = (index // 4) * (thumb[1] + 38)
        sheet.paste(image, (x, y))
        draw.text((x + 12, y + thumb[1] + 8), path.name, font=label_font, fill=(16, 58, 88))
    return sheet


def main():
    if not FONT_PATH.exists():
        raise FileNotFoundError(FONT_PATH)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    for number, (filename, lines) in enumerate(FRAMES, start=1):
        source = INPUT_DIR / filename
        if not source.exists():
            raise FileNotFoundError(source)
        frame = draw_centered_telop(cover_to_size(source), lines, number)
        output = OUTPUT_DIR / f"telop_{number:02d}.png"
        frame.save(output, quality=95)
        outputs.append(output)

    contact_sheet = OUTPUT_DIR / "_contact_sheet.png"
    make_contact_sheet(outputs).save(contact_sheet, quality=95)
    manifest = {
        "input_manifest": str(INPUT_DIR / "production_manifest.md"),
        "telop_frames": [str(path) for path in outputs],
        "contact_sheet": str(contact_sheet),
        "size": {"width": SIZE[0], "height": SIZE[1]},
        "style": {
            "font": str(FONT_PATH),
            "text": "dark navy with keyword-only blue emphasis",
            "backing": "white rounded rectangle at 70% opacity",
            "position": "center",
        },
        "note": "Audio and video generation are not included.",
    }
    (OUTPUT_DIR / "telop_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(contact_sheet)


if __name__ == "__main__":
    main()
