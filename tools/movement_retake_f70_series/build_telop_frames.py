from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "sample_frames" / "movement_retake_f70_20260725"
OUT_DIR = ASSET_DIR / "telop_frames"
CONTACT_SHEET = ASSET_DIR / "contact_sheet_telop_frames.png"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (8, 30, 54, 255)
WHITE = (255, 255, 255, 238)
SHADOW = (16, 26, 38, 70)


FRAMES = [
    {
        "src": "frame_01_patient_on_table_sample.png",
        "out": "frame_01_telop.png",
        "lines": ["動いてしまったら", "撮り直し？"],
    },
    {
        "src": "frame_02_patient_after_exam_sample.png",
        "out": "frame_02_telop.png",
        "lines": ["迷惑だったかな…", "と感じることも"],
    },
    {
        "src": "frame_03_rt_patient_talk_sample.png",
        "out": "frame_03_telop.png",
        "lines": ["その気持ち", "自然です"],
    },
    {
        "src": "frame_04_flat_exam_room_sample.png",
        "out": "frame_04_telop.png",
        "lines": ["同じ姿勢は", "意外と難しい"],
    },
    {
        "src": "frame_05_rt_control_sample.png",
        "out": "frame_05_telop.png",
        "lines": ["現場では", "想定しています"],
        "y": 560,
    },
    {
        "src": "frame_06_rt_patient_explain_sample.png",
        "out": "frame_06_telop.png",
        "lines": ["できない場面も", "確認しながら"],
    },
    {
        "src": "frame_07_monitor_review_sample.png",
        "out": "frame_07_telop.png",
        "lines": ["必要な時は", "医師にも確認"],
    },
    {
        "src": "frame_08_patient_bracing_needs_flat_review_sample.png",
        "out": "frame_08_telop.png",
        "lines": ["また動いたら…", "不安になりますよね"],
    },
    {
        "src": "frame_09_together_consult_sample.png",
        "out": "frame_09_telop.png",
        "lines": ["遠慮せず", "伝えてください"],
    },
    {
        "src": "frame_10_save_cta_bg_sample.png",
        "out": "frame_10_telop.png",
        "lines": ["不安な時のために", "保存してください"],
    },
    {
        "src": "frame_11_follow_cta_bg_sample.png",
        "out": "frame_11_telop.png",
        "lines": ["検査のこと", "一緒に考えます"],
    },
]


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size=size)


def cover_resize(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")
    scale = max(W / img.width, H / img.height)
    resized = img.resize(
        (round(img.width * scale), round(img.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = (resized.width - W) // 2
    top = (resized.height - H) // 2
    return resized.crop((left, top, left + W, top + H))


def measure(draw: ImageDraw.ImageDraw, lines: list[str], fnt: ImageFont.FreeTypeFont, gap: int):
    boxes = [draw.textbbox((0, 0), line, font=fnt) for line in lines]
    widths = [box[2] - box[0] for box in boxes]
    heights = [box[3] - box[1] for box in boxes]
    return max(widths), sum(heights) + gap * (len(lines) - 1), boxes


def fit_font(draw: ImageDraw.ImageDraw, lines: list[str], max_w: int, max_h: int):
    for size in range(74, 42, -2):
        fnt = font(size)
        gap = max(10, int(size * 0.22))
        text_w, text_h, _ = measure(draw, lines, fnt, gap)
        if text_w <= max_w and text_h <= max_h:
            return fnt, gap
    return font(42), 10


def draw_telop(img: Image.Image, lines: list[str], y: int | None) -> Image.Image:
    base = cover_resize(img).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    shadow_draw = ImageDraw.Draw(shadow_layer)

    max_text_w = int(W * 0.78)
    max_text_h = 170
    fnt, gap = fit_font(draw, lines, max_text_w, max_text_h)
    text_w, text_h, boxes = measure(draw, lines, fnt, gap)

    pad_x = 56
    pad_y = 32
    box_w = min(W - 150, text_w + pad_x * 2)
    box_h = text_h + pad_y * 2
    x0 = (W - box_w) // 2
    y0 = (H - box_h) // 2 if y is None else y
    x1 = x0 + box_w
    y1 = y0 + box_h

    shadow_draw.rounded_rectangle((x0 + 8, y0 + 10, x1 + 8, y1 + 10), radius=34, fill=SHADOW)
    overlay.alpha_composite(shadow_layer.filter(ImageFilter.GaussianBlur(10)))
    draw.rounded_rectangle((x0, y0, x1, y1), radius=34, fill=WHITE)

    yy = y0 + pad_y
    for line, box in zip(lines, boxes):
        line_w = box[2] - box[0]
        line_h = box[3] - box[1]
        xx = (W - line_w) // 2
        draw.text((xx, yy - box[1]), line, font=fnt, fill=NAVY)
        yy += line_h + gap

    return Image.alpha_composite(base, overlay).convert("RGB")


def make_contact_sheet(paths: list[Path]) -> None:
    cols = 4
    thumb_w, thumb_h = 270, 480
    label_h = 34
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (245, 247, 250))
    label_font = ImageFont.load_default()

    for idx, path in enumerate(paths):
        img = Image.open(path).convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (idx % cols) * thumb_w
        y = (idx // cols) * (thumb_h + label_h)
        sheet.paste(img, (x, y))
        ImageDraw.Draw(sheet).text((x + 8, y + thumb_h + 9), path.name, fill=(0, 0, 0), font=label_font)

    sheet.save(CONTACT_SHEET, quality=94)


def main() -> None:
    if not FONT_PATH.exists():
        raise FileNotFoundError(FONT_PATH)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    manifest_frames = []

    for frame in FRAMES:
        src = ASSET_DIR / frame["src"]
        out = OUT_DIR / frame["out"]
        if not src.exists():
            raise FileNotFoundError(src)
        draw_telop(Image.open(src), frame["lines"], frame.get("y")).save(out, quality=95)
        outputs.append(out)
        manifest_frames.append(
            {
                "source": str(src),
                "output": str(out),
                "telop": frame["lines"],
                "y": frame.get("y", "center"),
            }
        )

    make_contact_sheet(outputs)
    manifest = {
        "title": "検査中に動いてしまったら",
        "size": {"width": W, "height": H},
        "font": str(FONT_PATH),
        "style": "white rounded rectangle, dark navy M PLUS Rounded 1c Bold, short telop",
        "frames": manifest_frames,
        "contact_sheet": str(CONTACT_SHEET),
    }
    (OUT_DIR / "telop_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8-sig",
    )
    print(OUT_DIR)
    print(CONTACT_SHEET)


if __name__ == "__main__":
    main()
