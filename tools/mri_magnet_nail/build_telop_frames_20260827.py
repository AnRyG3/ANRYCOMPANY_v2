from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
BASE = ROOT / "reel_assets" / "mri_series" / "mri_magnet_nail_20260827" / "images"
OUT = ROOT / "reel_assets" / "mri_series" / "mri_magnet_nail_20260827" / "telop_frames"
CONTACT = OUT / "contact_sheet_20260827_telop_frames.jpg"
TEXTS = OUT / "telop_texts_20260827.txt"
MANIFEST = OUT / "telop_manifest_20260827.json"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (16, 36, 55, 255)
ACCENT = (0, 104, 150, 255)
WHITE = (255, 255, 255, 242)
SHADOW = (0, 0, 0, 36)

Y_POSITIONS = {
    "top": 230,
    "center": H // 2,
    "bottom": 1320,
}


CUTS = [
    {
        "src": "frame_01_mri_reservation_magnet_nail_patient.png",
        "out": "telop_01_mri_reservation_magnet_nail_patient.png",
        "lines": [["MRI予約", "あるのに"], ["ネイル", "大丈夫？"]],
        "highlights": {"MRI予約", "ネイル"},
        "position": "top",
    },
    {
        "src": "frame_02_mri_questionnaire_nail_item.png",
        "out": "telop_02_mri_questionnaire_nail_item.png",
        "lines": [["問診", "で"], ["聞かれることも"]],
        "highlights": {"問診"},
        "position": "top",
    },
    {
        "src": "frame_03_magnet_nail_closeup.png",
        "out": "telop_03_magnet_nail_closeup.png",
        "lines": [["一部のネイルに"], ["金属", "成分も"]],
        "highlights": {"金属"},
        "position": "center",
    },
    {
        "src": "frame_04_clean_mri_room.png",
        "out": "telop_04_clean_mri_room.png",
        "lines": [["MRI", "は"], ["強い磁石を使います"]],
        "highlights": {"MRI"},
        "position": "center",
    },
    {
        "src": "frame_05_patient_checks_nails_waiting.png",
        "out": "telop_05_patient_checks_nails_waiting.png",
        "lines": [["熱", "や", "変色"], ["画像への影響も"]],
        "highlights": {"熱", "変色"},
        "position": "top",
    },
    {
        "src": "frame_06_rt_checks_patient_nails.png",
        "out": "telop_06_rt_checks_patient_nails.png",
        "lines": [["いちばん大事なのは"], ["体", "へのリスク"]],
        "highlights": {"体"},
        "position": "top",
    },
    {
        "src": "frame_07_patient_enters_mri_bore_hands_inside.png",
        "out": "telop_07_patient_enters_mri_bore_hands_inside.png",
        "lines": [["手元", "が離れていても"], ["装置", "の中に入ります"]],
        "highlights": {"手元", "装置"},
        "position": "top",
    },
    {
        "src": "frame_08_patient_prepares_nail_removal.png",
        "out": "telop_08_patient_prepares_nail_removal.png",
        "lines": [["予約検査", "なら"], ["前もって準備を"]],
        "highlights": {"予約検査"},
        "position": "top",
    },
    {
        "src": "frame_09_mri_nail_consult_rt.png",
        "out": "telop_09_mri_nail_consult_rt.png",
        "lines": [["外せない時は"], ["先に", "相談"]],
        "highlights": {"相談"},
        "position": "top",
    },
    {
        "src": "frame_10_save_cta_phone.png",
        "out": "telop_10_save_cta_phone.png",
        "lines": [["検査前日や受付前に"], ["見返せるよう", "保存"]],
        "highlights": {"保存"},
        "position": "top",
    },
    {
        "src": "frame_11_rt_closing_mri_corridor.png",
        "out": "telop_11_rt_closing_mri_corridor.png",
        "lines": [["検査前の疑問も"], ["やさしく発信中"]],
        "highlights": {"疑問"},
        "position": "bottom",
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


def fit_font(draw: ImageDraw.ImageDraw, lines: list[list[str]], max_w: int) -> ImageFont.FreeTypeFont:
    for size in range(66, 37, -2):
        fnt = font(size)
        if max(line_width(draw, line, fnt) for line in lines) <= max_w:
            return fnt
    return font(38)


def draw_centered_line(
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
        fill = ACCENT if part in highlights else NAVY
        draw.text((x, y), part, font=fnt, fill=fill, anchor="la")
        x += segment_width(draw, part, fnt) + gap


def box_y(position: str, box_h: int) -> int:
    center_y = Y_POSITIONS[position]
    if position == "top":
        return center_y
    if position == "bottom":
        return center_y - box_h
    return center_y - box_h // 2


def add_telop(img: Image.Image, lines: list[list[str]], highlights: set[str], position: str) -> Image.Image:
    img = cover(img.convert("RGB"), (W, H)).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    fnt = fit_font(draw, lines, 800)
    size = fnt.size
    line_h = int(size * 1.18)
    pad_x, pad_y = 58, 40
    box_w = min(910, max(line_width(draw, line, fnt) for line in lines) + pad_x * 2)
    box_h = line_h * len(lines) + pad_y * 2
    x1 = (W - box_w) // 2
    y1 = box_y(position, box_h)
    x2 = x1 + box_w
    y2 = y1 + box_h

    draw.rounded_rectangle((x1 + 5, y1 + 7, x2 + 5, y2 + 7), radius=30, fill=SHADOW)
    draw.rounded_rectangle((x1, y1, x2, y2), radius=30, fill=WHITE)

    first_y = y1 + pad_y + int(size * 0.1)
    for i, line in enumerate(lines):
        draw_centered_line(draw, first_y + i * line_h, line, fnt, highlights)

    img.alpha_composite(overlay)
    return img.convert("RGB")


def make_contact_sheet(paths: list[Path]) -> None:
    cols, rows = 3, 4
    tw, th = 240, 426
    label_h = 34
    sheet = Image.new("RGB", (tw * cols, (th + label_h) * rows), (245, 245, 245))
    draw = ImageDraw.Draw(sheet)
    label_font = ImageFont.load_default()
    for i, path in enumerate(paths):
        thumb = cover(Image.open(path).convert("RGB"), (tw, th))
        x = (i % cols) * tw
        y = (i // cols) * (th + label_h)
        sheet.paste(thumb, (x, y))
        draw.text((x + 8, y + th + 8), path.stem[:28], fill=(0, 0, 0), font=label_font)
    sheet.save(CONTACT, quality=92)


def main() -> None:
    if not FONT_PATH.exists():
        raise FileNotFoundError(f"Required telop font not found: {FONT_PATH}")

    OUT.mkdir(parents=True, exist_ok=True)
    out_paths: list[Path] = []
    text_lines: list[str] = []
    manifest = []

    for i, cut in enumerate(CUTS, start=1):
        src = BASE / cut["src"]
        out = OUT / cut["out"]
        if not src.exists():
            raise FileNotFoundError(src)
        add_telop(Image.open(src), cut["lines"], cut["highlights"], cut["position"]).save(out, quality=95)
        out_paths.append(out)
        text = " / ".join("".join(line) for line in cut["lines"])
        text_lines.append(f"{i:02d}. {text}")
        manifest.append(
            {
                "index": i,
                "source": str(src),
                "output": str(out),
                "telop": cut["lines"],
                "highlights": sorted(cut["highlights"]),
                "x_axis": "center",
                "y_position": cut["position"],
                "font": str(FONT_PATH),
            }
        )

    make_contact_sheet(out_paths)
    TEXTS.write_text("\n".join(text_lines) + "\n", encoding="utf-8-sig")
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"created {len(out_paths)} telop frames")
    print(OUT)
    print(CONTACT)


if __name__ == "__main__":
    main()
