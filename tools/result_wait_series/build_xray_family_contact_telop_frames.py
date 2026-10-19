from pathlib import Path
import json
import math
import re

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
MANIFEST = ROOT / "reel_assets" / "xray_family_contact_20261012_samples" / "production_manifest.md"
OUT = ROOT / "reel_assets" / "xray_family_contact_20261012_telop_frames"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"
CONTACT = OUT / "contact_sheet_telop.png"
TEXTS = OUT / "telop_texts.txt"
TELOP_MANIFEST = OUT / "telop_manifest.json"

W, H = 1080, 1920
NAVY = (16, 36, 55, 255)
BLUE = (0, 104, 150, 255)
PANEL = (255, 255, 255, 179)
SHADOW = (0, 0, 0, 38)


# X is always centered. Center is preferred; top or bottom is used only when
# a centered panel would cover a face, hair, or head.
FRAMES = [
    {
        "out": "telop_01_family_ok.png",
        "lines": [[("レントゲン後", "blue"), "も"], ["家族に会って", ("大丈夫", "blue"), "です"]],
        "position": "center",
    },
    {
        "out": "telop_02_no_radiation_after.png",
        "lines": [[("撮影後", "blue"), "、体から"], ["放射線は", ("出ません", "blue")]],
        "position": "center",
    },
    {
        "out": "telop_03_check_guidance.png",
        "lines": [[("案内", "blue"), "があれば確認して"], [("普段どおり", "blue"), "で大丈夫"]],
        "position": "center",
    },
    {
        "out": "telop_04_family_concern.png",
        "lines": [["家族に近づいていい？"], [("気になります", "blue"), "よね"]],
        "position": "center",
    },
    {
        "out": "telop_05_during_exposure_only.png",
        "lines": [["放射線が出るのは"], [("撮影している間", "blue"), "だけ"]],
        "position": "center",
    },
    {
        "out": "telop_06_hug_is_ok.png",
        "lines": [[("抱っこ", "blue"), "しても"], ["そばにいても", ("大丈夫", "blue")]],
        "position": "top",
    },
    {
        "out": "telop_07_special_exam_guidance.png",
        "lines": [[("放射性の薬", "blue"), "を使う検査は"], [("案内", "blue"), "に従ってください"]],
        "position": "bottom",
    },
    {
        "out": "telop_08_family_time.png",
        "lines": [["帰ったら"], [("いつもどおり", "blue"), "家族と一緒に"]],
        "position": "top",
    },
    {
        "out": "telop_09_phrase_for_family.png",
        "lines": [["「", ("レントゲン後", "blue"), "、"], ["体から放射線は出ないよ」"]],
        "position": "top",
    },
    {
        "out": "telop_10_save_cta.png",
        "lines": [["家族に聞かれたときのために"], [("保存", "blue"), "しておいてください"]],
        "position": "top",
    },
]


def load_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size)


def cover(image: Image.Image, size: tuple[int, int] = (W, H)) -> Image.Image:
    image = image.convert("RGB")
    scale = max(size[0] / image.width, size[1] / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = (resized.width - size[0]) // 2
    top = (resized.height - size[1]) // 2
    return resized.crop((left, top, left + size[0], top + size[1]))


def segment_text(segment) -> str:
    return segment[0] if isinstance(segment, tuple) else segment


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def line_width(draw: ImageDraw.ImageDraw, line: list, font: ImageFont.FreeTypeFont) -> int:
    return sum(text_width(draw, segment_text(segment), font) for segment in line)


def fit_font(draw: ImageDraw.ImageDraw, lines: list[list]) -> ImageFont.FreeTypeFont:
    for size in range(66, 39, -2):
        candidate = load_font(size)
        if max(line_width(draw, line, candidate) for line in lines) <= 820:
            return candidate
    return load_font(38)


def telop_y(position: str, box_height: int) -> int:
    if position == "top":
        return 260
    if position == "bottom":
        return H - 300 - box_height
    return (H - box_height) // 2


def draw_telop(source: Image.Image, frame: dict) -> Image.Image:
    base = cover(source).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    lines = frame["lines"]
    font = fit_font(draw, lines)
    line_height = round(font.size * 1.18)
    pad_x, pad_y = 56, 34
    box_width = min(940, max(line_width(draw, line, font) for line in lines) + pad_x * 2)
    box_height = line_height * len(lines) + pad_y * 2
    x0 = (W - box_width) // 2
    y0 = telop_y(frame["position"], box_height)
    x1, y1 = x0 + box_width, y0 + box_height

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((x0 + 6, y0 + 8, x1 + 6, y1 + 8), radius=30, fill=SHADOW)
    overlay.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(7)))
    draw.rounded_rectangle((x0, y0, x1, y1), radius=30, fill=PANEL)

    first_y = y0 + pad_y + round(font.size * 0.04)
    for row, line in enumerate(lines):
        width = line_width(draw, line, font)
        x = (W - width) // 2
        y = first_y + row * line_height
        for segment in line:
            if isinstance(segment, tuple):
                text, color_name = segment
                color = BLUE if color_name == "blue" else NAVY
            else:
                text, color = segment, NAVY
            draw.text((x, y), text, font=font, fill=color)
            x += text_width(draw, text, font)

    base.alpha_composite(overlay)
    return base.convert("RGB")


def approved_paths_from_manifest() -> list[Path]:
    pattern = re.compile(r"^\|\s*(\d{2})\s*\|\s*`([^`]+)`\s*\|")
    approved = []
    for line in MANIFEST.read_text(encoding="utf-8-sig").splitlines():
        match = pattern.match(line)
        if match:
            approved.append((int(match.group(1)), Path(match.group(2))))
    approved.sort(key=lambda item: item[0])
    return [path.resolve() for _, path in approved]


def verify_source_lock() -> list[Path]:
    sources = approved_paths_from_manifest()
    if len(sources) != len(FRAMES):
        raise RuntimeError("production_manifest.md count differs from FRAMES")
    missing = [path for path in sources if not path.exists()]
    if missing:
        raise FileNotFoundError(missing)
    return sources


def make_contact_sheet(paths: list[Path]) -> None:
    columns = 5
    thumb_w, thumb_h, label_h = 216, 384, 36
    rows = math.ceil(len(paths) / columns)
    sheet = Image.new("RGB", (columns * thumb_w, rows * (thumb_h + label_h)), (246, 248, 250))
    draw = ImageDraw.Draw(sheet)
    label_font = load_font(20)
    for index, path in enumerate(paths):
        x = (index % columns) * thumb_w
        y = (index // columns) * (thumb_h + label_h)
        with Image.open(path) as image:
            sheet.paste(cover(image, (thumb_w, thumb_h)), (x, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill=(255, 255, 255))
        draw.text((x + 8, y + thumb_h + 7), f"{index + 1:02d}", font=label_font, fill=NAVY)
    sheet.save(CONTACT)


def plain_lines(lines: list[list]) -> list[str]:
    return ["".join(segment_text(segment) for segment in line) for line in lines]


def main() -> None:
    sources = verify_source_lock()
    OUT.mkdir(parents=True, exist_ok=True)
    outputs = []
    telop_manifest = []
    text_lines = []

    for index, (frame, source) in enumerate(zip(FRAMES, sources), start=1):
        output = OUT / frame["out"]
        with Image.open(source) as image:
            draw_telop(image, frame).save(output, quality=95)
        outputs.append(output)
        display_lines = plain_lines(frame["lines"])
        text_lines.append(f"{index:02d}. {' / '.join(display_lines)}")
        highlights = [segment[0] for line in frame["lines"] for segment in line if isinstance(segment, tuple)]
        telop_manifest.append(
            {
                "cut": index,
                "source": str(source),
                "output": str(output.resolve()),
                "telop": display_lines,
                "highlights": highlights,
                "position": frame["position"],
                "x_alignment": "center",
                "font": str(FONT_PATH),
                "panel_opacity": "70%",
            }
        )

    make_contact_sheet(outputs)
    TEXTS.write_text("\n".join(text_lines) + "\n", encoding="utf-8-sig")
    TELOP_MANIFEST.write_text(json.dumps(telop_manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(f"source lock verified: {len(sources)} images")
    print(f"created {len(outputs)} telop frames")
    print(CONTACT)


if __name__ == "__main__":
    main()
