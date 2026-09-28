from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
BASE = ROOT / "reel_assets" / "xray_wait_order_20260923_images"
OUT = ROOT / "reel_assets" / "xray_wait_order_20260923_telop_frames"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"
CONTACT = OUT / "contact_sheet_telop.png"
TEXTS = OUT / "telop_texts.txt"
MANIFEST = OUT / "telop_manifest.json"

W, H = 1080, 1920
NAVY = (16, 36, 55, 255)
BLUE = (0, 104, 150, 255)
PANEL = (255, 255, 255, 179)  # 70% opacity
SHADOW = (0, 0, 0, 38)


# One message per frame. Every telop is horizontally centered; only upper,
# center, and lower positions are allowed. Upper is used when a centered box
# would cover the patient or the CTA image.
FRAMES = [
    {
        "src": "frame_01_waiting_order.png",
        "out": "telop_01_waiting_order.png",
        "lines": [["後から来た人が先に…"], ["私、", "忘れられてる？"]],
        "highlights": {"忘れられてる？"},
        "position": "center",
    },
    {
        "src": "frame_02_check_appointment_time.png",
        "out": "telop_02_check_appointment_time.png",
        "lines": [["まずは"], ["予約票", "の時間を確認"]],
        "highlights": {"予約票"},
        "position": "center",
    },
    {
        "src": "frame_03_early_arrival_time_check.png",
        "out": "telop_03_early_arrival_time_check.png",
        "lines": [["早く着いても"], ["予約時間前", "なら待つことも"]],
        "highlights": {"予約時間前"},
        "position": "center",
    },
    {
        "src": "frame_04_different_exam_rooms.png",
        "out": "telop_04_different_exam_rooms.png",
        "lines": [["検査ごとに"], ["予約枠", "や部屋が違います"]],
        "highlights": {"予約枠", "部屋"},
        "position": "center",
    },
    {
        "src": "frame_05_order_may_vary.png",
        "out": "telop_05_order_may_vary.png",
        "lines": [["呼ばれる順番が"], ["前後する", "こともあります"]],
        "highlights": {"前後する"},
        "position": "center",
    },
    {
        "src": "frame_06_go_to_reception.png",
        "out": "telop_06_go_to_reception.png",
        "lines": [["不安な時は"], ["受付", "へ確認して大丈夫"]],
        "highlights": {"受付", "大丈夫"},
        "position": "center",
    },
    {
        "src": "frame_07_polite_reception_question.png",
        "out": "telop_07_polite_reception_question.png",
        "lines": [["○時の予約ですが"], ["こちらで待っていて", "大丈夫ですか？"]],
        "highlights": {"大丈夫ですか？"},
        "position": "center",
    },
    {
        "src": "frame_08_save_cta_background.png",
        "out": "telop_08_save_cta.png",
        "lines": [["受付で確認するときに"], ["見返せるよう", "保存"]],
        "highlights": {"保存"},
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


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def line_width(draw: ImageDraw.ImageDraw, line: list[str], font: ImageFont.FreeTypeFont) -> int:
    gap = round(font.size * 0.08)
    return sum(text_width(draw, item, font) for item in line) + gap * (len(line) - 1)


def fit_font(draw: ImageDraw.ImageDraw, lines: list[list[str]]) -> ImageFont.FreeTypeFont:
    for size in range(66, 39, -2):
        candidate = load_font(size)
        if max(line_width(draw, line, candidate) for line in lines) <= 790:
            return candidate
    return load_font(38)


def telop_y(position: str, box_height: int) -> int:
    if position == "top":
        return 180
    if position == "bottom":
        return H - 260 - box_height
    return (H - box_height) // 2


def draw_telop(source: Image.Image, frame: dict) -> Image.Image:
    base = cover(source).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    lines = frame["lines"]
    font = fit_font(draw, lines)
    line_height = round(font.size * 1.16)
    pad_x, pad_y = 56, 34
    box_width = min(920, max(line_width(draw, line, font) for line in lines) + pad_x * 2)
    box_height = line_height * len(lines) + pad_y * 2
    x0 = (W - box_width) // 2
    y0 = telop_y(frame["position"], box_height)
    x1, y1 = x0 + box_width, y0 + box_height

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((x0 + 6, y0 + 8, x1 + 6, y1 + 8), radius=30, fill=SHADOW)
    overlay.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(7)))
    draw.rounded_rectangle((x0, y0, x1, y1), radius=30, fill=PANEL)

    first_y = y0 + pad_y + round(font.size * 0.06)
    gap = round(font.size * 0.08)
    for row, line in enumerate(lines):
        width = line_width(draw, line, font)
        x = (W - width) // 2
        y = first_y + row * line_height
        for item in line:
            color = BLUE if item in frame["highlights"] else NAVY
            draw.text((x, y), item, font=font, fill=color)
            x += text_width(draw, item, font) + gap

    base.alpha_composite(overlay)
    return base.convert("RGB")


def make_contact_sheet(paths: list[Path]) -> None:
    columns = 4
    thumb_w, thumb_h, label_h = 216, 384, 36
    rows = math.ceil(len(paths) / columns)
    sheet = Image.new("RGB", (columns * thumb_w, rows * (thumb_h + label_h)), (246, 248, 250))
    draw = ImageDraw.Draw(sheet)
    label_font = load_font(20)
    for index, path in enumerate(paths):
        x = (index % columns) * thumb_w
        y = (index // columns) * (thumb_h + label_h)
        sheet.paste(cover(Image.open(path), (thumb_w, thumb_h)), (x, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill=(255, 255, 255))
        draw.text((x + 8, y + thumb_h + 7), f"{index + 1:02d}", font=label_font, fill=NAVY)
    sheet.save(CONTACT)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    manifest = []
    text_lines = []
    for index, frame in enumerate(FRAMES, start=1):
        source = BASE / frame["src"]
        output = OUT / frame["out"]
        if not source.exists():
            raise FileNotFoundError(source)
        draw_telop(Image.open(source), frame).save(output, quality=95)
        outputs.append(output)
        text_lines.append(f"{index:02d}. {' / '.join(''.join(line) for line in frame['lines'])}")
        manifest.append(
            {
                "index": index,
                "source": str(source.relative_to(ROOT)),
                "output": str(output.relative_to(ROOT)),
                "telop": frame["lines"],
                "highlights": sorted(frame["highlights"]),
                "position": frame["position"],
                "font": str(FONT_PATH),
                "panel_opacity": "70%",
            }
        )
    make_contact_sheet(outputs)
    TEXTS.write_text("\n".join(text_lines) + "\n", encoding="utf-8-sig")
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(f"created {len(outputs)} telop frames")
    print(OUT)
    print(CONTACT)


if __name__ == "__main__":
    main()
