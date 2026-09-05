from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
BASE = ROOT / "reel_assets" / "pre_exam_series" / "dentures_mri_ct_samples"
OUT = BASE / "telop_frames"
CONTACT = OUT / "contact_sheet_telop_frames.png"
MANIFEST = OUT / "telop_manifest.json"
TEXTS = OUT / "telop_texts.txt"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (16, 36, 55, 255)
ACCENT = (0, 104, 150, 255)
WHITE = (255, 255, 255, 238)
SHADOW = (0, 0, 0, 38)

POSITIONS = {
    "top": 230,
    "center": 825,
    "bottom": 1260,
}

CUTS = [
    {
        "src": "frame_01_home_denture_case.png",
        "out": "telop_01_home_denture_case.png",
        "lines": [["MRI", "や", "頭のCT"], ["入れ歯", "外すのかな"]],
        "highlights": ["MRI", "頭のCT", "入れ歯"],
        "position": "top",
    },
    {
        "src": "frame_02_reception_explanation.png",
        "out": "telop_02_reception_explanation.png",
        "lines": [["外せる", "入れ歯", "は"], ["検査前", "に外します"]],
        "highlights": ["入れ歯", "検査前"],
        "position": "top",
    },
    {
        "src": "frame_03_mri_entrance_case_tray.png",
        "out": "telop_03_mri_entrance_case_tray.png",
        "lines": [["MRI", "では"], ["金属", "が影響することも"]],
        "highlights": ["MRI", "金属"],
        "position": "center",
    },
    {
        "src": "frame_04_ct_flat_table_case.png",
        "out": "telop_04_ct_flat_table_case.png",
        "lines": [["頭やお顔の", "CT", "でも"], ["外すことがあります"]],
        "highlights": ["CT"],
        "position": "top",
    },
    {
        "src": "frame_05_tech_monitor_artifact.png",
        "out": "telop_05_tech_monitor_artifact.png",
        "lines": [["口元", "や", "顎", "の周りが"], ["見えにくいことも"]],
        "highlights": ["口元", "顎"],
        "position": "top",
    },
    {
        "src": "frame_06_image_comparison.png",
        "out": "telop_06_image_comparison.png",
        "lines": [["外しておくと"], ["確認", "しやすくなります"]],
        "highlights": ["確認"],
        "position": "top",
    },
    {
        "src": "frame_07_pack_case_bag.png",
        "out": "telop_07_pack_case_bag.png",
        "lines": [["画像", "を見やすくする"], ["ための案内です"]],
        "highlights": ["画像"],
        "position": "top",
    },
    {
        "src": "frame_08_case_handoff.png",
        "out": "telop_08_case_handoff.png",
        "lines": [["入れ歯ケース", "があると"], ["検査中", "も安心です"]],
        "highlights": ["入れ歯ケース", "検査中"],
        "position": "bottom",
    },
    {
        "src": "frame_09_after_exam_case.png",
        "out": "telop_09_after_exam_case.png",
        "lines": [["終わったら"], ["すぐ戻せます"]],
        "highlights": ["すぐ"],
        "position": "top",
    },
    {
        "src": "frame_10_cta_save_review.png",
        "out": "telop_10_cta_save_review.png",
        "lines": [["検査前日", "に見返せるよう"], ["保存", "しておいてください"]],
        "highlights": ["検査前日", "保存"],
        "position": "center",
    },
]


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size)


def cover(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    w, h = size
    scale = max(w / img.width, h / img.height)
    resized = img.resize((int(img.width * scale), int(img.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - w) // 2
    top = (resized.height - h) // 2
    return resized.crop((left, top, left + w, top + h))


def segment_width(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def line_width(draw: ImageDraw.ImageDraw, line: list[str], fnt: ImageFont.FreeTypeFont) -> int:
    gap = int(fnt.size * 0.08)
    return sum(segment_width(draw, part, fnt) for part in line) + gap * (len(line) - 1)


def fit_font(draw: ImageDraw.ImageDraw, lines: list[list[str]], max_w: int, start: int = 68) -> int:
    size = start
    while size >= 40:
        fnt = font(size)
        if max(line_width(draw, line, fnt) for line in lines) <= max_w:
            return size
        size -= 2
    return 40


def draw_segmented_line(
    draw: ImageDraw.ImageDraw,
    y: int,
    line: list[str],
    fnt: ImageFont.FreeTypeFont,
    highlights: set[str],
) -> None:
    gap = int(fnt.size * 0.08)
    total = line_width(draw, line, fnt)
    x = (W - total) // 2
    for part in line:
        draw.text((x, y), part, font=fnt, fill=ACCENT if part in highlights else NAVY, anchor="la")
        x += segment_width(draw, part, fnt) + gap


def add_telop(img: Image.Image, spec: dict) -> Image.Image:
    base = cover(img.convert("RGB"), (W, H)).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    lines = spec["lines"]
    highlights = set(spec["highlights"])
    size = fit_font(draw, lines, 850)
    fnt = font(size)
    line_h = int(size * 1.2)
    pad_x, pad_y = 56, 40
    box_w = min(930, max(line_width(draw, line, fnt) for line in lines) + pad_x * 2)
    box_h = line_h * len(lines) + pad_y * 2
    box_x1 = (W - box_w) // 2
    box_y1 = POSITIONS[spec["position"]]
    box_x2 = box_x1 + box_w
    box_y2 = box_y1 + box_h

    draw.rounded_rectangle((box_x1 + 5, box_y1 + 7, box_x2 + 5, box_y2 + 7), radius=28, fill=SHADOW)
    draw.rounded_rectangle((box_x1, box_y1, box_x2, box_y2), radius=28, fill=WHITE)

    first_y = box_y1 + pad_y + int(size * 0.1)
    for i, line in enumerate(lines):
        draw_segmented_line(draw, first_y + i * line_h, line, fnt, highlights)

    base.alpha_composite(overlay)
    return base.convert("RGB")


def make_contact_sheet(paths: list[Path]) -> None:
    cols, rows = 2, 5
    tw, th = 270, 480
    label_h = 34
    sheet = Image.new("RGB", (tw * cols, (th + label_h) * rows), (245, 245, 245))
    draw = ImageDraw.Draw(sheet)
    label_font = ImageFont.load_default()
    for i, path in enumerate(paths):
        thumb = cover(Image.open(path).convert("RGB"), (tw, th))
        x = (i % cols) * tw
        y = (i // cols) * (th + label_h)
        sheet.paste(thumb, (x, y))
        draw.text((x + 8, y + th + 8), path.name[:34], fill=(0, 0, 0), font=label_font)
    sheet.save(CONTACT)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    text_lines: list[str] = []
    manifest = {
        "style": "white rounded rectangle 93% opacity, dark navy M PLUS Rounded 1c Bold, word-only blue emphasis",
        "placement_policy": "x-axis centered; positions are top, center, or bottom only",
        "frames": [],
    }

    for idx, spec in enumerate(CUTS, start=1):
        src = BASE / spec["src"]
        out = OUT / spec["out"]
        add_telop(Image.open(src), spec).save(out, quality=95)
        outputs.append(out)
        plain = " / ".join("".join(line) for line in spec["lines"])
        text_lines.append(f"{idx:02d}. {plain} [{spec['position']}]")
        manifest["frames"].append(
            {
                "source": str(src),
                "output": str(out),
                "telop": ["".join(line) for line in spec["lines"]],
                "highlights": spec["highlights"],
                "position": spec["position"],
            }
        )

    make_contact_sheet(outputs)
    manifest["contact_sheet"] = str(CONTACT)
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8-sig")
    TEXTS.write_text("\n".join(text_lines) + "\n", encoding="utf-8-sig")
    print(f"created {len(outputs)} telop frames")
    print(OUT)
    print(CONTACT)


if __name__ == "__main__":
    main()
