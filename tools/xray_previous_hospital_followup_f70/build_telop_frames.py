from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "xray_previous_hospital_followup_f70"
OUT_DIR = ASSET_DIR / "telop_frames"
CONTACT_SHEET = ASSET_DIR / "contact_sheet_telop_frames.png"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (8, 30, 54, 255)
ACCENT = (37, 124, 142, 255)
WHITE = (255, 255, 255, 240)
SHADOW = (16, 26, 38, 72)


FRAMES = [
    {
        "src": "frame_01_patient_question.png",
        "out": "frame_01_telop.png",
        "lines": [[("前の病院でも", True), ("撮ったのに？", False)]],
    },
    {
        "src": "frame_02_repeat_uncertainty.png",
        "out": "frame_02_telop.png",
        "lines": [[("くり返す意味", True), ("があるのかな", False)]],
    },
    {
        "src": "frame_03_rt_listening.png",
        "out": "frame_03_telop.png",
        "lines": [[("その気持ち", True), ("、自然です", False)]],
    },
    {
        "src": "frame_04_doctor_comparison.png",
        "out": "frame_04_telop.png",
        "lines": [[("前の画像", True), ("との", False), ("比較", True), ("が大切", False)]],
    },
    {
        "src": "frame_05_single_image_context.png",
        "out": "frame_05_telop.png",
        "lines": [[("1枚だけ", True), ("では分かりにくいことも", False)]],
    },
    {
        "src": "frame_06_side_by_side_xray.png",
        "out": "frame_06_telop.png",
        "lines": [[("変化", True), ("が見えてきます", False)]],
    },
    {
        "src": "frame_07_prior_image_handoff.png",
        "out": "frame_07_telop.png",
        "lines": [[("前の画像", True), ("が診断の助けに", False)]],
    },
    {
        "src": "frame_08_repeat_question.png",
        "out": "frame_08_telop.png",
        "lines": [[("何度も撮る意味", True), ("あるのかな", False)]],
    },
    {
        "src": "frame_09_doctor_reassurance.png",
        "out": "frame_09_telop.png",
        "lines": [[("回復の道すじ", True), ("を確認します", False)]],
    },
    {
        "src": "frame_10_save_cta_bg.png",
        "out": "frame_10_telop.png",
        "lines": [[("保存", True), ("して見返せます", False)]],
        "y": 585,
        "center_x": 545,
    },
    {
        "src": "frame_11_follow_cta_bg.png",
        "out": "frame_11_telop.png",
        "lines": [[("検査の不安", True), ("をやさしく解説", False)]],
        "y": 640,
        "center_x": 650,
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


def line_size(draw: ImageDraw.ImageDraw, line, fnt: ImageFont.FreeTypeFont):
    width = 0
    height = 0
    top = 0
    for text, _ in line:
        box = draw.textbbox((0, 0), text, font=fnt)
        width += box[2] - box[0]
        height = max(height, box[3] - box[1])
        top = min(top, box[1])
    return width, height, top


def block_size(draw: ImageDraw.ImageDraw, lines, fnt: ImageFont.FreeTypeFont, gap: int):
    sizes = [line_size(draw, line, fnt) for line in lines]
    width = max(size[0] for size in sizes)
    height = sum(size[1] for size in sizes) + gap * (len(lines) - 1)
    return width, height, sizes


def fit_font(draw: ImageDraw.ImageDraw, lines, max_w: int, max_h: int):
    for size in range(70, 40, -2):
        fnt = font(size)
        gap = max(10, int(size * 0.22))
        width, height, _ = block_size(draw, lines, fnt, gap)
        if width <= max_w and height <= max_h:
            return fnt, gap
    return font(40), 10


def draw_rich_line(draw: ImageDraw.ImageDraw, xy, line, fnt):
    x, y = xy
    for text, emph in line:
        fill = ACCENT if emph else NAVY
        box = draw.textbbox((0, 0), text, font=fnt)
        draw.text((x, y - box[1]), text, font=fnt, fill=fill)
        x += box[2] - box[0]


def draw_telop(img: Image.Image, lines, y: int = 205, center_x: int = W // 2) -> Image.Image:
    base = cover_resize(img).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    shadow_draw = ImageDraw.Draw(shadow_layer)

    max_text_w = int(W * 0.77)
    max_text_h = 165
    fnt, gap = fit_font(draw, lines, max_text_w, max_text_h)
    text_w, text_h, sizes = block_size(draw, lines, fnt, gap)

    pad_x = 54
    pad_y = 30
    box_w = min(W - 148, text_w + pad_x * 2)
    box_h = text_h + pad_y * 2
    x0 = max(54, min(W - box_w - 54, center_x - box_w // 2))
    y0 = y
    x1 = x0 + box_w
    y1 = y0 + box_h

    shadow_draw.rounded_rectangle((x0 + 8, y0 + 10, x1 + 8, y1 + 10), radius=32, fill=SHADOW)
    overlay.alpha_composite(shadow_layer.filter(ImageFilter.GaussianBlur(10)))
    draw.rounded_rectangle((x0, y0, x1, y1), radius=32, fill=WHITE)

    yy = y0 + pad_y
    for line, (line_w, line_h, _top) in zip(lines, sizes):
        xx = (W - line_w) // 2
        draw_rich_line(draw, (xx, yy), line, fnt)
        yy += line_h + gap

    return Image.alpha_composite(base, overlay).convert("RGB")


def plain_telop(lines) -> list[str]:
    return ["".join(text for text, _ in line) for line in lines]


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
        draw_telop(
            Image.open(src),
            frame["lines"],
            y=frame.get("y", 205),
            center_x=frame.get("center_x", W // 2),
        ).save(out, quality=95)
        outputs.append(out)
        manifest_frames.append(
            {
                "source": str(src),
                "output": str(out),
                "telop": plain_telop(frame["lines"]),
                "emphasis": [text for line in frame["lines"] for text, emph in line if emph],
            }
        )

    make_contact_sheet(outputs)
    manifest = {
        "title": "前の病院でも撮ったのに、また撮るんですか？",
        "size": {"width": W, "height": H},
        "font": str(FONT_PATH),
        "style": "white rounded rectangle 94% opacity, dark navy text, teal emphasis words, M PLUS Rounded 1c Bold",
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
