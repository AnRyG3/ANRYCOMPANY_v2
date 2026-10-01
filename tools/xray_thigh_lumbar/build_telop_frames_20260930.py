from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
BASE = ROOT / "reel_assets" / "xray_thigh_lumbar_20260930_images"
OUT = ROOT / "reel_assets" / "xray_thigh_lumbar_20260930_telop_frames"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (16, 36, 55, 255)
BLUE = (0, 104, 150, 255)
PANEL = (255, 255, 255, 179)
SHADOW = (0, 0, 0, 38)


# One message per frame. All panels remain horizontally centered in the frame.
FRAMES = [
    ("frame_01_hook_why_lower_back_too.png", "telop_01_hook_question.png", [["太ももが痛いのに"], ["どうして", "腰", "も撮るの？"]], {"腰"}),
    ("frame_02_ask_before_exam.png", "telop_02_ask_before_exam.png", [["「なぜここも？」と思ったら"], ["撮影前に", "確認", "して大丈夫です"]], {"確認"}),
    ("frame_03_pain_location_not_always_cause.png", "telop_03_pain_and_cause.png", [["痛い場所と"], ["原因", "の場所は同じとは限りません"]], {"原因"}),
    ("frame_04_symptoms_and_exam_explanation.png", "telop_04_symptoms_may_relate.png", [["症状によっては"], ["腰や股関節", "が関係することも"]], {"腰や股関節"}),
    ("frame_05_preparing_needed_views.png", "telop_05_doctor_orders_views.png", [["医師が"], ["必要と判断した部位", "を撮影します"]], {"必要と判断した部位"}),
    ("frame_06_more_information_needed.png", "telop_06_clue_for_cause.png", [["原因を見分ける"], ["手がかり", "を増やすためです"]], {"手がかり"}),
    ("frame_07_ask_staff_or_doctor.png", "telop_07_ask_for_purpose.png", [["詳しい目的は"], ["医師やスタッフに", "確認", "できます"]], {"確認"}),
    ("frame_08_save_before_exam.png", "telop_08_save_before_exam.png", [["整形外科の検査前に"], ["見返せるよう", "保存"]], {"保存"}),
    ("frame_09_follow_cta_technologist.png", "telop_09_follow_cta.png", [["検査の「なぜ？」を"], ["減らしたい方は", "フォロー"]], {"フォロー"}),
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


def width(draw: ImageDraw.ImageDraw, text: str, used_font: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=used_font)
    return box[2] - box[0]


def line_width(draw: ImageDraw.ImageDraw, line: list[str], used_font: ImageFont.FreeTypeFont) -> int:
    gap = round(used_font.size * 0.08)
    return sum(width(draw, part, used_font) for part in line) + gap * (len(line) - 1)


def choose_font(draw: ImageDraw.ImageDraw, lines: list[list[str]]) -> ImageFont.FreeTypeFont:
    for size in range(68, 39, -2):
        candidate = font(size)
        if max(line_width(draw, line, candidate) for line in lines) <= 820:
            return candidate
    return font(38)


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
    y0 = 190 if position == "top" else (H - panel_height) // 2
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
            x += width(draw, part, used_font) + gap
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
    outputs = []
    manifest = []
    for index, (source_name, output_name, lines, highlights) in enumerate(FRAMES, start=1):
        source = BASE / source_name
        output = OUT / output_name
        if not source.exists():
            raise FileNotFoundError(source)
        position = "top" if index in {6, 7, 8} else "center"
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
