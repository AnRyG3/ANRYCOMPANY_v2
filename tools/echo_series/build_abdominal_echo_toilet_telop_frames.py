from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
BASE = ROOT / "reel_assets" / "echo_series" / "06_toilet_before_abdominal_echo_v1" / "images"
OUT = ROOT / "reel_assets" / "echo_series" / "06_toilet_before_abdominal_echo_v1" / "telop_frames"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
PANEL_W = 760
NAVY = (12, 34, 58, 255)
BLUE = (0, 104, 150, 255)
PANEL = (255, 255, 255, 240)
PANEL_EDGE = (255, 255, 255, 255)
SHADOW = (0, 0, 0, 42)


FRAMES = [
    ("frame_01_waiting_room_hesitation.png", "telop_01.png", [["腹部エコー", "前"], ["トイレ、今行っていい？"]], {"腹部エコー"}, "center"),
    ("frame_02_reception_question.png", "telop_02.png", [["行きたいけれど"], ["検査前", "だし…"]], {"検査前"}, "center"),
    ("frame_03_walk_to_reception.png", "telop_03.png", [["迷ったら"], ["先にひとこと"]], {"迷ったら", "先に"}, "center"),
    ("frame_04_ultrasound_room.png", "telop_04.png", [["膀胱", "などを見るときは"], ["尿", "がある方が"], ["見やすいことも"]], {"膀胱", "尿"}, "center"),
    ("frame_05_check_appointment.png", "telop_05.png", [["尿", "のたまりが"], ["影響しにくい"], ["部位もあります"]], {"尿"}, "center"),
    ("frame_06_preparation_varies.png", "telop_06.png", [["準備は"], ["検査内容", "や", "施設", "で"], ["変わります"]], {"検査内容", "施設"}, "center"),
    ("frame_07_ask_reception.png", "telop_07.png", [["トイレ、今行っても"], ["大丈夫", "ですか？"]], {"大丈夫"}, "center"),
    ("frame_08_reassured_waiting.png", "telop_08.png", [["つらい", "ほど"], ["我慢", "しないでください"]], {"つらい", "我慢"}, "center"),
    ("frame_09_save_for_later.png", "telop_09.png", [["検査前日に"], ["見返せるよう"], ["保存", "しておいてください"]], {"保存"}, "top"),
    ("frame_10_closing_waiting_room.png", "telop_10.png", [["次の検査前にも"], ["フォロー", "で見返せます"]], {"フォロー"}, "center"),
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
        line_h = int(size * 1.2)
        if max(line_width(draw, line, fnt) for line in lines) <= 600:
            return fnt, line_h
    return font(42), 51


def box_y(position: str, height: int) -> int:
    if position == "top":
        return 176
    if position == "bottom":
        return H - height - 240
    return (H - height) // 2


def normalize_canvas(image: Image.Image) -> Image.Image:
    """Scale the generated 9:16 source to the fixed Reel canvas before positioning text."""
    if image.size == (W, H):
        return image
    return image.convert("RGB").resize((W, H), Image.Resampling.LANCZOS)


def draw_telop(image: Image.Image, lines: list[list[str]], highlights: set[str], position: str) -> tuple[Image.Image, list[int]]:
    image = normalize_canvas(image).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    fnt, line_h = fit_font(draw, lines)
    pad_x, pad_y = 52, 34
    width = PANEL_W
    height = line_h * len(lines) + pad_y * 2
    x0 = (W - width) // 2  # Fixed at x=60; box center is always x=540.
    y0 = box_y(position, height)
    x1, y1 = x0 + width, y0 + height

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
            color = BLUE if part in highlights else NAVY
            draw.text((x, y), part, font=fnt, fill=color)
            x += text_width(draw, part, fnt) + gap

    image.alpha_composite(overlay)
    return image.convert("RGB"), [x0, y0, x1, y1]


def make_contact_sheet(paths: list[Path]) -> Path:
    thumb_w, thumb_h, label_h, cols = 216, 384, 36, 5
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (246, 248, 250))
    label_font = font(20)
    draw = ImageDraw.Draw(sheet)
    for i, path in enumerate(paths):
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (i % cols) * thumb_w
        y = (i // cols) * (thumb_h + label_h)
        sheet.paste(image, (x + (thumb_w - image.width) // 2, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill=(255, 255, 255))
        draw.text((x + 8, y + thumb_h + 7), f"{i + 1:02d}", font=label_font, fill=NAVY)
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
        })

    contact = make_contact_sheet(outputs)
    (OUT / "telop_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(f"created {len(outputs)} telop frames")
    print(contact)


if __name__ == "__main__":
    main()
