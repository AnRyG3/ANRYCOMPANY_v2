from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
BASE = ROOT / "reel_assets" / "mri_series" / "mri_nicotine_patch_20260907_images"
OUT = ROOT / "reel_assets" / "mri_series" / "mri_nicotine_patch_20260907_telop_frames"
CONTACT = OUT / "contact_sheet_20260907_telop_frames.png"
TEXTS = OUT / "telop_texts_20260907.txt"
MANIFEST = OUT / "telop_manifest_20260907.json"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (12, 34, 58, 255)
ACCENT = (0, 104, 150, 255)
PANEL = (255, 255, 255, 240)
PANEL_EDGE = (255, 255, 255, 255)
SHADOW = (0, 0, 0, 42)


FRAMES = [
    {
        "src": "frame_01_hook_patient_patch_mri.png",
        "out": "telop_01_hook_patient_patch_mri.png",
        "lines": [["禁煙パッチ"], ["MRI", "前どうする？"]],
        "highlights": {"禁煙パッチ", "MRI"},
        "position": "bottom",
    },
    {
        "src": "frame_02_reception_disclose_patch.png",
        "out": "telop_02_reception_disclose_patch.png",
        "lines": [["受付", "で"], ["先に", "伝えてください"]],
        "highlights": {"受付", "先に"},
        "position": "bottom",
    },
    {
        "src": "frame_03_patch_before_mri.png",
        "out": "telop_03_patch_before_mri.png",
        "lines": [["MRI", "の前に"], ["外す", "必要があります"]],
        "highlights": {"MRI", "外す"},
        "position": "bottom",
    },
    {
        "src": "frame_04_patch_mri_attention.png",
        "out": "telop_04_patch_mri_attention.png",
        "lines": [["貼った部分が"], ["熱く", "なることも"]],
        "highlights": {"熱く"},
        "position": "bottom",
    },
    {
        "src": "frame_05_confirm_timing_with_staff.png",
        "out": "telop_05_confirm_timing_with_staff.png",
        "lines": [["外す", "タイミング", "は"], ["スタッフに", "確認"]],
        "highlights": {"タイミング", "確認"},
        "position": "bottom",
    },
    {
        "src": "frame_06_reassured_after_explanation.png",
        "out": "telop_06_reassured_after_explanation.png",
        "lines": [["先に", "伝えれば"], ["対応", "してもらえます"]],
        "highlights": {"先に", "対応"},
        "position": "bottom",
    },
    {
        "src": "frame_07_save_and_share_cta.png",
        "out": "telop_07_save_and_share_cta.png",
        "lines": [["予約票と一緒に"], ["保存", "・", "共有"]],
        "highlights": {"保存", "共有"},
        "position": "center",
    },
]


def font(size: int) -> ImageFont.FreeTypeFont:
    if not FONT_PATH.exists():
        raise FileNotFoundError(FONT_PATH)
    return ImageFont.truetype(str(FONT_PATH), size)


def cover(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    img = img.convert("RGB")
    scale = max(size[0] / img.width, size[1] / img.height)
    resized = img.resize((int(img.width * scale), int(img.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - size[0]) // 2
    top = (resized.height - size[1]) // 2
    return resized.crop((left, top, left + size[0], top + size[1]))


def text_width(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def part_color(part: str, highlights: set[str]) -> tuple[int, int, int, int]:
    if part in highlights:
        return ACCENT
    return NAVY


def line_width(draw: ImageDraw.ImageDraw, line: list[str], fnt: ImageFont.FreeTypeFont) -> int:
    gap = int(fnt.size * 0.08)
    return sum(text_width(draw, part, fnt) for part in line) + gap * (len(line) - 1)


def fit_font(draw: ImageDraw.ImageDraw, lines: list[list[str]], max_w: int, max_h: int):
    for size in range(66, 41, -2):
        fnt = font(size)
        line_h = int(size * 1.18)
        total_h = line_h * len(lines)
        if max(line_width(draw, line, fnt) for line in lines) <= max_w and total_h <= max_h:
            return fnt, line_h
    return font(42), 50


def box_y(position: str, box_h: int) -> int:
    if position == "top":
        return 176
    if position == "bottom":
        return 1270
    return (H - box_h) // 2


def draw_telop(base: Image.Image, frame: dict) -> tuple[Image.Image, tuple[int, int, int, int]]:
    img = cover(base, (W, H)).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    lines = frame["lines"]
    fnt, line_h = fit_font(draw, lines, 790, 210)
    pad_x, pad_y = 54, 32
    box_w = min(936, max(line_width(draw, line, fnt) for line in lines) + pad_x * 2)
    box_h = line_h * len(lines) + pad_y * 2
    x0 = (W - box_w) // 2
    y0 = box_y(frame["position"], box_h)
    x1, y1 = x0 + box_w, y0 + box_h

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((x0 + 6, y0 + 8, x1 + 6, y1 + 8), radius=28, fill=SHADOW)
    overlay.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(7)))
    draw.rounded_rectangle((x0, y0, x1, y1), radius=28, fill=PANEL)
    draw.rounded_rectangle((x0 + 7, y0 + 7, x1 - 7, y1 - 7), radius=22, outline=PANEL_EDGE, width=4)

    first_y = y0 + pad_y + int(fnt.size * 0.05)
    gap = int(fnt.size * 0.08)
    for row, line in enumerate(lines):
        total_w = line_width(draw, line, fnt)
        x = (W - total_w) // 2
        y = first_y + row * line_h
        for part in line:
            draw.text((x, y), part, font=fnt, fill=part_color(part, frame["highlights"]))
            x += text_width(draw, part, fnt) + gap

    img.alpha_composite(overlay)
    return img.convert("RGB"), (x0, y0, x1, y1)


def make_contact_sheet(paths: list[Path]) -> None:
    cols = 4
    thumb_w, thumb_h = 216, 384
    label_h = 36
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (246, 248, 250))
    draw = ImageDraw.Draw(sheet)
    label_font = font(20)
    for i, path in enumerate(paths):
        thumb = cover(Image.open(path), (thumb_w, thumb_h))
        x = (i % cols) * thumb_w
        y = (i // cols) * (thumb_h + label_h)
        sheet.paste(thumb, (x, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill=(255, 255, 255))
        draw.text((x + 8, y + thumb_h + 7), f"{i + 1:02d}", font=label_font, fill=NAVY)
    sheet.save(CONTACT)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    outputs = []
    manifest = []
    text_lines = []

    for i, frame in enumerate(FRAMES, start=1):
        src = BASE / frame["src"]
        out = OUT / frame["out"]
        if not src.exists():
            raise FileNotFoundError(src)
        image, box = draw_telop(Image.open(src), frame)
        image.save(out, quality=95)
        outputs.append(out)
        text = " / ".join("".join(line) for line in frame["lines"])
        text_lines.append(f"{i:02d}. {text}")
        manifest.append(
            {
                "index": i,
                "source": str(src.relative_to(ROOT)),
                "output": str(out.relative_to(ROOT)),
                "telop": frame["lines"],
                "highlights": sorted(frame["highlights"]),
                "position": frame["position"],
                "box": list(box),
                "font": str(FONT_PATH),
            }
        )

    make_contact_sheet(outputs)
    TEXTS.write_text("\n".join(text_lines) + "\n", encoding="utf-8-sig")
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(f"created {len(outputs)} telop frames")
    print(OUT)
    print(CONTACT)


if __name__ == "__main__":
    main()
