from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
INPUT_DIR = ROOT / "reel_assets" / "pre_exam_series" / "12_barium_laxative_return_samples"
OUTPUT_DIR = ROOT / "reel_assets" / "pre_exam_series" / "12_barium_laxative_return_telop"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"
CONTACT_SHEET = OUTPUT_DIR / "_qa_contact_sheet_telop.png"
MANIFEST = OUTPUT_DIR / "telop_manifest.json"
TEXTS = OUTPUT_DIR / "telop_texts.txt"

W, H = 1080, 1920
NAVY = (12, 34, 64, 255)
BLUE = (0, 112, 185, 255)
PANEL = (255, 255, 255, 240)
PANEL_EDGE = (255, 255, 255, 255)
SHADOW = (8, 18, 32, 58)
BOXES = {
    "top": (82, 252, 998, 488),
    "center": (82, 842, 998, 1078),
    "bottom": (82, 1248, 998, 1484),
}

# Frames 1, 2, 3, 5, 6, 7, and 9 use center; frames 4 and 8 stay top.
FRAMES = [
    {
        "src": "01_hook_station_concourse_sample.png",
        "out": "telop_01_hook_station_concourse.png",
        "segments": [["バリウム検査の帰り"], [("下剤", "blue"), "が効いたらどうしよう"]],
        "position": "center",
    },
    {
        "src": "02_station_gate.png",
        "out": "telop_02_station_gate.png",
        "segments": [["検査後、これから"], [("電車", "blue"), "で帰るところ"]],
        "position": "center",
    },
    {
        "src": "03_toilet_check_sample.png",
        "out": "telop_03_toilet_check.png",
        "segments": [["乗る前に"], [("お手洗い", "blue"), "を確認"]],
        "position": "center",
    },
    {
        "src": "04_facility_guidance.png",
        "out": "telop_04_facility_guidance.png",
        "segments": [["下剤の飲み方は"], [("施設ごとに", "blue"), "異なります"]],
        "position": "top",
    },
    {
        "src": "05_timing_varies.png",
        "out": "telop_05_timing_varies.png",
        "segments": [["効き方には"], [("個人差", "blue"), "があります"]],
        "position": "center",
    },
    {
        "src": "06_call_facility.png",
        "out": "telop_06_call_facility.png",
        "segments": [["心配なら"], ["施設に", ("確認", "blue"), "を"]],
        "position": "center",
    },
    {
        "src": "07_normalize_anxiety.png",
        "out": "telop_07_normalize_anxiety.png",
        "segments": [["不安に思っても"], [("おかしく", "blue"), "ありません"]],
        "position": "center",
    },
    {
        "src": "08_save_cta_background.png",
        "out": "telop_08_save_cta.png",
        "segments": [["検査前日に"], [("保存", "blue"), "して見返す"]],
        "position": "top",
    },
    {
        "src": "09_follow_cta_background.png",
        "out": "telop_09_follow_cta.png",
        "segments": [[("フォロー", "blue"), "で"], ["検査前後の迷いに答えます"]],
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
    nw, nh = round(img.width * scale), round(img.height * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left, top = (nw - W) // 2, (nh - H) // 2
    return img.crop((left, top, left + W, top + H))


def segment_text(segment: str | tuple[str, str]) -> str:
    return segment[0] if isinstance(segment, tuple) else segment


def text_width(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def text_height(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[3] - box[1]


def line_width(draw: ImageDraw.ImageDraw, line: list, fnt: ImageFont.FreeTypeFont) -> int:
    return sum(text_width(draw, segment_text(part), fnt) for part in line)


def line_height(draw: ImageDraw.ImageDraw, line: list, fnt: ImageFont.FreeTypeFont) -> int:
    return max(text_height(draw, segment_text(part), fnt) for part in line)


def fit_font(draw: ImageDraw.ImageDraw, segments: list[list], max_w: int, max_h: int):
    for size in range(74, 41, -2):
        fnt = font(size)
        spacing = max(12, round(size * 0.22))
        height = sum(line_height(draw, line, fnt) for line in segments) + spacing * (len(segments) - 1)
        if max(line_width(draw, line, fnt) for line in segments) <= max_w and height <= max_h:
            return fnt, spacing
    return font(42), 10


def draw_panel(img: Image.Image, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((x0 + 8, y0 + 10, x1 + 8, y1 + 10), radius=34, fill=SHADOW)
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(12)))
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rounded_rectangle(box, radius=34, fill=PANEL)
    draw.rounded_rectangle((x0 + 7, y0 + 7, x1 - 7, y1 - 7), radius=28, outline=PANEL_EDGE, width=4)


def draw_telop(img: Image.Image, frame: dict) -> None:
    x0, y0, x1, y1 = BOXES[frame["position"]]
    draw_panel(img, (x0, y0, x1, y1))
    draw = ImageDraw.Draw(img, "RGBA")
    fnt, spacing = fit_font(draw, frame["segments"], (x1 - x0) - 84, (y1 - y0) - 64)
    heights = [line_height(draw, line, fnt) for line in frame["segments"]]
    yy = y0 + ((y1 - y0) - sum(heights) - spacing * (len(heights) - 1)) // 2 - 4
    for line, height in zip(frame["segments"], heights):
        xx = x0 + ((x1 - x0) - line_width(draw, line, fnt)) // 2
        for part in line:
            text, color = part if isinstance(part, tuple) else (part, NAVY)
            draw.text((xx, yy), text, font=fnt, fill=BLUE if color == "blue" else NAVY)
            xx += text_width(draw, text, fnt)
        yy += height + spacing


def make_contact_sheet(paths: list[Path]) -> None:
    cols, thumb_w, thumb_h, label_h = 3, 270, 480, 42
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (244, 246, 248))
    draw, label_font = ImageDraw.Draw(sheet), font(20)
    for idx, path in enumerate(paths):
        thumb = Image.open(path).convert("RGB")
        thumb.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x, y = (idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)
        sheet.paste(thumb, (x + (thumb_w - thumb.width) // 2, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill=(255, 255, 255))
        draw.text((x + 8, y + thumb_h + 8), f"{idx + 1:02d} {path.stem[:20]}", font=label_font, fill=NAVY)
    sheet.save(CONTACT_SHEET, quality=94)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs, manifest_frames, text_lines = [], [], []
    for idx, frame in enumerate(FRAMES, start=1):
        source, output = INPUT_DIR / frame["src"], OUTPUT_DIR / frame["out"]
        if not source.exists():
            raise FileNotFoundError(source)
        image = cover_resize(Image.open(source)).convert("RGBA")
        draw_telop(image, frame)
        image.convert("RGB").save(output, quality=95)
        outputs.append(output)
        lines = ["".join(segment_text(part) for part in line) for line in frame["segments"]]
        text_lines.append(f"{idx:02d}. {' / '.join(lines)} [{frame['position']}]")
        manifest_frames.append({"source": str(source.relative_to(ROOT)), "output": str(output.relative_to(ROOT)), "telop": lines, "position": frame["position"], "box": BOXES[frame["position"]]})
    make_contact_sheet(outputs)
    MANIFEST.write_text(json.dumps({"title": "健診の帰り道、下剤がいつ効くか不安なときは", "style": "要点だけ、1画面1メッセージ、X軸中央、1・2・3・5・6・7・9は中段、4・8は上段、重要語だけ青強調", "font": str(FONT_PATH), "size": {"width": W, "height": H}, "frames": manifest_frames, "contact_sheet": str(CONTACT_SHEET.relative_to(ROOT))}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8-sig")
    TEXTS.write_text("\n".join(text_lines) + "\n", encoding="utf-8-sig")
    print(f"created {len(outputs)} telop frames")
    print(OUTPUT_DIR)
    print(CONTACT_SHEET)


if __name__ == "__main__":
    main()
