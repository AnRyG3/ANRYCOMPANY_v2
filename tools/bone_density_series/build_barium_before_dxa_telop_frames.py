from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
SOURCE_DIR = ROOT / "reel_assets" / "bone_density_series" / "barium_before_dxa_20261013_images"
MANIFEST = SOURCE_DIR / "production_manifest.md"
OUT = ROOT / "reel_assets" / "bone_density_series" / "barium_before_dxa_20261013_telop_frames"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (16, 36, 55, 255)
BLUE = (0, 104, 150, 255)
PANEL = (255, 255, 255, 179)  # 70% opacity
SHADOW = (0, 0, 0, 38)


FRAMES = [
    {
        "source": "01_booking_call_no_text.png",
        "output": "telop_01.png",
        "lines": [[("バリウム検査", True), ("の日を", False)], [("予約時", True), ("に伝えて", False)]],
        "position": "center",
    },
    {
        "source": "02_reception_phone_no_text.png",
        "output": "telop_02.png",
        "lines": [[("あける日数は", False)], [("施設", True), ("によって異なります", False)]],
        "position": "center",
    },
    {
        "source": "03_ask_booking_office_no_text.png",
        "output": "telop_03.png",
        "lines": [[("そのまま受けられるか", False)], [("予約先", True), ("に確認を", False)]],
        "position": "center",
    },
    {
        "source": "04_gentle_question_no_text.png",
        "output": "telop_04.png",
        "lines": [[("骨密度検査", True), ("を", False)], [("受けていいのかな？", False)]],
        "position": "center",
    },
    {
        "source": "05_dxa_room_no_text.png",
        "output": "telop_05.png",
        "lines": [[("残った", False), ("バリウム", True), ("が", False)], [("測定", True), ("に影響することも", False)]],
        "position": "center",
    },
    {
        "source": "06_dxa_room_alt_no_text.png",
        "output": "telop_06.png",
        "lines": [[("体から出る時間には", False)], [("個人差", True), ("があります", False)]],
        "position": "center",
    },
    {
        "source": "07_facility_confirmation_no_text.png",
        "output": "telop_07.png",
        "lines": [[("日数をあけるかは", False)], [("施設の案内", True), ("に沿って", False)]],
        "position": "center",
    },
    {
        "source": "08_approximate_date_no_text.png",
        "output": "telop_08.png",
        "lines": [[("日にちが曖昧でも", False)], [("「先週あたり」", True), ("と伝えて", False)]],
        "position": "center",
    },
    {
        "source": "09_booking_phrase_space_no_text.png",
        "output": "telop_09.png",
        "lines": [
            [("「○日に", False), ("バリウム検査", True), ("を", False)],
            [("受けましたが", False)],
            [("骨密度検査", True), ("は受けられますか？」", False)],
        ],
        "position": "top",
    },
    {
        "source": "10_save_cta_space_no_text.png",
        "output": "telop_10.png",
        "lines": [[("次の予約前に", False)], [("見返せるよう", False), ("保存", True)]],
        "position": "center",
    },
]


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size)


def cover(image: Image.Image, size: tuple[int, int] = (W, H)) -> Image.Image:
    image = image.convert("RGB")
    scale = max(size[0] / image.width, size[1] / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)),
        Image.Resampling.LANCZOS,
    )
    x = (resized.width - size[0]) // 2
    y = (resized.height - size[1]) // 2
    return resized.crop((x, y, x + size[0], y + size[1]))


def segment_width(draw: ImageDraw.ImageDraw, text: str, used_font: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=used_font)
    return box[2] - box[0]


def line_width(
    draw: ImageDraw.ImageDraw,
    line: list[tuple[str, bool]],
    used_font: ImageFont.FreeTypeFont,
) -> int:
    return sum(segment_width(draw, text, used_font) for text, _ in line)


def choose_font(
    draw: ImageDraw.ImageDraw,
    lines: list[list[tuple[str, bool]]],
) -> ImageFont.FreeTypeFont:
    for size in range(68, 41, -2):
        candidate = font(size)
        if max(line_width(draw, line, candidate) for line in lines) <= 850:
            return candidate
    return font(40)


def panel_y(panel_height: int, position: str) -> int:
    positions = {
        "top": 260,
        "center": (H - panel_height) // 2,
        "bottom": H - panel_height - 300,
    }
    return positions[position]


def draw_frame(
    source: Image.Image,
    lines: list[list[tuple[str, bool]]],
    position: str,
) -> Image.Image:
    base = cover(source).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    used_font = choose_font(draw, lines)
    line_height = round(used_font.size * 1.22)
    pad_x, pad_y = 58, 38
    panel_width = min(
        950,
        max(line_width(draw, line, used_font) for line in lines) + pad_x * 2,
    )
    panel_height = line_height * len(lines) + pad_y * 2
    x0 = (W - panel_width) // 2
    y0 = panel_y(panel_height, position)
    x1, y1 = x0 + panel_width, y0 + panel_height

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(
        (x0 + 6, y0 + 8, x1 + 6, y1 + 8),
        radius=30,
        fill=SHADOW,
    )
    overlay.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(7)))
    draw.rounded_rectangle((x0, y0, x1, y1), radius=30, fill=PANEL)

    y = y0 + pad_y + round(used_font.size * 0.04)
    for line in lines:
        x = (W - line_width(draw, line, used_font)) // 2
        for text, emphasized in line:
            draw.text(
                (x, y),
                text,
                font=used_font,
                fill=BLUE if emphasized else NAVY,
            )
            x += segment_width(draw, text, used_font)
        y += line_height

    base.alpha_composite(overlay)
    return base.convert("RGB")


def make_contact_sheet(outputs: list[Path]) -> Path:
    thumb_w, thumb_h, label_h, columns = 270, 480, 40, 3
    rows = math.ceil(len(outputs) / columns)
    sheet = Image.new(
        "RGB",
        (columns * thumb_w, rows * (thumb_h + label_h)),
        (246, 248, 250),
    )
    draw = ImageDraw.Draw(sheet)
    label_font = font(22)
    for index, path in enumerate(outputs):
        x = (index % columns) * thumb_w
        y = (index // columns) * (thumb_h + label_h)
        with Image.open(path) as image:
            sheet.paste(cover(image, (thumb_w, thumb_h)), (x, y))
        draw.rectangle(
            (x, y + thumb_h, x + thumb_w, y + thumb_h + label_h),
            fill=(255, 255, 255),
        )
        draw.text(
            (x + 10, y + thumb_h + 6),
            f"CUT {index + 1:02d}",
            font=label_font,
            fill=NAVY,
        )
    output = OUT / "contact_sheet_telop_frames.png"
    sheet.save(output)
    return output


def verify_locked_sources() -> None:
    if not FONT_PATH.exists():
        raise FileNotFoundError(FONT_PATH)
    if not MANIFEST.exists():
        raise FileNotFoundError(MANIFEST)
    manifest_text = MANIFEST.read_text(encoding="utf-8-sig")
    if len(FRAMES) != 10:
        raise ValueError(f"Expected 10 cuts, found {len(FRAMES)}")
    if len({frame["source"] for frame in FRAMES}) != 10:
        raise ValueError("Duplicate source image in frame list")
    for frame in FRAMES:
        source = SOURCE_DIR / frame["source"]
        if not source.exists():
            raise FileNotFoundError(source)
        if str(source) not in manifest_text:
            raise ValueError(f"Source is not locked in production_manifest.md: {source}")
        if frame["position"] not in {"top", "center", "bottom"}:
            raise ValueError(f"Invalid telop position: {frame['position']}")


def main() -> None:
    verify_locked_sources()
    OUT.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    telop_manifest = []

    for index, frame in enumerate(FRAMES, start=1):
        source = SOURCE_DIR / frame["source"]
        output = OUT / frame["output"]
        with Image.open(source) as image:
            draw_frame(image, frame["lines"], frame["position"]).save(output, quality=95)
        outputs.append(output)
        telop_manifest.append(
            {
                "cut": index,
                "source": str(source),
                "output": str(output),
                "text": ["".join(text for text, _ in line) for line in frame["lines"]],
                "highlight_words": [
                    text
                    for line in frame["lines"]
                    for text, emphasized in line
                    if emphasized
                ],
                "position": frame["position"],
                "x_axis": "center",
                "font": str(FONT_PATH),
                "panel_opacity": "70%",
            }
        )

    contact_sheet = make_contact_sheet(outputs)
    manifest_output = OUT / "telop_manifest.json"
    manifest_output.write_text(
        json.dumps(
            {
                "input_manifest": str(MANIFEST),
                "frames": telop_manifest,
                "contact_sheet": str(contact_sheet),
                "size": {"width": W, "height": H},
                "style": {
                    "font": str(FONT_PATH),
                    "text": "dark navy with keyword-only blue emphasis",
                    "backing": "white rounded rectangle at 70% opacity",
                    "position": "X-axis centered; top, center, or bottom only",
                },
                "note": "Audio and video generation are not included.",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8-sig",
    )
    print(f"created {len(outputs)} telop frames")
    print(contact_sheet)
    print(manifest_output)


if __name__ == "__main__":
    main()
