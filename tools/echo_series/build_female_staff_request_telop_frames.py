from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
BASE = ROOT / "reel_assets" / "echo_series" / "07_female_staff_request_v1" / "images"
OUT = ROOT / "reel_assets" / "echo_series" / "07_female_staff_request_v1" / "telop_frames"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
PANEL_W = 760
NAVY = (12, 34, 58, 255)
BLUE = (0, 104, 150, 255)
PANEL = (255, 255, 255, 178)  # White at 70% opacity.
PANEL_EDGE = (255, 255, 255, 220)
SHADOW = (0, 0, 0, 42)


FRAMES = [
    ("image_01_waiting_room_preference.png", "telop_01.png", [["エコーは"], ["女性", "の方がいい…"]], {"女性"}, "center"),
    ("image_02_not_selfish.png", "telop_02.png", [["希望", "を伝えても"], ["わがままではありません"]], {"希望"}, "center"),
    ("image_03_reception_request.png", "telop_03.png", [["予約時", "か", "受付", "で"], ["伝えて大丈夫です"]], {"予約時", "受付"}, "center"),
    ("image_04_simple_request.png", "telop_04.png", [["女性", "の方に"], ["お願いできますか"]], {"女性"}, "center"),
    ("image_05_facility_difference.png", "telop_05.png", [["対応できるかは"], ["施設", "によって異なります"]], {"施設"}, "center"),
    ("image_06_schedule_consideration.png", "telop_06.png", [["人数や時間帯、"], ["検査内容", "によって"], ["難しいこともあります"]], {"検査内容"}, "center"),
    ("image_07_contact_in_advance.png", "telop_07.png", [["事前", "に伝えると"], ["調整しやすくなります"]], {"事前"}, "top"),
    ("image_08_consult_anyway.png", "telop_08.png", [["希望に添えない時も"], ["まず", "相談", "して大丈夫です"]], {"相談"}, "center"),
    ("image_09_save_before_appointment.png", "telop_09.png", [["予約前に"], ["見返せるよう"], ["保存", "してください"]], {"保存"}, "top"),
    ("image_10_follow_cta.png", "telop_10.png", [["検査前に役立つ情報"], ["フォロー", "で見返せます"]], {"フォロー"}, "center"),
]


def font(size: int) -> ImageFont.FreeTypeFont:
    if not FONT_PATH.exists():
        raise FileNotFoundError(FONT_PATH)
    return ImageFont.truetype(str(FONT_PATH), size)


def text_width(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=fnt)
    return bbox[2] - bbox[0]


def line_width(draw: ImageDraw.ImageDraw, line: list[str], fnt: ImageFont.FreeTypeFont) -> int:
    gap = int(fnt.size * 0.04)
    return sum(text_width(draw, part, fnt) for part in line) + gap * (len(line) - 1)


def fit_font(draw: ImageDraw.ImageDraw, lines: list[list[str]]) -> tuple[ImageFont.FreeTypeFont, int]:
    for size in range(72, 43, -2):
        fnt = font(size)
        if max(line_width(draw, line, fnt) for line in lines) <= 600:
            return fnt, int(size * 1.2)
    return font(42), 51


def normalize_canvas(image: Image.Image) -> Image.Image:
    return image.convert("RGB").resize((W, H), Image.Resampling.LANCZOS)


def box_y(position: str, height: int) -> int:
    if position == "top":
        return 176
    return (H - height) // 2


def draw_telop(image: Image.Image, lines: list[list[str]], highlights: set[str], position: str) -> tuple[Image.Image, list[int]]:
    image = normalize_canvas(image).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    fnt, line_h = fit_font(draw, lines)
    pad_x, pad_y = 52, 34
    height = line_h * len(lines) + pad_y * 2
    x0 = (W - PANEL_W) // 2
    y0 = box_y(position, height)
    x1, y1 = x0 + PANEL_W, y0 + height

    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((x0 + 6, y0 + 8, x1 + 6, y1 + 8), radius=28, fill=SHADOW)
    overlay.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(7)))
    draw.rounded_rectangle((x0, y0, x1, y1), radius=28, fill=PANEL)
    draw.rounded_rectangle((x0 + 7, y0 + 7, x1 - 7, y1 - 7), radius=22, outline=PANEL_EDGE, width=4)

    first_y = y0 + pad_y + int(fnt.size * 0.05)
    gap = int(fnt.size * 0.04)
    for row, line in enumerate(lines):
        x = (W - line_width(draw, line, fnt)) // 2
        y = first_y + row * line_h
        for part in line:
            draw.text((x, y), part, font=fnt, fill=BLUE if part in highlights else NAVY)
            x += text_width(draw, part, fnt) + gap

    image.alpha_composite(overlay)
    return image.convert("RGB"), [x0, y0, x1, y1]


def make_contact_sheet(paths: list[Path]) -> Path:
    thumb_w, thumb_h, label_h, cols = 216, 384, 36, 5
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (246, 248, 250))
    label_font = font(20)
    draw = ImageDraw.Draw(sheet)
    for index, path in enumerate(paths):
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (index % cols) * thumb_w
        y = (index // cols) * (thumb_h + label_h)
        sheet.paste(image, (x + (thumb_w - image.width) // 2, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill=(255, 255, 255))
        draw.text((x + 8, y + thumb_h + 7), f"{index + 1:02d}", font=label_font, fill=NAVY)
    contact = OUT / "contact_sheet_telop_frames.png"
    sheet.save(contact)
    return contact


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    outputs, manifest = [], []
    for index, (source_name, output_name, lines, highlights, position) in enumerate(FRAMES, start=1):
        source = BASE / source_name
        output = OUT / output_name
        image, box = draw_telop(Image.open(source), lines, highlights, position)
        image.save(output, quality=95)
        outputs.append(output)
        manifest.append({
            "index": index,
            "source": str(source.relative_to(ROOT)),
            "output": str(output.relative_to(ROOT)),
            "telop": ["".join(line) for line in lines],
            "highlights": sorted(highlights),
            "position": position,
            "box": box,
            "x_center": (box[0] + box[2]) // 2,
            "font": str(FONT_PATH),
            "panel_opacity": "70%",
        })

    contact = make_contact_sheet(outputs)
    (OUT / "telop_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(f"created {len(outputs)} telop frames")
    print(contact)


if __name__ == "__main__":
    main()
