from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "toilet_during_exam_series"
INPUT_DIR = ASSET_DIR / "images"
OUT_DIR = ASSET_DIR / "telop_frames"
CONTACT_SHEET = ASSET_DIR / "contact_sheet_telop_frames.png"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (8, 30, 54, 255)
PANEL = (255, 255, 255, 238)
PANEL_EDGE = (255, 255, 255, 255)
SHADOW = (16, 26, 38, 72)
ACCENT = (57, 139, 154, 255)
ACCENT_YELLOW = (255, 213, 86, 255)


FRAMES = [
    {
        "src": "01_patient_mri_flatbed.png",
        "out": "01_patient_mri_flatbed_telop.png",
        "lines": ["検査中に", "トイレに行きたい…"],
        "accent": "yellow",
        "y0": 185,
    },
    {
        "src": "02_patient_mri_hesitate.png",
        "out": "02_patient_mri_hesitate_telop.png",
        "lines": ["あと少しだし", "今さら言えない…"],
        "accent": "yellow",
        "y0": 185,
    },
    {
        "src": "03_rt_pre_exam_guidance.png",
        "out": "03_rt_pre_exam_guidance_telop.png",
        "lines": ["MRIは", "時間がかかることも"],
        "accent": "green",
        "y0": 1220,
    },
    {
        "src": "04_rt_reassure.png",
        "out": "04_rt_reassure_telop.png",
        "lines": ["途中でつらくなることも", "あります"],
        "accent": "green",
        "y0": 1220,
    },
    {
        "src": "05_rt_ct_bladder_explain.png",
        "out": "05_rt_ct_bladder_explain_telop.png",
        "lines": ["検査によっては", "尿をためる場合も"],
        "accent": "green",
        "y0": 1220,
    },
    {
        "src": "06_rt_ct_purpose.png",
        "out": "06_rt_ct_purpose_telop.png",
        "lines": ["それは", "検査目的があるため"],
        "accent": "green",
        "y0": 1220,
    },
    {
        "src": "07_rt_patient_consult.png",
        "out": "07_rt_patient_consult_telop.png",
        "lines": ["つらい時は", "その場で伝えてOK"],
        "accent": "yellow",
        "y0": 1220,
    },
    {
        "src": "08_patient_relieved.png",
        "out": "08_patient_relieved_telop.png",
        "lines": ["「こんなことで」は", "気にしなくて大丈夫"],
        "accent": "yellow",
        "y0": 1220,
    },
    {
        "src": "09_rt_table_pause_explain.png",
        "out": "09_rt_table_pause_explain_telop.png",
        "lines": ["続けるか中断するか", "一緒に判断します"],
        "accent": "green",
        "y0": 1220,
    },
    {
        "src": "10_patient_safe_return.png",
        "out": "10_patient_safe_return_telop.png",
        "lines": ["我慢せず", "伝えてください"],
        "accent": "yellow",
        "y0": 1220,
    },
    {
        "src": "11_smartphone_save.png",
        "out": "11_smartphone_save_telop.png",
        "lines": ["検査前に見返せるよう", "保存しておいてください"],
        "accent": "yellow",
        "y0": 185,
    },
    {
        "src": "12_rt_bow_follow.png",
        "out": "12_rt_bow_follow_telop.png",
        "lines": ["診療放射線技師の発信", "フォローで応援お願いします"],
        "accent": "green",
        "y0": 1220,
    },
]


def load_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size=size)


def cover_resize(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")
    scale = max(W / img.width, H / img.height)
    resized = img.resize((int(img.width * scale), int(img.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - W) // 2
    top = (resized.height - H) // 2
    return resized.crop((left, top, left + W, top + H))


def line_metrics(draw: ImageDraw.ImageDraw, lines: list[str], fnt: ImageFont.ImageFont, spacing: int):
    boxes = [draw.textbbox((0, 0), line, font=fnt) for line in lines]
    widths = [box[2] - box[0] for box in boxes]
    heights = [box[3] - box[1] for box in boxes]
    return max(widths), sum(heights) + spacing * (len(lines) - 1), heights


def fit_font(draw: ImageDraw.ImageDraw, lines: list[str], max_w: int, max_h: int):
    for size in range(72, 38, -2):
        spacing = max(10, int(size * 0.22))
        fnt = load_font(size)
        width, height, _ = line_metrics(draw, lines, fnt, spacing)
        if width <= max_w and height <= max_h:
            return fnt, spacing
    return load_font(38), 10


def draw_telop(img: Image.Image, frame: dict) -> None:
    x0, x1 = 70, 1010
    y0 = frame["y0"]
    y1 = y0 + 238

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x0 + 10, y0 + 14, x1 + 10, y1 + 14), radius=36, fill=SHADOW)
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(13)))

    draw = ImageDraw.Draw(img, "RGBA")
    draw.rounded_rectangle((x0, y0, x1, y1), radius=34, fill=PANEL)
    draw.rounded_rectangle((x0 + 8, y0 + 8, x1 - 8, y1 - 8), radius=28, outline=PANEL_EDGE, width=5)

    accent = ACCENT_YELLOW if frame["accent"] == "yellow" else ACCENT
    draw.rounded_rectangle((x0 + 64, y1 - 34, x1 - 64, y1 - 24), radius=5, fill=accent)

    lines = frame["lines"]
    fnt, spacing = fit_font(draw, lines, (x1 - x0) - 96, (y1 - y0) - 90)
    _, total_h, heights = line_metrics(draw, lines, fnt, spacing)
    yy = y0 + ((y1 - y0) - total_h) // 2 - 8
    for line, line_h in zip(lines, heights):
        bbox = draw.textbbox((0, 0), line, font=fnt)
        line_w = bbox[2] - bbox[0]
        xx = (x0 + x1 - line_w) // 2
        draw.text((xx, yy), line, font=fnt, fill=NAVY)
        yy += line_h + spacing


def make_contact_sheet(paths: list[Path]) -> None:
    cols = 4
    thumb_w, thumb_h = 216, 384
    label_h = 34
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (245, 247, 250))
    label_font = ImageFont.load_default()
    for idx, path in enumerate(paths):
        im = Image.open(path).convert("RGB")
        im.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), "white")
        tile.paste(im, ((thumb_w - im.width) // 2, 0))
        ImageDraw.Draw(tile).text((8, thumb_h + 9), path.name[:30], fill=(0, 0, 0), font=label_font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
    sheet.save(CONTACT_SHEET, quality=94)


def main() -> None:
    if not FONT_PATH.exists():
        raise FileNotFoundError(FONT_PATH)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    outputs = []
    manifest_frames = []
    for frame in FRAMES:
        src = INPUT_DIR / frame["src"]
        out = OUT_DIR / frame["out"]
        if not src.exists():
            raise FileNotFoundError(src)

        img = cover_resize(Image.open(src)).convert("RGBA")
        draw_telop(img, frame)
        img.convert("RGB").save(out, quality=95)
        outputs.append(out)
        manifest_frames.append({"source": str(src), "output": str(out), "telop": frame["lines"]})

    make_contact_sheet(outputs)
    manifest = {
        "title": "トイレに行きたくなった、途中で言っていいの?",
        "size": {"width": W, "height": H},
        "font": str(FONT_PATH),
        "style": "white rounded rectangle backing, dark navy M PLUS Rounded 1c Bold text",
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
