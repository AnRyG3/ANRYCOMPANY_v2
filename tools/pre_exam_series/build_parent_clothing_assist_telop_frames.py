from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
INPUT_DIR = ROOT / "reel_assets" / "parent_clothing_assist_images"
OUTPUT_DIR = ROOT / "reel_assets" / "parent_clothing_assist_telop_frames"
CONTACT_SHEET = OUTPUT_DIR / "contact_sheet_telop_frames.png"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (10, 32, 58, 255)
ACCENT_GREEN = (34, 132, 120, 255)
ACCENT_YELLOW = (210, 142, 22, 255)
PANEL = (255, 255, 255, 240)
PANEL_EDGE = (255, 255, 255, 255)
SHADOW = (8, 18, 32, 68)


FRAMES = [
    {
        "src": "frame_01_opening_patient_changing_room.png",
        "out": "frame_01_opening_patient_changing_room_telop.png",
        "segments": [[("親の着替え", "yellow")], ["一人でできるかな"]],
        "box": (76, 178, 1004, 430),
    },
    {
        "src": "frame_02_family_view_waiting_area.png",
        "out": "frame_02_family_view_waiting_area_telop.png",
        "segments": [["手伝う？"], [("見守る？", "green")]],
        "box": (76, 176, 1004, 428),
    },
    {
        "src": "frame_03_reassured_patient_bench.png",
        "out": "frame_03_reassured_patient_bench_telop.png",
        "segments": [["その気持ち"], [("おかしくありません", "green")]],
        "box": (76, 176, 1004, 428),
    },
    {
        "src": "frame_04_clothing_varies_by_person.png",
        "out": "frame_04_clothing_varies_by_person_telop.png",
        "segments": [["手伝いの必要さは"], [("人それぞれ", "yellow")]],
        "box": (76, 176, 1004, 428),
    },
    {
        "src": "frame_05_info_to_share_checklist.png",
        "out": "frame_05_info_to_share_checklist_telop.png",
        "segments": [[("普段の着替え", "green")], ["先に伝えてOK"]],
        "box": (76, 176, 1004, 428),
    },
    {
        "src": "frame_06_staff_support_preparation_area.png",
        "out": "frame_06_staff_support_preparation_area_telop.png",
        "segments": [["対応は"], [("状況によって変わります", "green")]],
        "box": (76, 176, 1004, 428),
    },
    {
        "src": "frame_07_no_need_to_force_patient.png",
        "out": "frame_07_no_need_to_force_patient_telop.png",
        "segments": [["無理に一人で"], [("進めなくて大丈夫", "green")]],
        "box": (76, 176, 1004, 428),
    },
    {
        "src": "frame_08_how_much_to_tell_memo.png",
        "out": "frame_08_how_much_to_tell_memo_telop.png",
        "segments": [["どこまで伝える？"], [("迷っても大丈夫", "green")]],
        "box": (76, 176, 1004, 428),
    },
    {
        "src": "frame_09_staff_prepares_gown.png",
        "out": "frame_09_staff_prepares_gown_telop.png",
        "segments": [["先にわかると"], [("準備しやすい", "green")]],
        "box": (76, 176, 1004, 428),
    },
    {
        "src": "frame_10_save_cta_background.png",
        "out": "frame_10_save_cta_background_telop.png",
        "segments": [[("保存", "yellow"), "して"], ["検査前に見返してね"]],
        "box": (76, 612, 1004, 864),
    },
    {
        "src": "frame_11_follow_cta_background.png",
        "out": "frame_11_follow_cta_background_telop.png",
        "segments": [[("フォロー", "green"), "で"], ["検査前の不安を少し軽く"]],
        "box": (76, 612, 1004, 864),
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


def line_width(draw: ImageDraw.ImageDraw, line: list, fnt: ImageFont.FreeTypeFont) -> int:
    return sum(text_width(draw, text, fnt) for text in plain_segments(line))


def line_height(draw: ImageDraw.ImageDraw, line: list, fnt: ImageFont.FreeTypeFont) -> int:
    heights = []
    for text in plain_segments(line):
        bbox = draw.textbbox((0, 0), text, font=fnt)
        heights.append(bbox[3] - bbox[1])
    return max(heights) if heights else 0


def fit_font(draw: ImageDraw.ImageDraw, segments: list[list], max_w: int, max_h: int):
    for size in range(76, 43, -2):
        fnt = font(size)
        spacing = max(12, int(size * 0.24))
        width = max(line_width(draw, line, fnt) for line in segments)
        height = sum(line_height(draw, line, fnt) for line in segments)
        height += spacing * (len(segments) - 1)
        if width <= max_w and height <= max_h:
            return fnt, spacing
    return font(44), 12


def color_for(mark: str | None):
    if mark == "green":
        return ACCENT_GREEN
    if mark == "yellow":
        return ACCENT_YELLOW
    return NAVY


def draw_background_panel(img: Image.Image, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((x0 + 9, y0 + 11, x1 + 9, y1 + 11), radius=34, fill=SHADOW)
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(12)))
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rounded_rectangle(box, radius=34, fill=PANEL)
    draw.rounded_rectangle((x0 + 8, y0 + 8, x1 - 8, y1 - 8), radius=28, outline=PANEL_EDGE, width=5)


def draw_telop(img: Image.Image, frame: dict) -> None:
    x0, y0, x1, y1 = frame["box"]
    segments = frame["segments"]
    draw_background_panel(img, frame["box"])
    draw = ImageDraw.Draw(img, "RGBA")

    fnt, spacing = fit_font(draw, segments, (x1 - x0) - 100, (y1 - y0) - 76)
    heights = [line_height(draw, line, fnt) for line in segments]
    total_h = sum(heights) + spacing * (len(segments) - 1)
    yy = y0 + ((y1 - y0) - total_h) // 2 - 4

    for line, h in zip(segments, heights):
        width = line_width(draw, line, fnt)
        xx = x0 + ((x1 - x0) - width) // 2
        for part in line:
            if isinstance(part, tuple):
                text, mark = part
            else:
                text, mark = part, None
            draw.text((xx, yy), text, font=fnt, fill=color_for(mark))
            xx += text_width(draw, text, fnt)
        yy += h + spacing


def make_contact_sheet(paths: list[Path]) -> None:
    cols = 5
    thumb_w, thumb_h = 216, 384
    label_h = 38
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
        draw.text((x + 10, y + thumb_h + 7), f"{idx + 1:02d}", font=label_font, fill=NAVY)
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
                "title": "親の着替えが不安な時、付き添い家族が先に伝えたいこと",
                "style": "要点だけ、1画面1メッセージ、白角丸パネル、重要語だけ強調",
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
    print(OUTPUT_DIR)
    print(CONTACT_SHEET)


if __name__ == "__main__":
    main()
