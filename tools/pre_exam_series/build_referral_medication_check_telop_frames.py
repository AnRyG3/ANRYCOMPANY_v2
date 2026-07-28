from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "pre_exam_series" / "09_referral_medication_check_v1"
INPUT_DIR = ASSET_DIR / "raw_frames"
OUTPUT_DIR = ASSET_DIR / "telop_frames"
CONTACT_SHEET = ASSET_DIR / "contact_sheet_telop_frames.png"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (12, 34, 64, 255)
ACCENT_GREEN = (34, 132, 120, 255)
ACCENT_YELLOW = (202, 139, 24, 255)
PANEL = (255, 255, 255, 240)
PANEL_EDGE = (255, 255, 255, 255)
SHADOW = (8, 18, 32, 72)


FRAMES = [
    {
        "src": "frame_01_reception_referral_meds.png",
        "out": "frame_01_reception_referral_meds_telop.png",
        "segments": [["また", ("確認", "yellow"), "？"], ["それには理由があります"]],
        "box": (94, 1248, 986, 1474),
    },
    {
        "src": "frame_02_questionnaire_hands.png",
        "out": "frame_02_questionnaire_hands_telop.png",
        "segments": [["同じ質問に感じると"], [("面倒", "yellow"), "ですよね"]],
        "box": (92, 1148, 988, 1378),
    },
    {
        "src": "frame_03_empathy_voice.png",
        "out": "frame_03_empathy_voice_telop.png",
        "segments": [["そう感じても"], [("おかしくありません", "green")]],
        "box": (98, 1242, 982, 1466),
    },
    {
        "src": "frame_04_medication_notebook_check.png",
        "out": "frame_04_medication_notebook_check_telop.png",
        "segments": [[("薬や体調", "green"), "によって"], ["注意が必要なことも"]],
        "box": (86, 1260, 994, 1494),
    },
    {
        "src": "frame_05_referral_review.png",
        "out": "frame_05_referral_review_telop.png",
        "segments": [[("紹介状", "green"), "には"], ["検査の目的が書かれています"]],
        "box": (70, 1260, 1010, 1492),
    },
    {
        "src": "frame_06_documents_together.png",
        "out": "frame_06_documents_together_telop.png",
        "segments": [["情報があると"], [("注意点", "green"), "を確認しやすい"]],
        "box": (78, 1244, 1002, 1474),
    },
    {
        "src": "frame_07_safety_confirmation.png",
        "out": "frame_07_safety_confirmation_telop.png",
        "segments": [["確認は二度手間ではなく"], [("安全", "yellow"), "のための工程です"]],
        "box": (70, 1260, 1010, 1496),
    },
    {
        "src": "frame_08_next_visit_guarded.png",
        "out": "frame_08_next_visit_guarded_telop.png",
        "segments": [["また聞かれると"], ["身構えることもあります"]],
        "box": (84, 1242, 996, 1472),
    },
    {
        "src": "frame_09_reassuring_finish.png",
        "out": "frame_09_reassuring_finish_telop.png",
        "segments": [["毎回の確認が"], [("安心", "green"), "につながります"]],
        "box": (96, 1282, 984, 1510),
    },
    {
        "src": "frame_10_save_cta_bg.png",
        "out": "frame_10_save_cta_bg_telop.png",
        "segments": [["次回の検査前に"], ["見返せるよう", ("保存", "yellow")]],
        "box": (92, 308, 988, 548),
    },
    {
        "src": "frame_11_follow_cta_bg.png",
        "out": "frame_11_follow_cta_bg_telop.png",
        "segments": [["一緒に考えます"], [("フォロー", "green"), "して待っていてください"]],
        "box": (92, 304, 988, 548),
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


def line_width(draw: ImageDraw.ImageDraw, line: list, fnt: ImageFont.FreeTypeFont) -> int:
    width = 0
    for text in plain_segments(line):
        bbox = draw.textbbox((0, 0), text, font=fnt)
        width += bbox[2] - bbox[0]
    return width


def line_height(draw: ImageDraw.ImageDraw, line: list, fnt: ImageFont.FreeTypeFont) -> int:
    heights = []
    for text in plain_segments(line):
        bbox = draw.textbbox((0, 0), text, font=fnt)
        heights.append(bbox[3] - bbox[1])
    return max(heights) if heights else 0


def fit_font(draw: ImageDraw.ImageDraw, segments: list[list], max_w: int, max_h: int):
    for size in range(72, 41, -2):
        fnt = font(size)
        spacing = max(12, int(size * 0.22))
        width = max(line_width(draw, line, fnt) for line in segments)
        height = sum(line_height(draw, line, fnt) for line in segments) + spacing * (len(segments) - 1)
        if width <= max_w and height <= max_h:
            return fnt, spacing
    return font(42), 10


def draw_background_panel(img: Image.Image, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((x0 + 9, y0 + 11, x1 + 9, y1 + 11), radius=34, fill=SHADOW)
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(12)))
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rounded_rectangle(box, radius=34, fill=PANEL)
    draw.rounded_rectangle((x0 + 8, y0 + 8, x1 - 8, y1 - 8), radius=28, outline=PANEL_EDGE, width=5)


def color_for(mark: str | None):
    if mark == "green":
        return ACCENT_GREEN
    if mark == "yellow":
        return ACCENT_YELLOW
    return NAVY


def draw_telop(img: Image.Image, frame: dict) -> None:
    x0, y0, x1, y1 = frame["box"]
    segments = frame["segments"]
    draw_background_panel(img, frame["box"])
    draw = ImageDraw.Draw(img, "RGBA")

    fnt, spacing = fit_font(draw, segments, (x1 - x0) - 96, (y1 - y0) - 72)
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
            bbox = draw.textbbox((0, 0), text, font=fnt)
            xx += bbox[2] - bbox[0]
        yy += h + spacing


def make_contact_sheet(paths: list[Path]) -> None:
    cols = 4
    thumb_w, thumb_h = 270, 480
    label_h = 38
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (244, 246, 248))
    label_font = ImageFont.truetype(str(FONT_PATH), 22)
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
                "source": str(src.relative_to(ASSET_DIR)),
                "output": str(out.relative_to(ASSET_DIR)),
                "telop": [
                    "".join(plain_segments(line))
                    for line in frame["segments"]
                ],
                "box": frame["box"],
            }
        )

    make_contact_sheet(outputs)
    (OUTPUT_DIR / "telop_manifest.json").write_text(
        json.dumps(
            {
                "title": "紹介状やお薬手帳、なぜ検査前に確認するの？",
                "style": "要点だけ、1画面1メッセージ、白背景、濃紺文字、重要語のみアクセント",
                "font": str(FONT_PATH),
                "size": {"width": W, "height": H},
                "frames": manifest,
                "contact_sheet": str(CONTACT_SHEET.relative_to(ASSET_DIR)),
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
