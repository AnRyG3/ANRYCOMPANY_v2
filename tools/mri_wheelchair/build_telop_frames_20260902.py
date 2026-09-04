from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
BASE = ROOT / "reel_assets" / "mri_series" / "mri_wheelchair_20260902_images"
OUT = ROOT / "reel_assets" / "mri_series" / "mri_wheelchair_20260902_telop_frames"
CONTACT = OUT / "contact_sheet_20260902_telop_frames.png"
TEXTS = OUT / "telop_texts_20260902.txt"
MANIFEST = OUT / "telop_manifest_20260902.json"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (12, 34, 58, 255)
ACCENT = (0, 104, 150, 255)
PANEL = (255, 255, 255, 240)
PANEL_EDGE = (255, 255, 255, 255)
SHADOW = (0, 0, 0, 42)


FRAMES = [
    {
        "src": "01_opening_wheelchair_home.png",
        "out": "telop_01_opening_wheelchair_home.png",
        "lines": [["車椅子", "だけど"], ["MRI", "受けられる？"]],
        "highlights": {"車椅子", "MRI"},
        "position": "top",
    },
    {
        "src": "02_reception_consultation.png",
        "out": "telop_02_reception_consultation.png",
        "lines": [["車椅子", "の方も"], ["MRI検査", "は受けられます"]],
        "highlights": {"車椅子", "MRI検査"},
        "position": "center",
    },
    {
        "src": "03_wheelchair_outside_mri_room.png",
        "out": "telop_03_wheelchair_outside_mri_room.png",
        "lines": [["ただし"], ["車椅子", "はMRI室へ入れません"]],
        "highlights": {"車椅子", "MRI室"},
        "position": "center",
    },
    {
        "src": "04_prepare_single_table.png",
        "out": "telop_04_prepare_single_table.png",
        "lines": [["室外", "で"], ["寝台", "へ移る方法も"]],
        "highlights": {"室外", "寝台"},
        "position": "center",
    },
    {
        "src": "05_transfer_support_single_table.png",
        "out": "telop_05_transfer_support_single_table.png",
        "lines": [["移乗", "は"], ["職員", "がサポート"]],
        "highlights": {"移乗", "職員"},
        "position": "bottom",
    },
    {
        "src": "06_on_table_ready_for_mri_v3_flat_table.png",
        "out": "telop_06_on_table_ready_for_mri.png",
        "lines": [["寝台", "に移ったら"], ["検査へ進みます"]],
        "highlights": {"寝台"},
        "position": "bottom",
    },
    {
        "src": "07_pre_exam_consult_support_needs.png",
        "out": "telop_07_pre_exam_consult_support_needs.png",
        "lines": [["支えが必要", "なら"], ["予約時", "に伝えて"]],
        "highlights": {"支えが必要", "予約時"},
        "position": "top",
    },
    {
        "src": "08_return_to_wheelchair_after_exam.png",
        "out": "telop_08_return_to_wheelchair_after_exam.png",
        "lines": [["検査後", "も"], ["同じように戻ります"]],
        "highlights": {"検査後"},
        "position": "bottom",
    },
    {
        "src": "09_appointment_note_wheelchair.png",
        "out": "telop_09_appointment_note_wheelchair.png",
        "lines": [["痛い場所", "も"], ["一緒に伝えてOK"]],
        "highlights": {"痛い場所"},
        "position": "center",
    },
    {
        "src": "10_save_cta_phone.png",
        "out": "telop_10_save_cta_phone.png",
        "lines": [["検査前日", "に"], ["見返せるよう", "保存"]],
        "highlights": {"検査前日", "保存"},
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


def line_width(draw: ImageDraw.ImageDraw, line: list[str], fnt: ImageFont.FreeTypeFont) -> int:
    gap = int(fnt.size * 0.08)
    return sum(text_width(draw, part, fnt) for part in line) + gap * (len(line) - 1)


def fit_font(draw: ImageDraw.ImageDraw, lines: list[list[str]], max_w: int, max_h: int):
    for size in range(64, 39, -2):
        fnt = font(size)
        line_h = int(size * 1.16)
        total_h = line_h * len(lines)
        if max(line_width(draw, line, fnt) for line in lines) <= max_w and total_h <= max_h:
            return fnt, line_h
    return font(40), 48


def box_y(position: str, box_h: int) -> int:
    if position == "bottom":
        return 1270
    if position == "center":
        return (H - box_h) // 2
    return 176


def draw_telop(base: Image.Image, frame: dict) -> Image.Image:
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

    first_y = y0 + pad_y + int(fnt.size * 0.06)
    gap = int(fnt.size * 0.08)
    for row, line in enumerate(lines):
        total_w = line_width(draw, line, fnt)
        x = (W - total_w) // 2
        y = first_y + row * line_h
        for part in line:
            color = ACCENT if part in frame["highlights"] else NAVY
            draw.text((x, y), part, font=fnt, fill=color)
            x += text_width(draw, part, fnt) + gap

    img.alpha_composite(overlay)
    return img.convert("RGB")


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
        draw_telop(Image.open(src), frame).save(out, quality=95)
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
