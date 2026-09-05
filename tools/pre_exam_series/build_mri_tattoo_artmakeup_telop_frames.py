from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
INPUT_DIR = ROOT / "reel_assets" / "mri_series" / "mri_tattoo_artmakeup_20260905_images"
OUTPUT_DIR = ROOT / "reel_assets" / "mri_series" / "mri_tattoo_artmakeup_20260905_telop"
CONTACT_SHEET = OUTPUT_DIR / "_qa_contact_sheet_telop.png"
MANIFEST = OUTPUT_DIR / "telop_manifest.json"
TEXTS = OUTPUT_DIR / "telop_texts.txt"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (12, 34, 64, 255)
BLUE = (0, 112, 185, 255)
SAVE = (218, 145, 25, 255)
PANEL = (255, 255, 255, 240)
PANEL_EDGE = (255, 255, 255, 255)
SHADOW = (8, 18, 32, 58)

BOXES = {
    "top": (82, 252, 998, 488),
    "center": (82, 842, 998, 1078),
    "bottom": (82, 1248, 998, 1484),
}

FRAMES = [
    {
        "src": "frame01_reception_disclose_tattoo.png",
        "out": "telop_01_reception_disclose_tattoo.png",
        "segments": [[("タトゥーあり", "blue")], [("MRI", "blue"), "受けられる？"]],
        "position": "bottom",
    },
    {
        "src": "frame02_waiting_area_worry.png",
        "out": "telop_02_waiting_area_worry.png",
        "segments": [["受付前に"], [("先にひと言", "blue")]],
        "position": "top",
    },
    {
        "src": "frame03_tattoo_checklist_closeup.png",
        "out": "telop_03_tattoo_checklist_closeup.png",
        "segments": [["色素の成分は"], [("見た目で分からない", "blue")]],
        "position": "top",
    },
    {
        "src": "frame04_artmakeup_eye_closeup.png",
        "out": "telop_04_artmakeup_eye_closeup.png",
        "segments": [[("アートメイク", "blue"), "も"], ["申告を"]],
        "position": "top",
    },
    {
        "src": "frame05_pigment_checklist_stilllife.png",
        "out": "telop_05_pigment_checklist_stilllife.png",
        "segments": [["検査中に"], [("熱く感じる", "blue"), "ことも"]],
        "position": "top",
    },
    {
        "src": "frame06_staff_hand_screening.png",
        "out": "telop_06_staff_hand_screening.png",
        "segments": [["伝えると"], [("確認が進みます", "blue")]],
        "position": "top",
    },
    {
        "src": "frame07_mri_room_15t_background.png",
        "out": "telop_07_mri_room_15t_background.png",
        "segments": [["当院では"], [("1.5T", "blue"), "で対応"]],
        "position": "center",
    },
    {
        "src": "frame08_patient_relieved.png",
        "out": "telop_08_patient_relieved.png",
        "segments": [["隠さなくて"], [("大丈夫", "blue")]],
        "position": "bottom",
    },
    {
        "src": "frame09_save_share_cta_background.png",
        "out": "telop_09_save_share_cta_background.png",
        "segments": [["検査前日・受付前に"], [("保存", "save"), "して見返す"]],
        "position": "center",
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
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def text_height(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[3] - box[1]


def line_width(draw: ImageDraw.ImageDraw, line: list, fnt: ImageFont.FreeTypeFont) -> int:
    return sum(text_width(draw, text, fnt) for text in plain_segments(line))


def line_height(draw: ImageDraw.ImageDraw, line: list, fnt: ImageFont.FreeTypeFont) -> int:
    heights = [text_height(draw, text, fnt) for text in plain_segments(line)]
    return max(heights) if heights else 0


def fit_font(draw: ImageDraw.ImageDraw, segments: list[list], max_w: int, max_h: int):
    for size in range(76, 43, -2):
        fnt = font(size)
        spacing = max(12, int(size * 0.22))
        width = max(line_width(draw, line, fnt) for line in segments)
        height = sum(line_height(draw, line, fnt) for line in segments)
        height += spacing * (len(segments) - 1)
        if width <= max_w and height <= max_h:
            return fnt, spacing
    return font(44), 10


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
    if mark == "blue":
        return BLUE
    if mark == "save":
        return SAVE
    return NAVY


def draw_telop(img: Image.Image, frame: dict) -> None:
    box = BOXES[frame["position"]]
    x0, y0, x1, y1 = box
    segments = frame["segments"]
    draw_panel(img, box)
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
    cols = 5
    thumb_w, thumb_h = 216, 384
    label_h = 42
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (244, 246, 248))
    label_font = font(20)
    draw = ImageDraw.Draw(sheet)
    for idx, path in enumerate(paths):
        thumb = Image.open(path).convert("RGB")
        thumb.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (idx % cols) * thumb_w
        y = (idx // cols) * (thumb_h + label_h)
        sheet.paste(thumb, (x + (thumb_w - thumb.width) // 2, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill=(255, 255, 255))
        draw.text((x + 8, y + thumb_h + 8), f"{idx + 1:02d} {path.stem[:14]}", font=label_font, fill=NAVY)
    sheet.save(CONTACT_SHEET, quality=94)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    manifest_frames = []
    text_lines = []

    for idx, frame in enumerate(FRAMES, start=1):
        src = INPUT_DIR / frame["src"]
        out = OUTPUT_DIR / frame["out"]
        if not src.exists():
            raise FileNotFoundError(src)

        img = cover_resize(Image.open(src)).convert("RGBA")
        draw_telop(img, frame)
        img.convert("RGB").save(out, quality=95)
        outputs.append(out)

        telop = ["".join(plain_segments(line)) for line in frame["segments"]]
        text_lines.append(f"{idx:02d}. {' / '.join(telop)} [{frame['position']}]")
        manifest_frames.append(
            {
                "source": str(src.relative_to(ROOT)),
                "output": str(out.relative_to(ROOT)),
                "telop": telop,
                "position": frame["position"],
                "box": BOXES[frame["position"]],
            }
        )

    make_contact_sheet(outputs)
    MANIFEST.write_text(
        json.dumps(
            {
                "title": "MRI前、タトゥーやアートメイクがあると受けられない？",
                "style": "要点だけ、1画面2行以内、重要語だけ青または保存色で強調",
                "font": str(FONT_PATH),
                "size": {"width": W, "height": H},
                "frames": manifest_frames,
                "contact_sheet": str(CONTACT_SHEET.relative_to(ROOT)),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8-sig",
    )
    TEXTS.write_text("\n".join(text_lines) + "\n", encoding="utf-8-sig")

    print(f"created {len(outputs)} telop frames")
    print(OUTPUT_DIR)
    print(CONTACT_SHEET)


if __name__ == "__main__":
    main()
