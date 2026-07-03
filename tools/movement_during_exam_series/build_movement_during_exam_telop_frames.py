from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "movement_during_exam_series"
BG_DIR = ASSET_DIR / "background_frames_no_text"
OUT_DIR = ASSET_DIR / "telop_frames"
CONTACT_SHEET = ASSET_DIR / "contact_sheet_telop_frames.png"

W, H = 1080, 1920
NAVY = (8, 30, 54, 255)
PANEL = (255, 255, 255, 238)
PANEL_EDGE = (255, 255, 255, 255)
SHADOW = (16, 26, 38, 74)
ACCENT = (57, 139, 154, 255)
ACCENT_YELLOW = (255, 213, 86, 255)
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"


FRAMES = [
    {
        "src": "01_patient_apologetic_no_text.png",
        "out": "01_patient_apologetic_telop.png",
        "lines": ["動いてしまって", "思わず「すみません」"],
        "accent": "yellow",
    },
    {
        "src": "02_rt_nods_to_patient_no_text.png",
        "out": "02_moving_is_common_telop.png",
        "lines": ["動くこと", "意外とよくあります"],
        "accent": "green",
    },
    {
        "src": "03_rt_reassuring_smile_no_text.png",
        "out": "03_no_need_to_apologize_telop.png",
        "lines": ["謝らなくて", "大丈夫です"],
        "accent": "yellow",
    },
    {
        "src": "04_rt_control_monitor_no_text.png",
        "out": "04_staff_handles_it_telop.png",
        "lines": ["動いても", "その場で対応しています"],
        "accent": "green",
    },
    {
        "src": "05_rt_checks_xray_monitor_no_text.png",
        "out": "05_not_always_big_problem_telop.png",
        "lines": ["大きな問題とは", "限りません"],
        "accent": "green",
    },
    {
        "src": "06_patient_relaxed_on_table_no_text.png",
        "out": "06_body_natural_telop.png",
        "lines": ["じっとするのは", "難しいものです"],
        "accent": "yellow",
    },
    {
        "src": "07_support_cushion_xray_room_no_text.png",
        "out": "07_positioning_support_telop.png",
        "lines": ["動きにくいよう", "支える工夫もあります"],
        "accent": "green",
    },
    {
        "src": "08_pre_exam_conversation_no_text.png",
        "out": "08_tell_us_telop.png",
        "lines": ["気になることは", "遠慮なく伝えてください"],
        "accent": "green",
    },
    {
        "src": "09_patient_leaves_relieved_no_text.png",
        "out": "09_dont_worry_too_much_telop.png",
        "lines": ["動いたかも、と思っても", "心配しすぎなくて大丈夫"],
        "accent": "yellow",
        "y0": 1160,
    },
    {
        "src": "10_rt_walks_corridor_no_text.png",
        "out": "10_next_topic_telop.png",
        "lines": ["レントゲンやCTの", "気になるを次回も"],
        "accent": "green",
        "y0": 1160,
    },
    {
        "src": "11_smartphone_save_closeup_no_text.png",
        "out": "11_save_cta_telop.png",
        "lines": ["役に立ったら", "保存してください"],
        "accent": "yellow",
        "y0": 1160,
    },
    {
        "src": "12_rt_bow_follow_no_text.png",
        "out": "12_follow_cta_telop.png",
        "lines": ["診療放射線技師の発信", "フォローで応援お願いします"],
        "accent": "green",
        "y0": 1160,
    },
]


def font(size: int) -> ImageFont.FreeTypeFont:
    if FONT_PATH.exists():
        return ImageFont.truetype(str(FONT_PATH), size=size)
    return ImageFont.load_default()


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
    for size in range(76, 38, -2):
        spacing = max(10, int(size * 0.22))
        fnt = font(size)
        width, height, _ = line_metrics(draw, lines, fnt, spacing)
        if width <= max_w and height <= max_h:
            return fnt, spacing
    return font(38), 10


def panel_box(lines: list[str]) -> tuple[int, int, int, int]:
    x0, x1 = 70, 1010
    y0 = 175
    height = 250 if len(lines) <= 2 else 330
    return x0, y0, x1, y0 + height


def draw_telop(img: Image.Image, frame: dict) -> None:
    x0, y0, x1, y1 = panel_box(frame["lines"])
    if "y0" in frame:
        height = y1 - y0
        y0 = frame["y0"]
        y1 = y0 + height

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x0 + 10, y0 + 14, x1 + 10, y1 + 14), radius=36, fill=SHADOW)
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(13)))

    draw = ImageDraw.Draw(img, "RGBA")
    draw.rounded_rectangle((x0, y0, x1, y1), radius=34, fill=PANEL)
    draw.rounded_rectangle((x0 + 8, y0 + 8, x1 - 8, y1 - 8), radius=28, outline=PANEL_EDGE, width=5)

    accent = ACCENT_YELLOW if frame.get("accent") == "yellow" else ACCENT
    draw.rounded_rectangle((x0 + 64, y1 - 34, x1 - 64, y1 - 24), radius=5, fill=accent)

    fnt, spacing = fit_font(draw, frame["lines"], (x1 - x0) - 96, (y1 - y0) - 88)
    _, total_h, heights = line_metrics(draw, frame["lines"], fnt, spacing)
    yy = y0 + ((y1 - y0) - total_h) // 2 - 6
    for line, line_h in zip(frame["lines"], heights):
        bbox = draw.textbbox((0, 0), line, font=fnt)
        xx = (x0 + x1 - (bbox[2] - bbox[0])) // 2
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
        ImageDraw.Draw(tile).text((8, thumb_h + 9), path.name[:29], fill=(0, 0, 0), font=label_font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
    sheet.save(CONTACT_SHEET, quality=94)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    manifest_frames = []
    for frame in FRAMES:
        src = BG_DIR / frame["src"]
        out = OUT_DIR / frame["out"]
        img = cover_resize(Image.open(src)).convert("RGBA")
        draw_telop(img, frame)
        img.convert("RGB").save(out, quality=95)
        outputs.append(out)
        manifest_frames.append({"source": str(src), "output": str(out), "telop": frame["lines"]})

    make_contact_sheet(outputs)
    manifest = {
        "title": "検査中に動いてしまったとき",
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
