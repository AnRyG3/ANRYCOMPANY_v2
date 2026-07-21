from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "pre_exam_series" / "ask_again_explanation_f40"
INPUT_DIR = ASSET_DIR / "final_frames"
OUTPUT_DIR = ASSET_DIR / "telop_frames"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

NAVY = (20, 42, 74, 255)
WHITE_PANEL = (255, 255, 255, 238)
SHADOW = (0, 0, 0, 42)

FRAMES = [
    (
        "frame_01_patient_confused.png",
        "frame_01_telop.png",
        ["検査説明、正直", "よくわからなかった"],
        "bottom",
    ),
    (
        "frame_02_patient_silent.png",
        "frame_02_telop.png",
        ["聞き返すのが", "恥ずかしい…"],
        "bottom",
    ),
    (
        "frame_03_once_is_ok.png",
        "frame_03_telop.png",
        ["一度で全部", "わからなくてOK"],
        "top",
    ),
    (
        "frame_04_terms_are_hard.png",
        "frame_04_telop.png",
        ["専門用語は", "難しくて自然"],
        "top",
    ),
    (
        "frame_05_patient_asks_again.png",
        "frame_05_telop.png",
        ["「もう一度お願いします」", "で大丈夫"],
        "top",
    ),
    (
        "frame_06_confirmation_sheet.png",
        "frame_06_telop.png",
        ["わかったふりより", "確認が安心"],
        "top",
    ),
    (
        "frame_07_rt_reexplains.png",
        "frame_07_telop.png",
        ["診療放射線技師が", "もう一度説明します"],
        "top",
    ),
    (
        "frame_08_patient_relieved.png",
        "frame_08_telop.png",
        ["聞き返すことは", "おかしくありません"],
        "bottom",
    ),
    (
        "frame_09_save_cta_phone.png",
        "frame_09_telop.png",
        ["保存して", "検査前に見返す"],
        "bottom",
    ),
    (
        "frame_10_follow_cta_rt.png",
        "frame_10_telop.png",
        ["フォローして", "不安を減らそう"],
        "top",
    ),
]


def text_bbox(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    return right - left, bottom - top


def fit_font(draw: ImageDraw.ImageDraw, lines: list[str], max_width: int) -> ImageFont.FreeTypeFont:
    for size in range(70, 40, -2):
        font = ImageFont.truetype(str(FONT_PATH), size)
        widest = max(text_bbox(draw, line, font)[0] for line in lines)
        if widest <= max_width:
            return font
    return ImageFont.truetype(str(FONT_PATH), 40)


def panel_position(position: str, image_w: int, image_h: int, panel_w: int, panel_h: int) -> tuple[int, int]:
    x = (image_w - panel_w) // 2
    if position == "bottom":
        y = image_h - panel_h - 280
    elif position == "center":
        y = (image_h - panel_h) // 2
    else:
        y = 210
    return x, y


def render_frame(src: Path, dst: Path, lines: list[str], position: str) -> None:
    image = Image.open(src).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shadow_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    shadow = ImageDraw.Draw(shadow_layer)

    max_text_width = int(image.width * 0.76)
    font = fit_font(draw, lines, max_text_width)
    sizes = [text_bbox(draw, line, font) for line in lines]
    line_gap = 16
    pad_x = 52
    pad_y = 30
    text_w = max(width for width, _ in sizes)
    text_h = sum(height for _, height in sizes) + line_gap * (len(lines) - 1)
    panel_w = min(image.width - 136, max(620, text_w + pad_x * 2))
    panel_h = text_h + pad_y * 2 + 6
    x, y = panel_position(position, image.width, image.height, panel_w, panel_h)

    shadow.rounded_rectangle((x + 8, y + 10, x + panel_w + 8, y + panel_h + 10), radius=30, fill=SHADOW)
    draw.rounded_rectangle((x, y, x + panel_w, y + panel_h), radius=30, fill=WHITE_PANEL)

    current_y = y + pad_y
    for line, (_, line_h) in zip(lines, sizes):
        line_w, _ = text_bbox(draw, line, font)
        draw.text((x + (panel_w - line_w) // 2, current_y), line, font=font, fill=NAVY)
        current_y += line_h + line_gap

    composed = Image.alpha_composite(image, shadow_layer)
    composed = Image.alpha_composite(composed, overlay)
    composed.convert("RGB").save(dst, quality=95)


def make_contact_sheet(files: list[Path]) -> None:
    thumb_w, thumb_h = 270, 480
    cols = 5
    rows = math.ceil(len(files) / cols)
    sheet = Image.new("RGB", (thumb_w * cols, thumb_h * rows), (28, 31, 33))
    draw = ImageDraw.Draw(sheet)
    label_font = ImageFont.truetype(str(FONT_PATH), 24)
    for i, path in enumerate(files):
        img = Image.open(path).convert("RGB")
        img.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (i % cols) * thumb_w
        y = (i // cols) * thumb_h
        sheet.paste(img, (x + (thumb_w - img.width) // 2, y + (thumb_h - img.height) // 2))
        draw.rectangle((x, y, x + 58, y + 34), fill=(20, 42, 74))
        draw.text((x + 10, y + 4), f"{i + 1:02d}", font=label_font, fill=(255, 255, 255))
    sheet.save(OUTPUT_DIR / "_contact_sheet.png", quality=92)


def main() -> None:
    if not FONT_PATH.exists():
        raise FileNotFoundError(FONT_PATH)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []
    output_files = []
    for src_name, dst_name, lines, position in FRAMES:
        src = INPUT_DIR / src_name
        dst = OUTPUT_DIR / dst_name
        if not src.exists():
            raise FileNotFoundError(src)
        render_frame(src, dst, lines, position)
        output_files.append(dst)
        manifest.append(
            {
                "source": str(src.relative_to(ASSET_DIR)),
                "file": str(dst.relative_to(ASSET_DIR)),
                "telop": lines,
                "position": position,
            }
        )

    (OUTPUT_DIR / "telop_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    make_contact_sheet(output_files)
    print(OUTPUT_DIR)


if __name__ == "__main__":
    main()
