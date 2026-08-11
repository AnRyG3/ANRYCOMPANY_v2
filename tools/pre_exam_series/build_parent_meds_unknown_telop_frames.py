from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "pre_exam_series" / "10_parent_meds_unknown_v1"
INPUT_DIR = ROOT / "reel_assets" / "pre_exam_series" / "10_parent_meds_unknown_v1_production"
OUTPUT_DIR = ROOT / "reel_assets" / "pre_exam_series" / "10_parent_meds_unknown_v1_telop"
CONTACT_SHEET = OUTPUT_DIR / "_qa_contact_sheet_telop.png"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (12, 34, 64, 255)
ACCENT_GREEN = (34, 132, 120, 255)
PANEL = (255, 255, 255, 240)
PANEL_EDGE = (255, 255, 255, 255)
SHADOW = (8, 18, 32, 62)


FRAMES = [
    {
        "src": "frame_03_family_checking_meds.png",
        "out": "frame_01_opening_family_meds_telop.png",
        "segments": [[("親の薬", "green"), "、聞かれても"], ["分からない"]],
        "box": (86, 292, 994, 528),
    },
    {
        "src": "frame_01_home_medicine_notebook.png",
        "out": "frame_02_anxiety_medicine_table_telop.png",
        "segments": [["答えられるか"], [("不安", "green"), "になる"]],
        "box": (82, 292, 998, 528),
    },
    {
        "src": "frame_06_waiting_area_pouch.png",
        "out": "frame_03_empathy_waiting_telop.png",
        "segments": [["その気持ち"], [("おかしくありません", "green")]],
        "box": (92, 292, 988, 526),
    },
    {
        "src": "frame_04_phone_photo_meds.png",
        "out": "frame_04_phone_photo_meds_telop.png",
        "segments": [["写真に撮ったものでも"], [("大丈夫", "green")]],
        "box": (86, 292, 994, 526),
    },
    {
        "src": "frame_02_hospital_check_counter.png",
        "out": "frame_05_bags_photo_clue_telop.png",
        "segments": [[("薬袋", "green"), "や写真も"], ["手がかりになります"]],
        "box": (82, 292, 998, 528),
    },
    {
        "src": "frame_08_tell_unknown_to_staff.png",
        "out": "frame_06_tell_unknown_to_staff_telop.png",
        "segments": [["分からない所は"], [("分からない", "green"), "で大丈夫"]],
        "box": (74, 292, 1006, 538),
    },
    {
        "src": "frame_09_staff_confirms_helpful.png",
        "out": "frame_07_staff_confirms_helpful_telop.png",
        "segments": [["分かる範囲でも"], [("確認の助け", "green"), "に"]],
        "box": (82, 292, 998, 526),
    },
    {
        "src": "frame_07_counter_show_items.png",
        "out": "frame_08_not_perfect_counter_telop.png",
        "segments": [["完璧でなくても"], [("大きな情報", "green"), "です"]],
        "box": (88, 842, 992, 1076),
    },
    {
        "src": "frame_10_save_cta_family.png",
        "out": "frame_09_save_cta_family_telop.png",
        "segments": [["家族の検査前に"], [("保存", "green"), "して見返す"]],
        "box": (82, 292, 998, 526),
    },
    {
        "src": "frame_10_save_cta_family.png",
        "out": "frame_10_follow_cta_family_telop.png",
        "segments": [["検査前の不安を"], [("少し軽く", "green")]],
        "box": (82, 292, 998, 526),
    },
]


def font(size: int) -> ImageFont.FreeTypeFont:
    if not FONT_PATH.exists():
        raise FileNotFoundError(f"Required telop font not found: {FONT_PATH}")
    return ImageFont.truetype(str(FONT_PATH), size=size)


def cover_resize(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")
    scale = max(W / img.width, H / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - W) // 2
    top = (nh - H) // 2
    return resized.crop((left, top, left + W, top + H))


def plain_segments(line: list) -> list[str]:
    return [part[0] if isinstance(part, tuple) else part for part in line]


def text_width(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=fnt)
    return bbox[2] - bbox[0]


def text_height(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=fnt)
    return bbox[3] - bbox[1]


def line_width(draw: ImageDraw.ImageDraw, line: list, fnt: ImageFont.FreeTypeFont) -> int:
    return sum(text_width(draw, text, fnt) for text in plain_segments(line))


def line_height(draw: ImageDraw.ImageDraw, line: list, fnt: ImageFont.FreeTypeFont) -> int:
    heights = [text_height(draw, text, fnt) for text in plain_segments(line)]
    return max(heights) if heights else 0


def fit_font(draw: ImageDraw.ImageDraw, segments: list[list], max_w: int, max_h: int):
    for size in range(70, 39, -2):
        fnt = font(size)
        spacing = max(12, int(size * 0.22))
        width = max(line_width(draw, line, fnt) for line in segments)
        height = sum(line_height(draw, line, fnt) for line in segments)
        height += spacing * (len(segments) - 1)
        if width <= max_w and height <= max_h:
            return fnt, spacing
    return font(40), 10


def draw_panel(img: Image.Image, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((x0 + 8, y0 + 10, x1 + 8, y1 + 10), radius=34, fill=SHADOW)
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(12)))

    draw = ImageDraw.Draw(img, "RGBA")
    draw.rounded_rectangle(box, radius=34, fill=PANEL)
    draw.rounded_rectangle((x0 + 7, y0 + 7, x1 - 7, y1 - 7), radius=28, outline=PANEL_EDGE, width=4)


def color_for(mark: str | None):
    return ACCENT_GREEN if mark == "green" else NAVY


def draw_telop(img: Image.Image, frame: dict) -> None:
    x0, y0, x1, y1 = frame["box"]
    segments = frame["segments"]
    draw_panel(img, frame["box"])
    draw = ImageDraw.Draw(img, "RGBA")

    fnt, spacing = fit_font(draw, segments, (x1 - x0) - 84, (y1 - y0) - 64)
    heights = [line_height(draw, line, fnt) for line in segments]
    total_h = sum(heights) + spacing * (len(segments) - 1)
    yy = y0 + ((y1 - y0) - total_h) // 2 - 4

    for line, line_h in zip(segments, heights):
        width = line_width(draw, line, fnt)
        xx = x0 + ((x1 - x0) - width) // 2
        for part in line:
            if isinstance(part, tuple):
                text, mark = part
            else:
                text, mark = part, None
            draw.text((xx, yy), text, font=fnt, fill=color_for(mark))
            xx += text_width(draw, text, fnt)
        yy += line_h + spacing


def make_contact_sheet(paths: list[Path]) -> None:
    cols = 4
    thumb_w, thumb_h = 270, 480
    label_h = 40
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (244, 246, 248))
    label_font = font(22)
    draw = ImageDraw.Draw(sheet)
    for idx, path in enumerate(paths):
        img = Image.open(path).convert("RGB")
        img.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (idx % cols) * thumb_w
        y = (idx // cols) * (thumb_h + label_h)
        sheet.paste(img, (x + (thumb_w - img.width) // 2, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill=(255, 255, 255))
        draw.text((x + 10, y + thumb_h + 8), f"{idx + 1:02d}", font=label_font, fill=NAVY)
    sheet.save(CONTACT_SHEET, quality=94)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    manifest = []

    for frame in FRAMES:
        src = INPUT_DIR / frame["src"]
        out = OUTPUT_DIR / frame["out"]
        if not src.exists():
            raise FileNotFoundError(src)

        img = cover_resize(Image.open(src)).convert("RGBA")
        draw_telop(img, frame)
        img.convert("RGB").save(out, quality=95)
        outputs.append(out)
        manifest.append(
            {
                "source": str(src.relative_to(ROOT)),
                "output": str(out.relative_to(ROOT)),
                "telop": ["".join(plain_segments(line)) for line in frame["segments"]],
                "box": frame["box"],
            }
        )

    make_contact_sheet(outputs)
    (OUTPUT_DIR / "telop_manifest.json").write_text(
        json.dumps(
            {
                "title": "親の薬が分からない時、家族が検査前にできること",
                "style": "要点だけ、1画面1メッセージ、白背景、濃紺文字、重要語のみ強調、X軸中央配置",
                "font": str(FONT_PATH),
                "size": {"width": W, "height": H},
                "frames": manifest,
                "contact_sheet": str(CONTACT_SHEET.relative_to(ROOT)),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8-sig",
    )

    for output in outputs:
        print(output)
    print(CONTACT_SHEET)


if __name__ == "__main__":
    main()
