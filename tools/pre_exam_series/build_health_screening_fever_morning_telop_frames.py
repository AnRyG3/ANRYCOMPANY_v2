from pathlib import Path
import hashlib
import json
import math
import re

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
UNIT = ROOT / "reel_assets" / "pre_exam_series" / "health_screening_fever_morning_20261019_samples"
OUT = UNIT / "telop"
MANIFEST = UNIT / "production_manifest.md"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"
CONTACT = OUT / "contact_sheet_telop.png"
TEXTS = OUT / "telop_texts.txt"
TELOP_MANIFEST = OUT / "telop_manifest.json"

W, H = 1080, 1920
NAVY = (16, 36, 55, 255)
BLUE = (0, 104, 150, 255)
PANEL = (255, 255, 255, 179)
SHADOW = (0, 0, 0, 38)
MAX_CHARS = 20


# Every panel is centered on the same X and Y coordinates. Cut 09 alone uses two
# lines because it contains the approved phone phrase. All other cuts use one line.
FRAMES = [
    {
        "src": "sample_01_hook_call_before_visit_no_text.png",
        "out": "telop_01_call_before_visit.png",
        "lines": [["熱っぽい朝は来院前に", ("連絡", "blue")]],
        "position": "center",
    },
    {
        "src": "scene_02_hesitate_before_call_no_text.png",
        "out": "telop_02_hesitate_before_call.png",
        "lines": [["迷ったときこそ予約先へ", ("連絡", "blue")]],
        "position": "center",
    },
    {
        "src": "scene_03_screening_not_diagnosis_no_text.png",
        "out": "telop_03_screening_not_diagnosis.png",
        "lines": [["健診は症状の", ("診断", "blue"), "ではありません"]],
        "position": "center",
    },
    {
        "src": "scene_04_schedule_change_call_no_text.png",
        "out": "telop_04_schedule_change.png",
        "lines": [[("日程変更", "blue"), "を案内する施設も"]],
        "position": "center",
    },
    {
        "src": "scene_05_facility_rules_check_no_text.png",
        "out": "telop_05_facility_rules.png",
        "lines": [["受診基準は", ("施設ごと", "blue"), "に違います"]],
        "position": "center",
    },
    {
        "src": "sample_06_call_to_confirm_no_text.png",
        "out": "telop_06_call_to_confirm.png",
        "lines": [["受診できるか", ("日程変更", "blue"), "を確認"]],
        "position": "center",
    },
    {
        "src": "scene_07_describe_symptoms_no_text.png",
        "out": "telop_07_describe_symptoms.png",
        "lines": [["熱や", ("症状", "blue"), "をそのまま伝える"]],
        "position": "center",
    },
    {
        "src": "scene_08_speak_without_hesitation_no_text.png",
        "out": "telop_08_speak_without_hesitation.png",
        "lines": [["体調は", ("遠慮なく", "blue"), "伝えてください"]],
        "position": "center",
    },
    {
        "src": "scene_09_phone_phrase_space_no_text.png",
        "out": "telop_09_phone_phrase.png",
        "lines": [["熱っぽいです"], ["受診か", ("日程変更", "blue"), "できますか"]],
        "position": "center",
    },
    {
        "src": "scene_10_save_phone_note_no_text.png",
        "out": "telop_10_save_phone_note.png",
        "lines": [["当日の朝に備えて", ("保存", "blue")]],
        "position": "center",
    },
]


def load_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size)


def cover(image: Image.Image, size: tuple[int, int] = (W, H)) -> Image.Image:
    image = image.convert("RGB")
    scale = max(size[0] / image.width, size[1] / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = (resized.width - size[0]) // 2
    top = (resized.height - size[1]) // 2
    return resized.crop((left, top, left + size[0], top + size[1]))


def segment_text(segment) -> str:
    return segment[0] if isinstance(segment, tuple) else segment


def plain_lines(lines: list[list]) -> list[str]:
    return ["".join(segment_text(segment) for segment in line) for line in lines]


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def line_width(draw: ImageDraw.ImageDraw, line: list, font: ImageFont.FreeTypeFont) -> int:
    return sum(text_width(draw, segment_text(segment), font) for segment in line)


def fit_font(draw: ImageDraw.ImageDraw, lines: list[list]) -> ImageFont.FreeTypeFont:
    for size in range(66, 47, -2):
        candidate = load_font(size)
        if max(line_width(draw, line, candidate) for line in lines) <= 820:
            return candidate
    raise RuntimeError("Telop is too long at the minimum approved font size")


def telop_y(position: str, box_height: int) -> int:
    if position == "top":
        return 180
    if position == "center":
        return (H - box_height) // 2
    if position == "bottom":
        return H - 260 - box_height
    raise ValueError(f"Unsupported telop position: {position}")


def validate_frames() -> None:
    if len(FRAMES) != 10:
        raise RuntimeError("Expected exactly 10 approved cuts")
    for index, frame in enumerate(FRAMES, start=1):
        lines = plain_lines(frame["lines"])
        char_count = sum(len(line) for line in lines)
        if len(lines) > 2:
            raise RuntimeError(f"Cut {index:02d} exceeds two lines")
        if index != 9 and len(lines) != 1:
            raise RuntimeError(f"Cut {index:02d} must use one line")
        if char_count > MAX_CHARS:
            raise RuntimeError(f"Cut {index:02d} exceeds {MAX_CHARS} characters: {char_count}")
        if frame["position"] != "center":
            raise RuntimeError(f"Cut {index:02d} must use the fixed center position")
        for line in frame["lines"]:
            for segment in line:
                if isinstance(segment, tuple) and segment[1] != "blue":
                    raise RuntimeError(f"Cut {index:02d} contains an unsupported emphasis color")


def draw_telop(source: Image.Image, frame: dict) -> Image.Image:
    base = cover(source).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    lines = frame["lines"]
    font = fit_font(draw, lines)
    line_height = round(font.size * 1.18)
    pad_x, pad_y = 56, 34
    box_width = min(932, max(line_width(draw, line, font) for line in lines) + pad_x * 2)
    box_height = line_height * len(lines) + pad_y * 2
    x0 = (W - box_width) // 2
    y0 = telop_y(frame["position"], box_height)
    x1, y1 = x0 + box_width, y0 + box_height

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((x0 + 6, y0 + 8, x1 + 6, y1 + 8), radius=30, fill=SHADOW)
    overlay.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(7)))
    draw.rounded_rectangle((x0, y0, x1, y1), radius=30, fill=PANEL)

    first_y = y0 + pad_y + round(font.size * 0.04)
    for row, line in enumerate(lines):
        width = line_width(draw, line, font)
        x = (W - width) // 2
        y = first_y + row * line_height
        for segment in line:
            if isinstance(segment, tuple):
                text, color_name = segment
                color = BLUE if color_name == "blue" else NAVY
            else:
                text, color = segment, NAVY
            draw.text((x, y), text, font=font, fill=color)
            x += text_width(draw, text, font)

    base.alpha_composite(overlay)
    return base.convert("RGB")


def approved_paths_from_manifest() -> list[Path]:
    pattern = re.compile(r"^\|\s*(\d{2})\s*\|\s*`([^`]+)`\s*\|")
    approved = []
    for line in MANIFEST.read_text(encoding="utf-8-sig").splitlines():
        match = pattern.match(line)
        if match:
            approved.append((int(match.group(1)), Path(match.group(2))))
    approved.sort(key=lambda item: item[0])
    return [path.resolve() for _, path in approved]


def verify_source_lock() -> list[Path]:
    expected = [(UNIT / frame["src"]).resolve() for frame in FRAMES]
    approved = approved_paths_from_manifest()
    if approved != expected:
        raise RuntimeError("production_manifest.md count, order, or path differs from FRAMES")
    missing = [path for path in expected if not path.exists()]
    if missing:
        raise FileNotFoundError(missing)
    if len(set(expected)) != len(expected):
        raise RuntimeError("An approved source image is duplicated in the cut order")
    return expected


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source_file:
        for chunk in iter(lambda: source_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def make_contact_sheet(paths: list[Path]) -> None:
    columns = 5
    thumb_w, thumb_h, label_h = 216, 384, 36
    rows = math.ceil(len(paths) / columns)
    sheet = Image.new("RGB", (columns * thumb_w, rows * (thumb_h + label_h)), (246, 248, 250))
    draw = ImageDraw.Draw(sheet)
    label_font = load_font(20)
    for index, path in enumerate(paths):
        x = (index % columns) * thumb_w
        y = (index // columns) * (thumb_h + label_h)
        sheet.paste(cover(Image.open(path), (thumb_w, thumb_h)), (x, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill=(255, 255, 255))
        draw.text((x + 8, y + thumb_h + 7), f"{index + 1:02d}", font=label_font, fill=NAVY)
    sheet.save(CONTACT)


def main() -> None:
    if not FONT_PATH.exists():
        raise FileNotFoundError(f"Required telop font not found: {FONT_PATH}")
    validate_frames()
    sources = verify_source_lock()
    source_hashes = {source: sha256(source) for source in sources}
    OUT.mkdir(parents=True, exist_ok=True)
    outputs = []
    telop_manifest = []
    text_lines = []
    for index, (frame, source) in enumerate(zip(FRAMES, sources), start=1):
        output = OUT / frame["out"]
        rendered = draw_telop(Image.open(source), frame)
        rendered.save(output, quality=95)
        outputs.append(output)
        display_lines = plain_lines(frame["lines"])
        highlights = [segment[0] for line in frame["lines"] for segment in line if isinstance(segment, tuple)]
        char_count = sum(len(line) for line in display_lines)
        text_lines.append(f"{index:02d}. {' / '.join(display_lines)} ({char_count}文字・{len(display_lines)}行・中央)")
        telop_manifest.append(
            {
                "cut": index,
                "source": str(source),
                "source_sha256": source_hashes[source],
                "output": str(output.resolve()),
                "telop": display_lines,
                "char_count": char_count,
                "line_count": len(display_lines),
                "highlights": highlights,
                "position": frame["position"],
                "x_alignment": "center",
                "canvas": f"{W}x{H}",
                "font": str(FONT_PATH),
                "panel_opacity": "70%",
            }
        )

    after_hashes = {source: sha256(source) for source in sources}
    if after_hashes != source_hashes:
        raise RuntimeError("An approved source image changed during telop generation")

    make_contact_sheet(outputs)
    TEXTS.write_text("\n".join(text_lines) + "\n", encoding="utf-8-sig")
    TELOP_MANIFEST.write_text(json.dumps(telop_manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(f"source lock verified: {len(sources)} images")
    print(f"created {len(outputs)} telop frames")
    print("approved source images unchanged: SHA-256 verified")
    print(CONTACT)


if __name__ == "__main__":
    main()
