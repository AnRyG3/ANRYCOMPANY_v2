from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
BASE = ROOT / "reel_assets" / "mri_series" / "mri_color_contact_20260828_samples"
OUT = ROOT / "reel_assets" / "mri_series" / "mri_color_contact_20260828_telop_frames"
CONTACT = OUT / "contact_sheet_20260828_telop_frames.jpg"
TEXTS = OUT / "telop_texts_20260828.txt"
MANIFEST = OUT / "telop_manifest_20260828.json"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (16, 36, 55, 255)
ACCENT = (0, 104, 150, 255)
WHITE = (255, 255, 255, 242)
SHADOW = (0, 0, 0, 34)

Y_POSITIONS = {
    "top": 235,
    "center": H // 2,
    "bottom": 1320,
}


CUTS = [
    {
        "src": "sample_01_patient_contact_case.png",
        "out": "telop_01_patient_contact_case.png",
        "lines": [["MRI前日"], ["カラコン", "どうする？"]],
        "highlights": {"カラコン"},
        "position": "top",
    },
    {
        "src": "image_02_patient_checks_appointment.png",
        "out": "telop_02_patient_checks_appointment.png",
        "lines": [["問診", "で"], ["聞かれることも"]],
        "highlights": {"問診"},
        "position": "center",
    },
    {
        "src": "image_03_rt_clear_contact_explain.png",
        "out": "telop_03_rt_clear_contact_explain.png",
        "lines": [["透明コンタクト", "は"], ["施設で確認"]],
        "highlights": {"透明コンタクト"},
        "position": "top",
    },
    {
        "src": "image_04_colored_contact_still_life.png",
        "out": "telop_04_colored_contact_still_life.png",
        "lines": [["カラコン", "や"], ["縁取りレンズ", "は注意"]],
        "highlights": {"カラコン", "縁取りレンズ"},
        "position": "top",
    },
    {
        "src": "image_05_mri_precheck_counter.png",
        "out": "telop_05_mri_precheck_counter.png",
        "lines": [["MRI", "は"], ["強い磁場を使います"]],
        "highlights": {"MRI"},
        "position": "center",
    },
    {
        "src": "image_06_mri_contact_risk_calm.png",
        "out": "telop_06_mri_contact_risk_calm.png",
        "lines": [["金属成分", "で"], ["発熱や画像影響も"]],
        "highlights": {"金属成分"},
        "position": "center",
    },
    {
        "src": "image_07_patient_removes_contacts.png",
        "out": "telop_07_patient_removes_contacts.png",
        "lines": [["カラコン", "は"], ["外す案内も"]],
        "highlights": {"カラコン"},
        "position": "center",
    },
    {
        "src": "sample_08_patient_consults_rt.png",
        "out": "telop_08_patient_consults_rt.png",
        "lines": [["迷ったら"], ["受付で", "相談"]],
        "highlights": {"相談"},
        "position": "center",
    },
    {
        "src": "image_09_save_cta_phone.png",
        "out": "telop_09_save_cta_phone.png",
        "lines": [["前日・受付前に"], ["見返せるよう", "保存"]],
        "highlights": {"保存"},
        "position": "top",
    },
    {
        "src": "image_10_rt_closing.png",
        "out": "telop_10_rt_closing.png",
        "lines": [["検査前の疑問も"], ["診療放射線技師", "目線で"]],
        "highlights": {"疑問"},
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

    fnt = fit_font(draw, lines, 820)
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
        draw.text((x + 8, y + th + 8), path.stem[:30], fill=(0, 0, 0), font=label_font)
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
