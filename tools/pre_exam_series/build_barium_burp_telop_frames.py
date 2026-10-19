from __future__ import annotations

import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
UNIT = ROOT / "reel_assets" / "pre_exam_series" / "25_barium_burp_during_exam_v1_samples"
IMAGES = UNIT / "images"
OUTPUT = UNIT / "telop_frames"
MANIFEST = UNIT / "production_manifest.md"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

WIDTH, HEIGHT = 1080, 1920
CENTER_X = WIDTH // 2
PANELS = {
    "center": (80, 854, 1000, 1066),
    "top": (80, 300, 1000, 512),
}
FONT_SIZE = 60
NAVY = (12, 34, 64, 255)

FRAMES = [
    ("01_patient_burp.png", "ゲップが出たら伝えてください", "top"),
    ("02_patient_mild_surprise.png", "出てしまっても慌てずに", "top"),
    ("03_effervescent_cup.png", "発泡剤で胃を膨らませる", "center"),
    ("04_monitor.png", "画像に影響することもあります", "center"),
    ("05_patient_calm.png", "出てしまうこともあります", "top"),
    ("06_rt_fluoroscopy.png", "透視で胃の空気の減りを確認", "top"),
    ("07_exam_room.png", "対応は状況や施設で違います", "center"),
    ("08_effervescent_example.png", "発泡剤の追加もあります", "center"),
    ("09_tell_technologist_v2.png", "「ゲップが出ました」", "top"),
    ("10_save_before_exam.png", "検査前に見返せるよう保存", "center"),
]


def check_sources() -> None:
    if not MANIFEST.is_file() or not FONT_PATH.is_file():
        raise FileNotFoundError("production manifest or required font missing")
    expected = [str(IMAGES / name) for name, _, _ in FRAMES]
    actual = re.findall(
        r"\| \d{2} \| `([A-Za-z]:\\[^`]+\.png)` \|",
        MANIFEST.read_text(encoding="utf-8"),
    )
    if actual != expected:
        raise RuntimeError("manifest images differ in count, path, or cut order")
    if any(not Path(path).is_file() for path in expected):
        raise FileNotFoundError("an approved source image is missing")
    for name, text, position in FRAMES:
        if "\n" in text or len(text) > 20:
            raise ValueError(f"invalid telop length or line count: {name}")
        if position not in PANELS:
            raise ValueError(f"invalid fixed position: {name}")


def cover(image: Image.Image) -> Image.Image:
    image = image.convert("RGB")
    factor = max(WIDTH / image.width, HEIGHT / image.height)
    image = image.resize(
        (round(image.width * factor), round(image.height * factor)),
        Image.Resampling.LANCZOS,
    )
    x = (image.width - WIDTH) // 2
    y = (image.height - HEIGHT) // 2
    return image.crop((x, y, x + WIDTH, y + HEIGHT)).convert("RGBA")


def render(source: Path, label: str, position: str, destination: Path) -> dict:
    with Image.open(source) as original:
        canvas = cover(original)
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    panel = PANELS[position]
    center_y = (panel[1] + panel[3]) // 2
    draw.rounded_rectangle(panel, radius=32, fill=(255, 255, 255, 179))
    font = ImageFont.truetype(str(FONT_PATH), FONT_SIZE)
    bbox = draw.textbbox((0, 0), label, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    if text_width > panel[2] - panel[0] - 72:
        raise ValueError(f"text too wide at fixed font size: {source.name}")
    x = CENTER_X - text_width / 2 - bbox[0]
    y = center_y - text_height / 2 - bbox[1]
    draw.text((x, y), label, font=font, fill=NAVY)
    canvas = Image.alpha_composite(canvas, overlay).convert("RGB")
    canvas.save(destination, format="PNG")
    return {
        "cut": source.name[:2],
        "source": str(source),
        "output": str(destination),
        "text": label,
        "characters": len(label),
        "lines": 1,
        "position": position,
        "center_x": CENTER_X,
        "center_y": center_y,
        "font_size": FONT_SIZE,
        "text_width": text_width,
    }


def main() -> None:
    check_sources()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    results = []
    for name, label, position in FRAMES:
        source = IMAGES / name
        destination = OUTPUT / f"telop_{name.replace('_v2', '')}"
        results.append(render(source, label, position, destination))
    (OUTPUT / "telop_qa.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
