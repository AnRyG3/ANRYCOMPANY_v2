from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
IMAGE_DIR = ROOT / "reel_assets" / "family_accompanying_exam_preparation_images"
OUT_DIR = ROOT / "reel_assets" / "family_accompanying_exam_preparation_telop_frames"
CONTACT_SHEET = OUT_DIR / "_qa_contact_sheet_telop.png"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (12, 34, 64, 255)
ACCENT_GREEN = (34, 132, 120, 255)
PANEL = (255, 255, 255, 238)
PANEL_EDGE = (255, 255, 255, 255)
SHADOW = (8, 18, 32, 58)


FRAMES = [
    {
        "src": "frame_01_opening_preparation_bag.png",
        "out": "frame_01_opening_preparation_bag_telop.png",
        "segments": [[("親の検査", "green"), "に付き添う前に"]],
        "box": (84, 292, 996, 448),
    },
    {
        "src": "frame_02_mild_uncertainty_bag.png",
        "out": "frame_02_mild_uncertainty_bag_telop.png",
        "segments": [["持ち物、", ("足りてるかな？", "green")]],
        "box": (84, 300, 996, 458),
    },
    {
        "src": "frame_03_calm_waiting_empathy.png",
        "out": "frame_03_calm_waiting_empathy_telop.png",
        "segments": [["そう思うのは", ("自然", "green"), "です"]],
        "box": (92, 292, 988, 450),
    },
    {
        "src": "frame_04_three_point_checklist.png",
        "out": "frame_04_three_point_checklist_telop.png",
        "segments": [["まずは", ("3つ", "green"), "確認"]],
        "box": (92, 292, 988, 450),
    },
    {
        "src": "frame_05_medicine_referral_checklist.png",
        "out": "frame_05_medicine_referral_checklist_telop.png",
        "segments": [[("お薬手帳", "green"), "・紹介状"]],
        "box": (92, 308, 988, 466),
    },
    {
        "src": "frame_06_easy_change_clothes.png",
        "out": "frame_06_easy_change_clothes_telop.png",
        "segments": [[("脱ぎ着", "green"), "しやすい服"]],
        "box": (92, 292, 988, 450),
    },
    {
        "src": "frame_07_metal_items_ready.png",
        "out": "frame_07_metal_items_ready_telop.png",
        "segments": [[("金属類", "green"), "は外しやすく"]],
        "box": (92, 292, 988, 450),
    },
    {
        "src": "frame_08_mild_concern_waiting.png",
        "out": "frame_08_mild_concern_waiting_telop.png",
        "segments": [["迷ったら", ("そのまま聞いてOK", "green")]],
        "box": (84, 292, 996, 450),
    },
    {
        "src": "frame_09_reception_question_ok.png",
        "out": "frame_09_reception_question_ok_telop.png",
        "segments": [["当日", ("スタッフ", "green"), "に確認できます"]],
        "box": (74, 304, 1006, 462),
    },
    {
        "src": "frame_10_save_cta_background.png",
        "out": "frame_10_save_cta_background_telop.png",
        "segments": [["付き添い前に見返せるように"], [("保存", "green"), "しておいてください"]],
        "box": (78, 326, 1002, 574),
    },
    {
        "src": "frame_11_follow_cta_background.png",
        "out": "frame_11_follow_cta_background_telop.png",
        "segments": [["検査前の不安を"], [("少し軽く", "green")]],
        "box": (92, 300, 988, 548),
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
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    manifest = []

    for frame in FRAMES:
        src = IMAGE_DIR / frame["src"]
        out = OUT_DIR / frame["out"]
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
    (OUT_DIR / "telop_manifest.json").write_text(
        json.dumps(
            {
                "title": "高齢の親を検査に連れて行く時、事前に準備しておきたいこと",
                "style": "要点だけ、1画面1メッセージ、重要語のみ強調",
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
