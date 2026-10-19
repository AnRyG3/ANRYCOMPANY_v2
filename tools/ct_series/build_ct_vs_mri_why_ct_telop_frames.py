from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
UNIT = ROOT / "reel_assets" / "ct_series" / "ct_vs_mri_why_ct_v1_samples"
MANIFEST = UNIT / "production_manifest.md"
OUT = UNIT / "telop_frames"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (16, 36, 55, 255)
BLUE = (0, 104, 150, 255)
PANEL = (255, 255, 255, 179)  # 70% opacity
SHADOW = (0, 0, 0, 38)


# A segment is (text, emphasized). Joining the segment text reproduces the
# displayed sentence exactly; no extra horizontal spacing is inserted.
FRAMES = [
    {
        "source": "sample_01_consultation_question.png",
        "output": "telop_01_ct_or_mri.png",
        "lines": [[("CT", True), ("と言われて", False)], [("MRI", True), ("じゃなくて大丈夫？", False)]],
        "position": "center",
    },
    {
        "source": "scene_02_ct_room_v2.png",
        "output": "telop_02_purpose.png",
        "lines": [[("目的", True), ("に応じて", False)], [("検査を使い分けます", False)]],
        "position": "center",
    },
    {
        "source": "scene_03_patient_asks_doctor.png",
        "output": "telop_03_ask_doctor.png",
        "lines": [[("理由は", False)], [("医師に聞いて", False), ("大丈夫", True)]],
        "position": "center",
    },
    {
        "source": "scene_04_patient_waiting_with_paper.png",
        "output": "telop_04_empathy.png",
        "lines": [[("MRIのほうが詳しそう…", False)], [("不安", True), ("になりますよね", False)]],
        "position": "center",
    },
    {
        "source": "sample_02_ct_mri_comparison_v2.png",
        "output": "telop_05_different_methods.png",
        "lines": [[("CT", True), ("と", False), ("MRI", True), ("は", False)], [("体を見る方法が違います", False)]],
        "position": "center",
    },
    {
        "source": "scene_06_ct_mri_equal_close_comparison_v2.png",
        "output": "telop_06_different_strengths.png",
        "lines": [[("どちらが上ではなく", False)], [("得意", True), ("なことが違います", False)]],
        "position": "center",
    },
    {
        "source": "scene_07_doctor_explains_choice.png",
        "output": "telop_07_doctor_decides.png",
        "lines": [[("検査内容は", False)], [("医師", True), ("が決めます", False)]],
        "position": "center",
    },
    {
        "source": "scene_08_imaging_department_corridor.png",
        "output": "telop_08_facility_variation.png",
        "lines": [[("施設", True), ("によって", False)], [("進め方が違うことも", False)]],
        "position": "center",
    },
    {
        "source": "scene_09_patient_prepares_question.png",
        "output": "telop_09_not_rude.png",
        "lines": [[("聞いたら失礼かな…", False)], [("そう思わなくて", False), ("大丈夫", True)]],
        "position": "center",
    },
    {
        "source": "scene_10_patient_question_doctor.png",
        "output": "telop_10_question_phrase.png",
        "lines": [[("今回、CTを受ける", False), ("理由", True), ("を", False)], [("教えていただけますか？", False)]],
        "position": "center",
    },
    {
        "source": "scene_11_patient_saves_on_phone.png",
        "output": "telop_11_save.png",
        "lines": [[("次の検査前に", False)], [("見返せるよう", False), ("保存", True)]],
        "position": "bottom",
    },
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


def segment_width(draw: ImageDraw.ImageDraw, text: str, used_font: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=used_font)
    return box[2] - box[0]


def line_width(draw: ImageDraw.ImageDraw, line: list[tuple[str, bool]], used_font: ImageFont.FreeTypeFont) -> int:
    return sum(segment_width(draw, text, used_font) for text, _ in line)


def choose_font(draw: ImageDraw.ImageDraw, lines: list[list[tuple[str, bool]]]) -> ImageFont.FreeTypeFont:
    for size in range(68, 43, -2):
        candidate = font(size)
        if max(line_width(draw, line, candidate) for line in lines) <= 850:
            return candidate
    return font(42)


def panel_y(panel_height: int, position: str) -> int:
    positions = {
        "top": 260,
        "center": (H - panel_height) // 2,
        "bottom": H - panel_height - 300,
    }
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
    outputs = []
    telop_manifest = []
    for index, frame in enumerate(FRAMES, start=1):
        source = UNIT / frame["source"]
        output = OUT / frame["output"]
        draw_frame(Image.open(source), frame["lines"], frame["position"]).save(output, quality=95)
        outputs.append(output)
        telop_manifest.append({
            "cut": index,
            "source": str(source),
            "output": str(output),
            "text": ["".join(text for text, _ in line) for line in frame["lines"]],
            "highlight_words": [text for line in frame["lines"] for text, emphasized in line if emphasized],
            "position": frame["position"],
            "x_axis": "center",
            "font": str(FONT_PATH),
            "panel_opacity": "70%",
        })

    contact_sheet = make_contact_sheet(outputs)
    (OUT / "telop_manifest.json").write_text(
        json.dumps(telop_manifest, ensure_ascii=False, indent=2),
        encoding="utf-8-sig",
    )
    print(f"created {len(outputs)} telop frames")
    print(contact_sheet)


if __name__ == "__main__":
    main()
