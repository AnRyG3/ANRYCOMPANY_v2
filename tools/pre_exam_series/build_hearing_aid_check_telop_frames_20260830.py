from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
INPUT_DIR = ROOT / "reel_assets" / "pre_exam_series" / "hearing_aid_check"
OUTPUT_DIR = ROOT / "reel_assets" / "pre_exam_series" / "hearing_aid_check_telop"
CONTACT_SHEET = OUTPUT_DIR / "_qa_contact_sheet_telop.png"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (12, 34, 64, 255)
ACCENT_BLUE = (0, 118, 210, 255)
ACCENT_SAVE = (218, 145, 25, 255)
PANEL = (255, 255, 255, 240)
PANEL_EDGE = (255, 255, 255, 255)
SHADOW = (8, 18, 32, 62)

BOXES = {
    "top": (82, 252, 998, 488),
    "top_low": (82, 348, 998, 584),
    "center": (82, 842, 998, 1078),
    "bottom": (82, 1248, 998, 1484),
}

FRAMES = [
    {
        "src": "frame_01_waiting_with_hearing_aid.png",
        "out": "telop_01_waiting_with_hearing_aid.png",
        "segments": [[("補聴器", "blue"), "を外したら"], ["聞こえないかも..."]],
        "position": "top",
    },
    {
        "src": "frame_02_explanation_before_removal.png",
        "out": "telop_02_explanation_before_removal.png",
        "segments": [["説明は"], ["聞こえる状態で", ("先に", "blue")]],
        "position": "center",
    },
    {
        "src": "frame_03_hearing_aid_listening_close.png",
        "out": "telop_03_hearing_aid_listening_close.png",
        "segments": [[("補聴器", "blue"), "をつけたまま"], ["先に確認します"]],
        "position": "top",
    },
    {
        "src": "frame_04_mri_before_removal.png",
        "out": "telop_04_mri_before_removal.png",
        "segments": [["MRIは"], [("入室直前", "blue"), "に外します"]],
        "position": "top",
    },
    {
        "src": "frame_05_hearing_aids_outside_mri.png",
        "out": "telop_05_hearing_aids_outside_mri.png",
        "segments": [["外した補聴器は"], ["検査室の", ("外", "blue"), "へ"]],
        "position": "center",
    },
    {
        "src": "frame_06_ct_control_room_check.png",
        "out": "telop_06_ct_control_room_check.png",
        "segments": [["CTは", ("当院", "blue"), "では"], ["聞こえを確認"]],
        "position": "top",
    },
    {
        "src": "frame_07_ct_light_signal_low_pillow.png",
        "out": "telop_07_ct_light_signal_low_pillow.png",
        "segments": [["聞こえにくい時は"], [("照明", "blue"), "で合図します"]],
        "position": "bottom",
    },
    {
        "src": "frame_08_ct_patient_sees_light.png",
        "out": "telop_08_ct_patient_sees_light.png",
        "segments": [["声だけでなく"], [("目", "blue"), "で分かる方法も"]],
        "position": "center",
    },
    {
        "src": "frame_09_reassuring_confirmation.png",
        "out": "telop_09_reassuring_confirmation.png",
        "segments": [["対応は"], [("確認", "blue"), "しながら進めます"]],
        "position": "top",
    },
    {
        "src": "frame_10_save_cta_review.png",
        "out": "telop_10_save_cta_review.png",
        "segments": [[("保存", "save"), "して"], ["検査", ("前日", "blue"), "に見返す"]],
        "position": "top_low",
    },
    {
        "src": "frame_11_outro_rt_tech.png",
        "out": "telop_11_outro_rt_tech.png",
        "segments": [["検査前の", ("疑問", "blue"), "も"], ["診療放射線技師目線で"]],
        "position": "top_low",
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
    for size in range(74, 41, -2):
        fnt = font(size)
        spacing = max(12, int(size * 0.22))
        width = max(line_width(draw, line, fnt) for line in segments)
        height = sum(line_height(draw, line, fnt) for line in segments)
        height += spacing * (len(segments) - 1)
        if width <= max_w and height <= max_h:
            return fnt, spacing
    return font(42), 10


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
        return ACCENT_BLUE
    if mark == "save":
        return ACCENT_SAVE
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
    cols = 4
    thumb_w, thumb_h = 270, 480
    label_h = 42
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
        draw.text((x + 10, y + thumb_h + 8), f"{idx + 1:02d} {path.stem[:17]}", font=label_font, fill=NAVY)
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
                "position": frame["position"],
                "box": BOXES[frame["position"]],
            }
        )

    make_contact_sheet(outputs)
    (OUTPUT_DIR / "telop_manifest.json").write_text(
        json.dumps(
            {
                "title": "補聴器を外したら説明が聞こえない時、どうすればいい？",
                "style": "要点だけ、1画面1メッセージ、X軸中央、上・中央・下のみ、重要語だけ青強調、患者さん向けにやさしく、断定しすぎない",
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
