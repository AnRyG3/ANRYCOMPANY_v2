from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
INPUT_DIR = ROOT / "reel_assets" / "parent_transfer_10_images"
OUTPUT_DIR = ROOT / "reel_assets" / "parent_transfer_10_telop_frames"
CONTACT_SHEET = OUTPUT_DIR / "_qa_contact_sheet_telop.png"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (12, 34, 64, 255)
ACCENT_GREEN = (34, 132, 120, 255)
ACCENT_YELLOW = (210, 142, 22, 255)
PANEL = (255, 255, 255, 238)
PANEL_EDGE = (255, 255, 255, 255)
SHADOW = (8, 18, 32, 62)


FRAMES = [
    {
        "src": "01_waiting_wheelchair.png",
        "out": "01_waiting_wheelchair_telop.png",
        "segments": [[("車椅子の親", "green")], ["検査台へどう移る？"]],
        "box": (82, 1188, 998, 1424),
    },
    {
        "src": "02_concern_before_transfer.png",
        "out": "02_concern_before_transfer_telop.png",
        "segments": [["家族だけで"], [("動かしていい？", "green")]],
        "box": (82, 1188, 998, 1424),
    },
    {
        "src": "03_staff_reassurance.png",
        "out": "03_staff_reassurance_telop.png",
        "segments": [["その気持ち"], [("おかしくありません", "green")]],
        "box": (82, 1054, 998, 1290),
    },
    {
        "src": "04_transfer_method_changes.png",
        "out": "04_transfer_method_changes_telop.png",
        "segments": [["移動方法は"], [("状態で変わります", "green")]],
        "box": (82, 1188, 998, 1424),
    },
    {
        "src": "05_do_not_move_alone.png",
        "out": "05_do_not_move_alone_telop.png",
        "segments": [["無理に動かさず"], [("スタッフへ", "green")]],
        "box": (82, 1188, 998, 1424),
    },
    {
        "src": "06_explain_usual_support.png",
        "out": "06_explain_usual_support_telop.png",
        "segments": [[("普段の支え方", "green")], ["先に伝える"]],
        "box": (82, 292, 998, 528),
    },
    {
        "src": "07_family_support_check.png",
        "out": "07_family_support_check_telop.png",
        "segments": [["必要な時は"], [("支え方を確認", "green")]],
        "box": (82, 1188, 998, 1424),
    },
    {
        "src": "08_anxious_to_explain.png",
        "out": "08_anxious_to_explain_telop.png",
        "segments": [["うまく話せるか"], [("不安でも", "green")]],
        "box": (82, 292, 998, 528),
    },
    {
        "src": "09_relief_after_telling.png",
        "out": "09_relief_after_telling_telop.png",
        "segments": [["負担を減らす"], [("手がかりに", "green")]],
        "box": (82, 1188, 998, 1424),
    },
    {
        "src": "10_save_cta.png",
        "out": "10_save_cta_telop.png",
        "segments": [[("保存", "yellow"), "して"], ["付き添い前に見返す"]],
        "box": (82, 1124, 998, 1360),
    },
    {
        "src": "11_follow_cta.png",
        "out": "11_follow_cta_telop.png",
        "segments": [["検査の不安を"], [("少しずつ軽く", "green")]],
        "box": (82, 1054, 998, 1290),
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
    for size in range(72, 39, -2):
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
    if mark == "green":
        return ACCENT_GREEN
    if mark == "yellow":
        return ACCENT_YELLOW
    return NAVY


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
                "title": "車椅子や杖を使う親、検査台への移動はどうすればいい？",
                "style": "要点だけ、1画面1メッセージ、患者さん向けにやさしく、断定しすぎない、重要語だけ強調、X軸中央配置",
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
