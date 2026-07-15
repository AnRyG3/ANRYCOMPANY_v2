from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(r"F:\ANRYCAMPANY")
SRC_DIR = ROOT / "reel_assets" / "cast_xray_with_cast_samples"
OUT_DIR = ROOT / "reel_assets" / "cast_xray_with_cast_telop_frames"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (12, 46, 78, 255)
WHITE = (255, 255, 255, 236)
SHADOW = (18, 28, 38, 70)


FRAMES = [
    {
        "src": "frame_01_patient_cast_waiting_sample.png",
        "out": "frame_01_telop.png",
        "lines": ["ギプスのまま", "撮れるの？"],
        "y": 210,
    },
    {
        "src": "frame_02_rt_guiding_patient_sample.png",
        "out": "frame_02_telop.png",
        "lines": ["そのままで", "撮影できます"],
        "y": 210,
    },
    {
        "src": "frame_03_cast_explanation_sample.png",
        "out": "frame_03_telop.png",
        "lines": ["骨の確認は", "しやすいです"],
        "y": 1280,
    },
    {
        "src": "frame_04_keep_cast_reassurance_sample.png",
        "out": "frame_04_telop.png",
        "lines": ["外さずに", "大丈夫です"],
        "y": 210,
    },
    {
        "src": "frame_05_monitor_check_sample.png",
        "out": "frame_05_telop.png",
        "lines": ["ギプス越しでも", "確認できます"],
        "y": 210,
    },
    {
        "src": "frame_06_rt_positioning_sample.png",
        "out": "frame_06_telop.png",
        "lines": ["体位が", "取りにくいことも"],
        "y": 210,
    },
    {
        "src": "frame_07_calm_interaction_sample.png",
        "out": "frame_07_telop.png",
        "lines": ["少し時間が", "かかることがあります"],
        "y": 210,
    },
    {
        "src": "frame_08_angle_adjustment_sample.png",
        "out": "frame_08_telop.png",
        "lines": ["向きや角度を", "調整します"],
        "y": 210,
    },
    {
        "src": "frame_09_patient_reassured_sample.png",
        "out": "frame_09_telop.png",
        "lines": ["ギプスのままで", "問題ありません"],
        "y": 210,
    },
    {
        "src": "frame_10_reassuring_end_sample.png",
        "out": "frame_10_telop.png",
        "lines": ["安心して", "受けてくださいね"],
        "y": 210,
    },
    {
        "src": "frame_11_save_cta_background.png",
        "out": "frame_11_telop.png",
        "lines": ["スマホに保存", "しておくと安心"],
        "y": 210,
    },
    {
        "src": "frame_12_follow_cta_bow_sample.png",
        "out": "frame_12_telop.png",
        "lines": ["診療放射線技師の発信", "フォローで応援お願いします"],
        "y": 210,
    },
]


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size=size)


def cover_resize(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")
    scale = max(W / img.width, H / img.height)
    resized = img.resize((round(img.width * scale), round(img.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - W) // 2
    top = (resized.height - H) // 2
    return resized.crop((left, top, left + W, top + H))


def measure(draw: ImageDraw.ImageDraw, lines: list[str], fnt: ImageFont.FreeTypeFont, gap: int):
    boxes = [draw.textbbox((0, 0), line, font=fnt) for line in lines]
    widths = [box[2] - box[0] for box in boxes]
    heights = [box[3] - box[1] for box in boxes]
    return max(widths), sum(heights) + gap * (len(lines) - 1), boxes


def fit_font(draw: ImageDraw.ImageDraw, lines: list[str], max_w: int, max_h: int):
    for size in range(72, 41, -2):
        fnt = font(size)
        gap = int(size * 0.24)
        text_w, text_h, _ = measure(draw, lines, fnt, gap)
        if text_w <= max_w and text_h <= max_h:
            return fnt, gap
    return font(42), 10


def draw_telop(img: Image.Image, lines: list[str], y: int) -> Image.Image:
    base = cover_resize(img).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    max_text_w = int(W * 0.76)
    max_text_h = 170
    fnt, gap = fit_font(draw, lines, max_text_w, max_text_h)
    text_w, text_h, boxes = measure(draw, lines, fnt, gap)

    pad_x = 56
    pad_y = 32
    box_w = min(W - 160, text_w + pad_x * 2)
    box_h = text_h + pad_y * 2
    x0 = (W - box_w) // 2
    y0 = y
    x1 = x0 + box_w
    y1 = y0 + box_h

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((x0 + 8, y0 + 10, x1 + 8, y1 + 10), radius=34, fill=SHADOW)
    overlay.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(10)))

    draw.rounded_rectangle((x0, y0, x1, y1), radius=34, fill=WHITE)

    yy = y0 + pad_y
    for line, box in zip(lines, boxes):
        line_w = box[2] - box[0]
        line_h = box[3] - box[1]
        xx = (W - line_w) // 2
        draw.text((xx, yy - box[1]), line, font=fnt, fill=NAVY)
        yy += line_h + gap

    return Image.alpha_composite(base, overlay).convert("RGB")


def make_contact_sheet(paths: list[Path]) -> Path:
    cols = 4
    rows = 3
    thumb_w, thumb_h = 270, 480
    label_h = 36
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (245, 247, 250))
    label_font = ImageFont.load_default()

    for idx, path in enumerate(paths):
        img = Image.open(path).convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (idx % cols) * thumb_w
        y = (idx // cols) * (thumb_h + label_h)
        sheet.paste(img, (x, y))
        ImageDraw.Draw(sheet).text((x + 8, y + thumb_h + 10), path.name, fill=(0, 0, 0), font=label_font)

    out = OUT_DIR / "_contact_sheet_telop_12.png"
    sheet.save(out, quality=94)
    return out


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []

    for frame in FRAMES:
        src = SRC_DIR / frame["src"]
        out = OUT_DIR / frame["out"]
        img = Image.open(src)
        if frame["lines"]:
            draw_telop(img, frame["lines"], frame["y"]).save(out, quality=95)
        else:
            cover_resize(img).save(out, quality=95)
        outputs.append(out)

    contact = make_contact_sheet(outputs)
    manifest = {
        "title": "ギプスをしていても、レントゲンは撮れるの？",
        "size": {"width": W, "height": H},
        "font": str(FONT_PATH),
        "source_dir": str(SRC_DIR),
        "output_dir": str(OUT_DIR),
        "contact_sheet": str(contact),
        "style": "white rounded rectangle, dark navy, short telop",
        "frames": [
            {"source": frame["src"], "output": frame["out"], "telop": frame["lines"]}
            for frame in FRAMES
        ],
    }
    (OUT_DIR / "telop_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8-sig",
    )

    print(OUT_DIR)
    print(contact)


if __name__ == "__main__":
    main()
