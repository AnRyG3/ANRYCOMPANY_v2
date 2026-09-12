from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "mammography_series" / "mammo_cycle_timing_v1"
SOURCE_DIR = ASSET_DIR / "frames_no_text"
OUT_DIR = ASSET_DIR / "telop_frames"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (12, 34, 58, 255)
BLUE = (0, 104, 150, 255)
PANEL = (255, 255, 255, 240)
PANEL_EDGE = (255, 255, 255, 255)
SHADOW = (0, 0, 0, 42)


FRAMES = [
    {
        "src": "frame_01_hook_calendar.png",
        "out": "telop_01_hook_calendar.png",
        "lines": [["生理前", "で胸が張る…"], ["マンモ", "の予約、変える？"]],
        "highlights": {"生理前", "マンモ"},
        "position": "bottom",
    },
    {
        "src": "frame_02_consult_by_phone.png",
        "out": "telop_02_consult_by_phone.png",
        "lines": [["つらければ"], ["予約先に", "相談", "を"]],
        "highlights": {"相談"},
        "position": "center",
    },
    {
        "src": "frame_03_appointment_hesitation.png",
        "out": "telop_03_appointment_hesitation.png",
        "lines": [["予約変更の電話"], ["気が引けますよね"]],
        "highlights": {"予約変更"},
        "position": "bottom",
    },
    {
        "src": "frame_04_mammography_equipment.png",
        "out": "telop_04_mammography_equipment.png",
        "lines": [["マンモ", "は乳房を"], ["圧迫", "して撮影します"]],
        "highlights": {"マンモ", "圧迫"},
        "position": "center",
    },
    {
        "src": "frame_05_compression_detail.png",
        "out": "telop_05_compression_detail.png",
        "lines": [["生理前は"], ["痛み", "を強く感じることも"]],
        "highlights": {"痛み"},
        "position": "center",
    },
    {
        "src": "frame_06_reassured_waiting.png",
        "out": "telop_06_reassured_waiting.png",
        "lines": [["生理前・生理中でも"], ["検査自体は", "受けられます"]],
        "highlights": {"検査自体"},
        "position": "center",
    },
    {
        "src": "frame_07_timing_calendar.png",
        "out": "telop_07_timing_calendar.png",
        "lines": [["目安は"], ["胸の張りが少ない", "時期"]],
        "highlights": {"目安", "時期"},
        "position": "center",
    },
    {
        "src": "frame_08_reschedule_note.png",
        "out": "telop_08_reschedule_note.png",
        "lines": [["自己判断で延期せず"], ["予約先に", "相談", "を"]],
        "highlights": {"相談"},
        "position": "center",
    },
    {
        "src": "frame_09_save_cta_background.png",
        "out": "telop_09_save_cta_background.png",
        "lines": [["予約日を決める前に"], ["保存", "しておこう"]],
        "highlights": {"保存"},
        "position": "center",
    },
    {
        "src": "frame_10_follow_cta_background.png",
        "out": "telop_10_follow_cta_background.png",
        "lines": [["次の検査前にも"], ["見返せるよう", "フォロー"]],
        "highlights": {"フォロー"},
        "position": "center",
    },
]


def font(size: int) -> ImageFont.FreeTypeFont:
    if not FONT_PATH.exists():
        raise FileNotFoundError(FONT_PATH)
    return ImageFont.truetype(str(FONT_PATH), size)


def text_width(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=fnt)
    return bbox[2] - bbox[0]


def line_width(draw: ImageDraw.ImageDraw, line: list[str], fnt: ImageFont.FreeTypeFont) -> int:
    gap = int(fnt.size * 0.08)
    return sum(text_width(draw, part, fnt) for part in line) + gap * (len(line) - 1)


def fit_font(draw: ImageDraw.ImageDraw, lines: list[list[str]]) -> tuple[ImageFont.FreeTypeFont, int]:
    for size in range(70, 41, -2):
        fnt = font(size)
        line_h = int(size * 1.2)
        if max(line_width(draw, line, fnt) for line in lines) <= 800:
            return fnt, line_h
    return font(42), 50


def box_y(position: str, box_h: int) -> int:
    if position == "top":
        return 176
    if position == "bottom":
        return 1270
    return (H - box_h) // 2


def color(part: str, highlights: set[str]) -> tuple[int, int, int, int]:
    return BLUE if part in highlights else NAVY


def draw_telop(source: Path, frame: dict) -> tuple[Image.Image, list[int]]:
    image = Image.open(source).convert("RGBA")
    if image.size != (W, H):
        image = image.resize((W, H), Image.Resampling.LANCZOS)

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    lines = frame["lines"]
    fnt, line_h = fit_font(draw, lines)
    pad_x, pad_y = 54, 32
    text_w = max(line_width(draw, line, fnt) for line in lines)
    box_w = min(936, text_w + pad_x * 2)
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
        x = (W - line_width(draw, line, fnt)) // 2
        y = first_y + row * line_h
        for part in line:
            draw.text((x, y), part, font=fnt, fill=color(part, frame["highlights"]))
            x += text_width(draw, part, fnt) + gap

    image.alpha_composite(overlay)
    return image.convert("RGB"), [x0, y0, x1, y1]


def make_contact_sheet(paths: list[Path], out_path: Path) -> None:
    cols, thumb_w, thumb_h, label_h = 4, 216, 384, 36
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (246, 248, 250))
    draw = ImageDraw.Draw(sheet)
    label_font = font(20)
    for i, path in enumerate(paths):
        thumb = Image.open(path).convert("RGB")
        thumb.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (thumb_w, thumb_h), "white")
        tile.paste(thumb, ((thumb_w - thumb.width) // 2, (thumb_h - thumb.height) // 2))
        x, y = (i % cols) * thumb_w, (i // cols) * (thumb_h + label_h)
        sheet.paste(tile, (x, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill="white")
        draw.text((x + 8, y + thumb_h + 7), f"{i + 1:02d}", font=label_font, fill=NAVY)
    sheet.save(out_path)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    manifest = []
    for index, frame in enumerate(FRAMES, start=1):
        source = SOURCE_DIR / frame["src"]
        if not source.exists():
            raise FileNotFoundError(source)
        output = OUT_DIR / frame["out"]
        image, box = draw_telop(source, frame)
        image.save(output, quality=95)
        outputs.append(output)
        manifest.append(
            {
                "index": index,
                "source": str(source.relative_to(ROOT)),
                "output": str(output.relative_to(ROOT)),
                "telop": ["".join(line) for line in frame["lines"]],
                "highlights": sorted(frame["highlights"]),
                "position": frame["position"],
                "box": box,
                "font": str(FONT_PATH.relative_to(ROOT)),
            }
        )

    contact_sheet = OUT_DIR / "contact_sheet_telop_frames.png"
    make_contact_sheet(outputs, contact_sheet)
    (OUT_DIR / "telop_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig"
    )
    print(f"created {len(outputs)} telop frames")
    print(contact_sheet)


if __name__ == "__main__":
    main()
