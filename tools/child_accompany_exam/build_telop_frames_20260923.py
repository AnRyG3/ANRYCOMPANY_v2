from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
BASE = ROOT / "reel_assets" / "child_accompany_exam_20260923_images"
OUT = ROOT / "reel_assets" / "child_accompany_exam_20260923_telop_frames"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (16, 36, 55, 255)
BLUE = (0, 104, 150, 255)
PANEL = (255, 255, 255, 179)  # 70% opacity
SHADOW = (0, 0, 0, 38)

# One frame, one message. All boxes are horizontally centered. Center is the
# default; upper-center is only used where a center box would overlap faces.
FRAMES = [
    {
        "src": "01_home_concern.png",
        "out": "telop_01_hook.png",
        "lines": [["自分の検査"], ["子どもを", "連れて行っていい？"]],
        "highlights": {"子どもを"},
        "position": "top",
    },
    {
        "src": "02_previsit_call.png",
        "out": "telop_02_consult_reservation.png",
        "lines": [["預け先がない時は"], ["予約先", "に相談して大丈夫"]],
        "highlights": {"予約先", "大丈夫"},
        "position": "top",
    },
    {
        "src": "03_clinic_entrance.png",
        "out": "telop_03_facility_difference.png",
        "lines": [["対応は"], ["施設", "や", "検査", "で異なります"]],
        "highlights": {"施設", "検査"},
        "position": "center",
    },
    {
        "src": "04_waiting_together.png",
        "out": "telop_04_wait_together.png",
        "lines": [["一緒に", "待てる"], ["場合もあります"]],
        "highlights": {"待てる"},
        "position": "top",
    },
    {
        "src": "05_exam_room_boundary.png",
        "out": "telop_05_separate_for_exam.png",
        "lines": [["検査中は"], ["離れる", "場合もあります"]],
        "highlights": {"離れる"},
        "position": "top",
    },
    {
        "src": "06_call_early_at_home.png",
        "out": "telop_06_tell_reservation.png",
        "lines": [["予約時に"], ["見てくれる人", "がいなくて", "と伝えて"]],
        "highlights": {"見てくれる人"},
        "position": "top",
    },
    {
        "src": "07_two_checks_note.png",
        "out": "telop_07_two_checks.png",
        "lines": [["確認するのは"], ["同伴", "できる？", "・", "待つ場所", "は？"]],
        "highlights": {"同伴", "待つ場所"},
        "position": "center",
    },
    {
        "src": "08_schedule_consultation.png",
        "out": "telop_08_schedule_consultation.png",
        "lines": [["難しい時は"], ["日程変更", "も相談を"]],
        "highlights": {"日程変更"},
        "position": "top",
    },
    {
        "src": "09_family_share.png",
        "out": "telop_09_save_and_share.png",
        "lines": [["予約前に見返せるよう"], ["保存", "して家族LINEへ共有"]],
        "highlights": {"保存", "家族LINE"},
        "position": "top",
    },
    {
        "src": "10_end_card_background.png",
        "out": "telop_10_follow_cta.png",
        "lines": [["役に立ったら"], ["フォロー", "も"]],
        "highlights": {"フォロー"},
        "position": "top",
    },
]


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size)


def text_width(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=face)
    return box[2] - box[0]


def row_width(draw: ImageDraw.ImageDraw, row: list[str], face: ImageFont.FreeTypeFont) -> int:
    gap = round(face.size * 0.08)
    return sum(text_width(draw, part, face) for part in row) + gap * (len(row) - 1)


def fit_font(draw: ImageDraw.ImageDraw, rows: list[list[str]]) -> ImageFont.FreeTypeFont:
    for size in range(66, 39, -2):
        candidate = font(size)
        if max(row_width(draw, row, candidate) for row in rows) <= 800:
            return candidate
    return font(38)


def position_y(position: str, box_height: int) -> int:
    if position == "top":
        return 180
    if position == "bottom":
        return H - 260 - box_height
    return (H - box_height) // 2


def render(source: Image.Image, frame: dict) -> Image.Image:
    base = source.convert("RGB").resize((W, H), Image.Resampling.LANCZOS).convert("RGBA")
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    rows = frame["lines"]
    face = fit_font(draw, rows)
    line_height = round(face.size * 1.16)
    pad_x, pad_y = 56, 34
    box_width = min(920, max(row_width(draw, row, face) for row in rows) + pad_x * 2)
    box_height = line_height * len(rows) + pad_y * 2
    x0 = (W - box_width) // 2
    y0 = position_y(frame["position"], box_height)
    x1, y1 = x0 + box_width, y0 + box_height

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((x0 + 6, y0 + 8, x1 + 6, y1 + 8), radius=30, fill=SHADOW)
    layer.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(7)))
    draw.rounded_rectangle((x0, y0, x1, y1), radius=30, fill=PANEL)

    gap = round(face.size * 0.08)
    first_y = y0 + pad_y + round(face.size * 0.06)
    for index, row in enumerate(rows):
        x = (W - row_width(draw, row, face)) // 2
        y = first_y + index * line_height
        for part in row:
            color = BLUE if part in frame["highlights"] else NAVY
            draw.text((x, y), part, font=face, fill=color)
            x += text_width(draw, part, face) + gap

    base.alpha_composite(layer)
    return base.convert("RGB")


def make_contact_sheet(paths: list[Path], destination: Path) -> None:
    columns, thumb_w, thumb_h, label_h = 4, 216, 384, 36
    rows = math.ceil(len(paths) / columns)
    sheet = Image.new("RGB", (columns * thumb_w, rows * (thumb_h + label_h)), (246, 248, 250))
    draw = ImageDraw.Draw(sheet)
    label_face = font(20)
    for index, path in enumerate(paths):
        image = Image.open(path).convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (index % columns) * thumb_w
        y = (index // columns) * (thumb_h + label_h)
        sheet.paste(image, (x, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill=(255, 255, 255))
        draw.text((x + 8, y + thumb_h + 7), f"{index + 1:02d}", font=label_face, fill=NAVY)
    sheet.save(destination, quality=95)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    outputs, manifest, text_lines = [], [], []
    for index, frame in enumerate(FRAMES, start=1):
        source = BASE / frame["src"]
        output = OUT / frame["out"]
        if not source.exists():
            raise FileNotFoundError(source)
        render(Image.open(source), frame).save(output, quality=95)
        outputs.append(output)
        text_lines.append(f"{index:02d}. {' / '.join(''.join(row) for row in frame['lines'])}")
        manifest.append({
            "index": index,
            "source": str(source.relative_to(ROOT)),
            "output": str(output.relative_to(ROOT)),
            "telop": frame["lines"],
            "highlights": sorted(frame["highlights"]),
            "position": frame["position"],
            "font": str(FONT_PATH),
            "panel_opacity": "70%",
        })

    make_contact_sheet(outputs, OUT / "contact_sheet_telop.png")
    (OUT / "telop_texts.txt").write_text("\n".join(text_lines) + "\n", encoding="utf-8-sig")
    (OUT / "telop_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(f"created {len(outputs)} telop frames")


if __name__ == "__main__":
    main()
