from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
UNIT = ROOT / "reel_assets" / "ct_series" / "ct_payment_estimate_v1_samples"
MANIFEST = UNIT / "production_manifest.md"
OUT = UNIT / "telop_frames"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (16, 36, 55, 255)
BLUE = (0, 104, 150, 255)
PANEL = (255, 255, 255, 179)  # 70% opacity
SHADOW = (0, 0, 0, 38)


# A segment is (text, emphasized). Joining the segments reproduces the
# displayed sentence exactly. All text is horizontally centered, and only
# top/center/bottom positions are supported.
FRAMES = [
    {
        "source": "scene_01_ct_payment_question_v2.png",
        "output": "telop_01_payment_estimate.png",
        "lines": [[("CTの日", False), (" 会計の目安", True)], [("事前に聞いて大丈夫", False)]],
        "position": "center",
    },
    {
        "source": "scene_02_reception_guidance.png",
        "output": "telop_02_hospital_difference.png",
        "lines": [[("金額は", False)], [("病院ごと", True), ("に違います", False)]],
        "position": "center",
    },
    {
        "source": "scene_03_payment_method.png",
        "output": "telop_03_payment_method.png",
        "lines": [[("使える", False)], [("支払い方法", True), ("も確認", False)]],
        "position": "center",
    },
    {
        "source": "scene_04_payment_concern.png",
        "output": "telop_04_payment_concern.png",
        "lines": [[("当日の", False), ("会計", True)], [("気になりますよね", False)]],
        "position": "center",
    },
    {
        "source": "scene_05_ct_contrast_difference.png",
        "output": "telop_05_contrast_cost.png",
        "lines": [[("造影剤", True), ("の有無で", False)], [("費用が変わることも", False)]],
        "position": "center",
    },
    {
        "source": "scene_06_consultation_and_ct_flow.png",
        "output": "telop_06_other_factors.png",
        "lines": [[("初診・再診", True)], [("診察やほかの検査でも", False)], [("金額が変わることも", False)]],
        "position": "center",
    },
    {
        "source": "scene_07_coverage_difference.png",
        "output": "telop_07_burden_ratio.png",
        "lines": [[("負担割合", True), ("によって", False)], [("窓口の金額は変わります", False)]],
        "position": "center",
    },
    {
        "source": "scene_08_confirm_at_reception.png",
        "output": "telop_08_where_to_ask.png",
        "lines": [[("目安と支払い方法は", False)], [("受付・会計窓口", True), ("へ", False)]],
        "position": "center",
    },
    {
        "source": "scene_09_note_for_preparation.png",
        "output": "telop_09_prepare.png",
        "lines": [[("目安がわかると", False)], [("当日の準備", True), ("がしやすい", False)]],
        "position": "center",
    },
    {
        "source": "scene_10_ask_reception_v2.png",
        "output": "telop_10_question_phrase.png",
        "lines": [
            [("だいたいいくら", True), ("になりそうですか？", False)],
            [("使える", False), ("支払い方法", True), ("も教えてください", False)],
        ],
        "position": "center",
    },
    {
        "source": "scene_11_save_before_exam_day.png",
        "output": "telop_11_save.png",
        "lines": [[("予約日の前に", False)], [("見返せるよう ", False), ("保存", True)]],
        "position": "bottom",
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


def line_width(draw: ImageDraw.ImageDraw, line: list[tuple[str, bool]], used_font: ImageFont.FreeTypeFont) -> int:
    return sum(segment_width(draw, text, used_font) for text, _ in line)


def choose_font(draw: ImageDraw.ImageDraw, lines: list[list[tuple[str, bool]]]) -> ImageFont.FreeTypeFont:
    for size in range(68, 39, -2):
        candidate = font(size)
        if max(line_width(draw, line, candidate) for line in lines) <= 850:
            return candidate
    return font(38)


def panel_y(panel_height: int, position: str) -> int:
    positions = {
        "top": 260,
        "center": (H - panel_height) // 2,
        "bottom": H - panel_height - 300,
    }
    if position not in positions:
        raise ValueError(f"Unsupported telop position: {position}")
    return positions[position]


def draw_frame(source: Image.Image, lines: list[list[tuple[str, bool]]], position: str) -> Image.Image:
    base = cover(source).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    used_font = choose_font(draw, lines)
    line_height = round(used_font.size * 1.22)
    pad_x, pad_y = 58, 38
    panel_width = min(950, max(line_width(draw, line, used_font) for line in lines) + pad_x * 2)
    panel_height = line_height * len(lines) + pad_y * 2
    x0 = (W - panel_width) // 2
    y0 = panel_y(panel_height, position)
    x1, y1 = x0 + panel_width, y0 + panel_height

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((x0 + 6, y0 + 8, x1 + 6, y1 + 8), radius=30, fill=SHADOW)
    overlay.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(7)))
    draw.rounded_rectangle((x0, y0, x1, y1), radius=30, fill=PANEL)

    y = y0 + pad_y + round(used_font.size * 0.04)
    for line in lines:
        x = (W - line_width(draw, line, used_font)) // 2
        for text, emphasized in line:
            draw.text((x, y), text, font=used_font, fill=BLUE if emphasized else NAVY)
            x += segment_width(draw, text, used_font)
        y += line_height

    base.alpha_composite(overlay)
    return base.convert("RGB")


def make_contact_sheet(outputs: list[Path]) -> Path:
    thumb_w, thumb_h, label_h, columns = 270, 480, 40, 3
    rows = math.ceil(len(outputs) / columns)
    sheet = Image.new("RGB", (columns * thumb_w, rows * (thumb_h + label_h)), (246, 248, 250))
    draw = ImageDraw.Draw(sheet)
    label_font = font(22)
    for index, path in enumerate(outputs):
        x = (index % columns) * thumb_w
        y = (index // columns) * (thumb_h + label_h)
        sheet.paste(cover(Image.open(path), (thumb_w, thumb_h)), (x, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill=(255, 255, 255))
        draw.text((x + 10, y + thumb_h + 6), f"CUT {index + 1:02d}", font=label_font, fill=NAVY)
    output = OUT / "contact_sheet_telop_frames.png"
    sheet.save(output)
    return output


def verify_locked_sources() -> None:
    if not FONT_PATH.exists():
        raise FileNotFoundError(FONT_PATH)
    if not MANIFEST.exists():
        raise FileNotFoundError(MANIFEST)
    manifest_text = MANIFEST.read_text(encoding="utf-8-sig")
    if len(FRAMES) != 11:
        raise ValueError(f"Expected 11 cuts, found {len(FRAMES)}")
    for frame in FRAMES:
        source = UNIT / frame["source"]
        if not source.exists():
            raise FileNotFoundError(source)
        if str(source) not in manifest_text:
            raise ValueError(f"Source is not locked in production_manifest.md: {source}")


def main() -> None:
    verify_locked_sources()
    OUT.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    telop_manifest = []
    text_lines = []
    for index, frame in enumerate(FRAMES, start=1):
        source = UNIT / frame["source"]
        output = OUT / frame["output"]
        draw_frame(Image.open(source), frame["lines"], frame["position"]).save(output, quality=95)
        outputs.append(output)
        displayed_lines = ["".join(text for text, _ in line) for line in frame["lines"]]
        text_lines.append(f"{index:02d}. {' / '.join(displayed_lines)}")
        telop_manifest.append(
            {
                "cut": index,
                "source": str(source),
                "output": str(output),
                "text": displayed_lines,
                "highlight_words": [
                    text for line in frame["lines"] for text, emphasized in line if emphasized
                ],
                "position": frame["position"],
                "x_axis": "center",
                "font": str(FONT_PATH),
                "panel_opacity": "70%",
            }
        )

    contact_sheet = make_contact_sheet(outputs)
    (OUT / "telop_manifest.json").write_text(
        json.dumps(telop_manifest, ensure_ascii=False, indent=2),
        encoding="utf-8-sig",
    )
    (OUT / "telop_texts.txt").write_text(
        "\n".join(text_lines) + "\n",
        encoding="utf-8-sig",
    )
    print(f"created {len(outputs)} telop frames")
    print(contact_sheet)


if __name__ == "__main__":
    main()
