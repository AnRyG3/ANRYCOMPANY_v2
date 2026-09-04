from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "pre_exam_series" / "pacemaker_mri_20260901"
OUT_DIR = ASSET_DIR / "telop_frames"
CONTACT_SHEET = OUT_DIR / "contact_sheet_telop_frames.png"
TEXTS = OUT_DIR / "telop_texts_20260901.txt"
MANIFEST = OUT_DIR / "telop_manifest_20260901.json"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (12, 34, 58, 255)
ACCENT_BLUE = (0, 104, 150, 255)
PANEL = (255, 255, 255, 238)
PANEL_EDGE = (255, 255, 255, 255)
SHADOW = (0, 0, 0, 44)


FRAMES = [
    {
        "src": "sample_01_hook_home_mri_reservation.png",
        "out": "telop_01_hook_home_mri_reservation.png",
        "lines": [["ペースメーカー"], ["MRI", "受けられる？"]],
        "highlights": {"ペースメーカー", "MRI"},
        "position": "top",
    },
    {
        "src": "frame_02_reception_questionnaire.png",
        "out": "telop_02_reception_questionnaire.png",
        "lines": [["CT", "は"], ["通常どおり", "撮れることも"]],
        "highlights": {"CT", "通常どおり"},
        "position": "center",
    },
    {
        "src": "frame_03_ct_room_patient_rt.png",
        "out": "telop_03_ct_room_patient_rt.png",
        "lines": [["レントゲン・CT"], ["多くは", "そのまま"]],
        "highlights": {"CT", "そのまま"},
        "position": "top",
    },
    {
        "src": "frame_04_mri_room_entrance.png",
        "out": "telop_04_mri_room_entrance.png",
        "lines": [["MRI", "は"], ["少し確認が必要"]],
        "highlights": {"MRI", "確認"},
        "position": "center",
    },
    {
        "src": "frame_05_rt_precheck_phone_pc.png",
        "out": "telop_05_rt_precheck_phone_pc.png",
        "lines": [["かかりつけ以外では"], ["事前確認", "に時間も"]],
        "highlights": {"事前確認"},
        "position": "top",
    },
    {
        "src": "sample_06_notebook_card.png",
        "out": "telop_06_notebook_card.png",
        "lines": [["必要なのは"], ["手帳", "と", "MRIカード"]],
        "highlights": {"手帳", "MRIカード"},
        "position": "center",
    },
    {
        "src": "frame_07_patient_packing_notebook.png",
        "out": "telop_07_patient_packing_notebook.png",
        "lines": [["確認には"], ["手帳・カード", "が大切"]],
        "highlights": {"手帳・カード"},
        "position": "center",
    },
    {
        "src": "frame_08_rt_returns_notebook_card.png",
        "out": "telop_08_rt_returns_notebook_card.png",
        "lines": [["あると"], ["準備が", "進めやすい"]],
        "highlights": {"準備"},
        "position": "top",
    },
    {
        "src": "frame_09_calendar_notebook_card.png",
        "out": "telop_09_calendar_notebook_card.png",
        "lines": [["MRI予約が決まったら"], ["まず", "手帳", "を用意"]],
        "highlights": {"手帳"},
        "position": "top",
    },
    {
        "src": "frame_10_patient_leaving_hospital.png",
        "out": "telop_10_patient_leaving_hospital.png",
        "lines": [["時間がかかるのは"], ["丁寧に", "確認するため"]],
        "highlights": {"確認"},
        "position": "top",
    },
    {
        "src": "frame_11_cta_save_phone.png",
        "out": "telop_11_cta_save_phone.png",
        "lines": [["MRI予約の前に"], ["見返せるよう", "保存"]],
        "highlights": {"MRI予約", "保存"},
        "position": "top",
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
    for size in range(66, 39, -2):
        fnt = font(size)
        line_h = int(size * 1.16)
        total_h = line_h * len(lines)
        if max(line_width(draw, line, fnt) for line in lines) <= max_w and total_h <= max_h:
            return fnt, line_h
    return font(40), 48


def box_for(position: str, box_h: int) -> tuple[int, int, int, int]:
    x0, x1 = 72, W - 72
    if position == "center":
        y0 = (H - box_h) // 2
    elif position == "bottom":
        y0 = 1268
    else:
        y0 = 176
    return x0, y0, x1, y0 + box_h


def draw_telop(base: Image.Image, frame: dict) -> Image.Image:
    img = cover(base, (W, H)).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    lines = frame["lines"]
    fnt, line_h = fit_font(draw, lines, 790, 220)
    pad_x, pad_y = 56, 34
    box_w = min(936, max(line_width(draw, line, fnt) for line in lines) + pad_x * 2)
    box_h = line_h * len(lines) + pad_y * 2
    x0 = (W - box_w) // 2
    _, y0, _, y1 = box_for(frame["position"], box_h)
    x1 = x0 + box_w

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((x0 + 6, y0 + 8, x1 + 6, y1 + 8), radius=30, fill=SHADOW)
    overlay.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(7)))
    draw.rounded_rectangle((x0, y0, x1, y1), radius=30, fill=PANEL)
    draw.rounded_rectangle((x0 + 7, y0 + 7, x1 - 7, y1 - 7), radius=24, outline=PANEL_EDGE, width=4)

    first_y = y0 + pad_y + int(fnt.size * 0.06)
    gap = int(fnt.size * 0.08)
    for row, line in enumerate(lines):
        total_w = line_width(draw, line, fnt)
        x = (W - total_w) // 2
        y = first_y + row * line_h
        for part in line:
            color = ACCENT_BLUE if part in frame["highlights"] else NAVY
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
    sheet.save(CONTACT_SHEET)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    manifest = []
    text_lines = []

    for i, frame in enumerate(FRAMES, start=1):
        src = ASSET_DIR / frame["src"]
        out = OUT_DIR / frame["out"]
        if not src.exists():
            raise FileNotFoundError(src)
        draw_telop(Image.open(src), frame).save(out, quality=95)
        outputs.append(out)
        telop = " / ".join("".join(line) for line in frame["lines"])
        text_lines.append(f"{i:02d}. {telop}")
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
    print(OUT_DIR)
    print(CONTACT_SHEET)


if __name__ == "__main__":
    main()
