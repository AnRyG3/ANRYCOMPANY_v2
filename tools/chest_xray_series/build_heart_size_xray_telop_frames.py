from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "chest_xray_series" / "heart_size_xray_sample_frames_v1"
OUT_DIR = ASSET_DIR / "telop_frames"
CONTACT_SHEET = ASSET_DIR / "contact_sheet_telop_frames.png"

W, H = 1080, 1920
TEXT_DARK = (2, 18, 34, 255)
PANEL = (255, 255, 255, 236)
PANEL_EDGE = (255, 255, 255, 255)
SHADOW = (16, 26, 38, 68)
ACCENT = (54, 137, 154, 255)
ACCENT_YELLOW = (255, 213, 86, 255)

FONT_PATH = r"F:\ANRYCAMPANY\reel_assets\fonts\M_PLUS_Rounded_1c\MPLUSRounded1c-Bold.ttf"

FRAMES = [
    {
        "src": "frame_01_patient_after_xray_room_v2.png",
        "out": "frame_01_telop.png",
        "lines": ["胸のレントゲンで", "心臓も見ています"],
        "kind": "rounded",
        "accent": "yellow",
    },
    {
        "src": "frame_02_patient_thinking_sample_v3.png",
        "out": "frame_02_telop.png",
        "lines": ["肺だけじゃないの？"],
        "kind": "rounded",
    },
    {
        "src": "frame_03_rt_pointing_xray_monitor.png",
        "out": "frame_03_telop.png",
        "lines": ["心臓の大きさも", "チェックしています"],
        "kind": "rounded",
        "accent": "green",
    },
    {
        "src": "frame_04_monitor_lungs_heart_rt_side.png",
        "out": "frame_04_telop.png",
        "lines": ["肺と心臓が", "同じ1枚に写ります"],
        "kind": "rounded",
    },
    {
        "src": "frame_05_rt_monitor_sample_v5.png",
        "out": "frame_05_telop.png",
        "lines": ["胸の横幅と比べて", "大きさを見ます"],
        "kind": "rounded",
        "accent": "green",
    },
    {
        "src": "frame_06_rt_reassuring_patient.png",
        "out": "frame_06_telop.png",
        "lines": ["「大きめ」だけで", "心配しすぎなくて大丈夫"],
        "kind": "rounded",
        "accent": "yellow",
        "box": (64, 154, 1016, 448),
    },
    {
        "src": "frame_07_patient_positioning_xray_room.png",
        "out": "frame_07_telop.png",
        "lines": ["息や姿勢で", "見えかたは変わります"],
        "kind": "rounded",
    },
    {
        "src": "frame_08_doctor_patient_consultation.png",
        "out": "frame_08_telop.png",
        "lines": ["気になる時は", "医師が詳しく確認します"],
        "kind": "rounded",
    },
    {
        "src": "frame_09_overhead_xray_monitor_rt.png",
        "out": "frame_09_telop.png",
        "lines": ["レントゲン1枚にも", "情報がたくさん"],
        "kind": "rounded",
        "accent": "green",
    },
    {
        "src": "frame_10_rt_walking_corridor.png",
        "out": "frame_10_telop.png",
        "lines": ["次回も検査の気になるを", "分かりやすく"],
        "kind": "rounded",
    },
    {
        "src": "frame_11_smartphone_save_video.png",
        "out": "frame_11_telop.png",
        "lines": ["役に立ったら", "保存して見返してください"],
        "kind": "rounded",
        "accent": "yellow",
    },
    {
        "src": "frame_12_rt_closing_bow.png",
        "out": "frame_12_telop.png",
        "lines": ["診療放射線技師の発信", "フォローで応援してください"],
        "kind": "rounded",
        "accent": "green",
    },
]


def choose_font(size: int, kind: str):
    if not Path(FONT_PATH).exists():
        raise FileNotFoundError(FONT_PATH)
    return ImageFont.truetype(FONT_PATH, size=size)


def cover_resize(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")
    scale = max(W / img.width, H / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - W) // 2
    top = (nh - H) // 2
    return resized.crop((left, top, left + W, top + H))


def measure_lines(draw: ImageDraw.ImageDraw, lines: list[str], font, spacing: int):
    boxes = [draw.textbbox((0, 0), line, font=font) for line in lines]
    widths = [box[2] - box[0] for box in boxes]
    heights = [box[3] - box[1] for box in boxes]
    return max(widths), sum(heights) + spacing * (len(lines) - 1), heights


def fit_font(draw: ImageDraw.ImageDraw, lines: list[str], kind: str, max_w: int, max_h: int):
    for size in range(74, 40, -2):
        spacing = max(12, int(size * 0.22))
        font = choose_font(size, kind)
        width, height, _ = measure_lines(draw, lines, font, spacing)
        if width <= max_w and height <= max_h:
            return font, spacing
    return choose_font(40, kind), 10


def draw_readability_wash(img: Image.Image) -> None:
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, W, 560), fill=(255, 255, 255, 20))
    img.alpha_composite(overlay)


def draw_telop(img: Image.Image, frame: dict) -> None:
    x0, y0, x1, y1 = frame.get("box", (64, 1160, 1016, 1454))
    lines = frame["lines"]
    kind = frame["kind"]

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x0 + 10, y0 + 12, x1 + 10, y1 + 12), radius=34, fill=SHADOW)
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(12)))

    draw = ImageDraw.Draw(img, "RGBA")
    draw.rounded_rectangle((x0, y0, x1, y1), radius=34, fill=PANEL)
    draw.rounded_rectangle((x0 + 8, y0 + 8, x1 - 8, y1 - 8), radius=28, outline=PANEL_EDGE, width=5)

    accent = frame.get("accent")
    if accent:
        color = ACCENT_YELLOW if accent == "yellow" else ACCENT
        draw.rounded_rectangle((x0 + 64, y1 - 34, x1 - 64, y1 - 24), radius=5, fill=color)

    font, spacing = fit_font(draw, lines, kind, (x1 - x0) - 92, (y1 - y0) - 86)
    _, total_h, heights = measure_lines(draw, lines, font, spacing)
    yy = y0 + ((y1 - y0) - total_h) // 2 - 6
    for line, line_h in zip(lines, heights):
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        draw.text(((x0 + x1 - line_w) // 2, yy), line, font=font, fill=TEXT_DARK)
        yy += line_h + spacing


def make_contact_sheet(paths: list[Path]) -> None:
    cols = 4
    thumb_w, thumb_h = 216, 384
    label_h = 34
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (245, 247, 250))
    label_font = ImageFont.load_default()
    for idx, path in enumerate(paths):
        img = Image.open(path).convert("RGB")
        img.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), "white")
        tile.paste(img, ((thumb_w - img.width) // 2, 0))
        ImageDraw.Draw(tile).text((8, thumb_h + 9), path.name[:30], fill=(0, 0, 0), font=label_font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
    sheet.save(CONTACT_SHEET, quality=94)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    manifest_frames = []
    for frame in FRAMES:
        src = ASSET_DIR / frame["src"]
        out = OUT_DIR / frame["out"]
        img = cover_resize(Image.open(src)).convert("RGBA")
        draw_readability_wash(img)
        draw_telop(img, frame)
        img.convert("RGB").save(out, quality=95)
        outputs.append(out)
        manifest_frames.append(
            {
                "source": str(src),
                "output": str(out),
                "telop": frame["lines"],
                "font_kind": frame["kind"],
            }
        )

    make_contact_sheet(outputs)
    manifest = {
        "title": "胸のレントゲンで心臓の大きさも見ている話",
        "size": {"width": W, "height": H},
        "style": "white rounded rectangle backing, dark navy text, Instagram Reels safe area",
        "asset_dir": str(ASSET_DIR),
        "output_dir": str(OUT_DIR),
        "contact_sheet": str(CONTACT_SHEET),
        "frames": manifest_frames,
    }
    (OUT_DIR / "telop_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8-sig",
    )
    print(OUT_DIR)
    print(CONTACT_SHEET)


if __name__ == "__main__":
    main()
