from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "pre_exam_series" / "07_pregnancy_possibility_v1"
OUT_DIR = ASSET_DIR / "telop_frames"
CONTACT_SHEET = ASSET_DIR / "contact_sheet_telop_frames.png"

W, H = 1080, 1920
NAVY = (8, 30, 54, 255)
PANEL = (255, 255, 255, 238)
PANEL_EDGE = (255, 255, 255, 255)
SHADOW = (16, 26, 38, 70)
ACCENT = (47, 148, 130, 255)
ACCENT_YELLOW = (255, 213, 86, 255)
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"


FRAMES = [
    {
        "src": "frame_01_after_consultation.png",
        "out": "frame_01_after_consultation_telop.png",
        "lines": ["診察室で", "言いそびれた"],
        "accent": "yellow",
    },
    {
        "src": "frame_02_patient_calendar.png",
        "out": "frame_02_patient_calendar_telop.png",
        "lines": ["妊娠してるかも…", "今さら言える？"],
    },
    {
        "src": "frame_03_rt_confirming.png",
        "out": "frame_03_rt_confirming_telop.png",
        "lines": ["検査室でも", "確認します"],
        "accent": "green",
    },
    {
        "src": "frame_04_questionnaire_hand.png",
        "out": "frame_04_questionnaire_hand_telop.png",
        "lines": ["検査前に", "もう一度チェック"],
    },
    {
        "src": "frame_05_patient_rt_conversation.png",
        "out": "frame_05_patient_rt_conversation_telop.png",
        "lines": ["ここで伝えて", "大丈夫です"],
        "accent": "yellow",
        "box": (78, 1240, 1002, 1460),
    },
    {
        "src": "frame_06_patient_speaks_up.png",
        "out": "frame_06_patient_speaks_up_telop.png",
        "lines": ["わからない段階でも", "大丈夫"],
    },
    {
        "src": "frame_07_rt_review_exam.png",
        "out": "frame_07_rt_review_exam_telop.png",
        "lines": ["必要に応じて", "方法を確認"],
        "accent": "green",
    },
    {
        "src": "frame_08_documents_equipment.png",
        "out": "frame_08_documents_equipment_telop.png",
        "lines": ["確認してから", "進めます"],
        "box": (78, 810, 1002, 1060),
    },
    {
        "src": "frame_09_patient_relieved.png",
        "out": "frame_09_patient_relieved_telop.png",
        "lines": ["あとからでも", "大丈夫"],
    },
    {
        "src": "frame_10_rt_patient_nod.png",
        "out": "frame_10_rt_patient_nod_telop.png",
        "lines": ["聞かれたら", "そのまま伝えて"],
    },
    {
        "src": "frame_11_enter_exam_room.png",
        "out": "frame_11_enter_exam_room_telop.png",
        "lines": ["ひとことだけで", "大丈夫です"],
        "accent": "green",
        "box": (78, 810, 1002, 1060),
    },
    {
        "src": "frame_12_cta_background.png",
        "out": "frame_12_cta_save_telop.png",
        "lines": ["保存して", "検査前に見返す"],
        "accent": "yellow",
        "box": (78, 700, 1002, 1000),
    },
]


def choose_font(size: int):
    if FONT_PATH.exists():
        return ImageFont.truetype(str(FONT_PATH), size=size)
    return ImageFont.load_default()


def cover_resize(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")
    scale = max(W / img.width, H / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - W) // 2
    top = (nh - H) // 2
    return resized.crop((left, top, left + W, top + H))


def measure_lines(draw: ImageDraw.ImageDraw, lines: list[str], font, spacing: int):
    boxes = [draw.textbbox((0, 0), line, font=font) for line in lines]
    widths = [box[2] - box[0] for box in boxes]
    heights = [box[3] - box[1] for box in boxes]
    return max(widths), sum(heights) + spacing * (len(lines) - 1), heights


def fit_font(draw: ImageDraw.ImageDraw, lines: list[str], max_w: int, max_h: int):
    spacing = 20
    for size in range(86, 44, -2):
        font = choose_font(size)
        width, height, _ = measure_lines(draw, lines, font, spacing)
        if width <= max_w and height <= max_h:
            return font, spacing
    return choose_font(44), 14


def draw_readability_wash(img: Image.Image) -> None:
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, W, 520), fill=(255, 255, 255, 16))
    draw.rectangle((0, H - 300, W, H), fill=(0, 0, 0, 14))
    img.alpha_composite(overlay)


def draw_telop(img: Image.Image, frame: dict) -> None:
    x0, y0, x1, y1 = frame.get("box", (78, 170, 1002, 420))
    lines = frame["lines"]

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x0 + 10, y0 + 12, x1 + 10, y1 + 12), radius=34, fill=SHADOW)
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(12)))

    draw = ImageDraw.Draw(img, "RGBA")
    draw.rounded_rectangle((x0, y0, x1, y1), radius=34, fill=PANEL)
    draw.rounded_rectangle((x0 + 8, y0 + 8, x1 - 8, y1 - 8), radius=28, outline=PANEL_EDGE, width=5)

    accent = frame.get("accent")
    if accent:
        color = ACCENT_YELLOW if accent == "yellow" else ACCENT
        draw.rounded_rectangle((x0 + 64, y1 - 34, x1 - 64, y1 - 24), radius=5, fill=color)

    font, spacing = fit_font(draw, lines, (x1 - x0) - 96, (y1 - y0) - 84)
    _, total_h, heights = measure_lines(draw, lines, font, spacing)
    yy = y0 + ((y1 - y0) - total_h) // 2 - 4
    for line, line_h in zip(lines, heights):
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        draw.text(((x0 + x1 - line_w) // 2, yy), line, font=font, fill=NAVY)
        yy += line_h + spacing


def make_contact_sheet(paths: list[Path]) -> None:
    cols = 4
    thumb_w, thumb_h = 216, 384
    label_h = 38
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (245, 247, 250))
    label_font = ImageFont.load_default()
    for idx, path in enumerate(paths):
        img = Image.open(path).convert("RGB")
        img.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), "white")
        tile.paste(img, ((thumb_w - img.width) // 2, 0))
        ImageDraw.Draw(tile).text((8, thumb_h + 10), path.name[:32], fill=(0, 0, 0), font=label_font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
    sheet.save(CONTACT_SHEET, quality=94)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    manifest_frames = []
    for frame in FRAMES:
        src = ASSET_DIR / frame["src"]
        out = OUT_DIR / frame["out"]
        img = cover_resize(Image.open(src)).convert("RGBA")
        draw_readability_wash(img)
        draw_telop(img, frame)
        img.convert("RGB").save(out, quality=95)
        outputs.append(out)
        manifest_frames.append({"source": str(src), "output": str(out), "telop": frame["lines"]})

    make_contact_sheet(outputs)
    manifest = {
        "title": "妊娠しているかも 診察室で言えなかった",
        "size": {"width": W, "height": H},
        "font": str(FONT_PATH),
        "style": "white rounded rectangle backing, dark navy text, Instagram Reels safe area",
        "asset_dir": str(ASSET_DIR),
        "output_dir": str(OUT_DIR),
        "contact_sheet": str(CONTACT_SHEET),
        "frames": manifest_frames,
    }
    (OUT_DIR / "telop_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8-sig",
    )
    print(OUT_DIR)
    print(CONTACT_SHEET)


if __name__ == "__main__":
    main()
