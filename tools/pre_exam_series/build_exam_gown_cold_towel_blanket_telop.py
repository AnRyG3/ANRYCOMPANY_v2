from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
BASE = ROOT / "reel_assets" / "pre_exam_series" / "13_exam_gown_cold_towel_blanket" / "images"
OUT = ROOT / "reel_assets" / "pre_exam_series" / "13_exam_gown_cold_towel_blanket" / "telop"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"
TEXTS = OUT / "telop_texts.txt"
MANIFEST = OUT / "telop_manifest.json"
CONTACT = OUT / "contact_sheet_telop.jpg"

W, H = 1080, 1920
NAVY = (16, 36, 55, 255)
BLUE = (0, 104, 150, 255)
WHITE = (255, 255, 255, 242)
SHADOW = (0, 0, 0, 34)


CUTS = [
    {"src": "01_waiting_cold.png", "out": "01_waiting_cold_telop.png", "lines": [["検査着、"], ["思ったより", "寒い…"]], "highlights": {"寒い…"}, "position": "center"},
    {"src": "02_hesitating.png", "out": "02_hesitating_telop.png", "lines": [["これくらいで"], ["言っていいの？"]], "highlights": set(), "position": "center"},
    {"src": "03_speaking_up.png", "out": "03_speaking_up_telop.png", "lines": [["寒いときは"], ["スタッフ", "へ伝えて大丈夫"]], "highlights": {"スタッフ"}, "position": "center"},
    {"src": "04_exam_gown_light.png", "out": "04_exam_gown_light_telop.png", "lines": [["検査着は"], ["肌寒く", "感じることも"]], "highlights": {"肌寒く"}, "position": "center"},
    {"src": "05_towel_blanket_option.png", "out": "05_towel_blanket_option_telop.png", "lines": [["タオルケットで"], ["対応できることも"]], "highlights": {"タオルケットで"}, "position": "center"},
    {"src": "06_ask_technologist.png", "out": "06_ask_technologist_telop.png", "lines": [["タオルケットを"], ["お借りできますか？"]], "highlights": {"タオルケットを"}, "position": "center"},
    {"src": "07_staff_confirms.png", "out": "07_staff_confirms_telop.png", "lines": [["使えるものは"], ["スタッフが", "確認"]], "highlights": {"確認"}, "position": "center"},
    {"src": "08_lap_blanket.png", "out": "08_lap_blanket_telop.png", "lines": [["検査前の小さなことも"], ["遠慮なく", "相談を"]], "highlights": {"相談を"}, "position": "center"},
    {"src": "09_relief.png", "out": "09_relief_telop.png", "lines": [["寒さを"], ["我慢しなくて", "大丈夫"]], "highlights": {"大丈夫"}, "position": "center"},
    {"src": "10_save_cta_background.png", "out": "10_save_cta_telop.png", "lines": [["検査前に"], ["保存", "しておいてください"]], "highlights": {"保存"}, "position": "center"},
    {"src": "11_follow_cta_background.png", "out": "11_follow_cta_telop.png", "lines": [["次の投稿も"], ["フォロー", "で"]], "highlights": {"フォロー"}, "position": "center"},
]


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size)


def cover(img: Image.Image) -> Image.Image:
    scale = max(W / img.width, H / img.height)
    resized = img.resize((round(img.width * scale), round(img.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - W) // 2
    top = (resized.height - H) // 2
    return resized.crop((left, top, left + W, top + H))


def width(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def line_width(draw: ImageDraw.ImageDraw, line: list[str], fnt: ImageFont.FreeTypeFont) -> int:
    gap = round(fnt.size * 0.08)
    return sum(width(draw, part, fnt) for part in line) + gap * (len(line) - 1)


def fit_font(draw: ImageDraw.ImageDraw, lines: list[list[str]]) -> ImageFont.FreeTypeFont:
    for size in range(64, 39, -2):
        fnt = font(size)
        if max(line_width(draw, line, fnt) for line in lines) <= 820:
            return fnt
    return font(38)


def draw_line(draw: ImageDraw.ImageDraw, y: int, line: list[str], fnt: ImageFont.FreeTypeFont, highlights: set[str]) -> None:
    gap = round(fnt.size * 0.08)
    x = (W - line_width(draw, line, fnt)) // 2
    for part in line:
        draw.text((x, y), part, font=fnt, fill=BLUE if part in highlights else NAVY, anchor="la")
        x += width(draw, part, fnt) + gap


def telop_y(position: str, box_h: int) -> int:
    if position == "top":
        return 180
    if position == "center":
        return H // 2 - box_h // 2
    return 1260


def add_telop(img: Image.Image, lines: list[list[str]], highlights: set[str], position: str) -> Image.Image:
    base = cover(img.convert("RGB")).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    fnt = fit_font(draw, lines)
    line_h = round(fnt.size * 1.18)
    pad_x, pad_y = 58, 34
    box_w = min(900, max(line_width(draw, line, fnt) for line in lines) + pad_x * 2)
    box_h = line_h * len(lines) + pad_y * 2
    x1 = (W - box_w) // 2
    y1 = telop_y(position, box_h)
    x2, y2 = x1 + box_w, y1 + box_h
    draw.rounded_rectangle((x1 + 5, y1 + 7, x2 + 5, y2 + 7), radius=30, fill=SHADOW)
    draw.rounded_rectangle((x1, y1, x2, y2), radius=30, fill=WHITE)
    first_y = y1 + pad_y + round(fnt.size * 0.08)
    for index, line in enumerate(lines):
        draw_line(draw, first_y + line_h * index, line, fnt, highlights)
    base.alpha_composite(overlay)
    return base.convert("RGB")


def make_contact_sheet(paths: list[Path]) -> None:
    cols, rows = 3, 4
    thumb_w, thumb_h, label_h = 240, 426, 34
    sheet = Image.new("RGB", (thumb_w * cols, (thumb_h + label_h) * rows), (245, 245, 245))
    draw = ImageDraw.Draw(sheet)
    label_font = ImageFont.load_default()
    for index, path in enumerate(paths):
        thumb = cover(Image.open(path).convert("RGB")).resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (index % cols) * thumb_w
        y = (index // cols) * (thumb_h + label_h)
        sheet.paste(thumb, (x, y))
        draw.text((x + 8, y + thumb_h + 8), path.stem[:29], fill=(0, 0, 0), font=label_font)
    sheet.save(CONTACT, quality=92)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    text_lines: list[str] = []
    manifest = []
    for index, cut in enumerate(CUTS, start=1):
        source = BASE / cut["src"]
        output = OUT / cut["out"]
        add_telop(Image.open(source), cut["lines"], cut["highlights"], cut["position"]).save(output, quality=95)
        outputs.append(output)
        text_lines.append(f"{index:02d}. {' / '.join(''.join(line) for line in cut['lines'])}")
        manifest.append({
            "index": index,
            "source": str(source),
            "output": str(output),
            "telop": cut["lines"],
            "highlights": sorted(cut["highlights"]),
            "position": cut["position"],
            "font": str(FONT_PATH),
        })
    make_contact_sheet(outputs)
    TEXTS.write_text("\n".join(text_lines) + "\n", encoding="utf-8-sig")
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"created {len(outputs)} telop frames")
    print(OUT)


if __name__ == "__main__":
    main()
