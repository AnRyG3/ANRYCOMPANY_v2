from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "ct_mri_cough_during_exam_20260729"
SRC_DIR = ASSET_DIR / "image_frames"
OUT_DIR = ASSET_DIR / "telop_frames"
CONTACT_SHEET = ASSET_DIR / "contact_sheet_telop_frames.png"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

W, H = 1080, 1920
NAVY = (8, 30, 54, 255)
WHITE = (255, 255, 255, 238)
PANEL_EDGE = (255, 255, 255, 255)
SHADOW = (16, 26, 38, 72)
ACCENT = (32, 128, 150, 255)
ACCENT_WARN = (226, 149, 45, 255)


FRAMES = [
    {
        "src": "s01_patient_cough_urge.png",
        "out": "s01_patient_cough_urge_telop.png",
        "lines": [[("咳", "accent"), ("が出そう…", "navy")], [("我慢", "warn"), ("しないとダメ？", "navy")]],
        "centered": True,
    },
    {
        "src": "s02_worried_about_disturbing_image.png",
        "out": "s02_worried_about_disturbing_image_telop.png",
        "lines": [[("迷惑かも…と", "navy")], [("不安", "warn"), ("になりますよね", "navy")]],
    },
    {
        "src": "s03_pre_exam_reassurance.png",
        "out": "s03_pre_exam_reassurance_telop.png",
        "lines": [[("その気持ち", "accent")], [("おかしくありません", "navy")]],
        "centered": True,
    },
    {
        "src": "s04_exam_room_environment.png",
        "out": "s04_exam_room_environment_telop.png",
        "lines": [[("検査中の", "navy"), ("咳", "accent"), ("は", "navy")], [("珍しくありません", "navy")]],
        "centered": True,
    },
    {
        "src": "s05_body_tension_from_overholding.png",
        "out": "s05_body_tension_from_overholding_telop.png",
        "lines": [[("我慢", "warn"), ("しすぎると", "navy")], [("力が入ることも", "navy")]],
    },
    {
        "src": "s06_staff_can_confirm.png",
        "out": "s06_staff_can_confirm_telop.png",
        "lines": [[("咳が出たことも", "navy")], [("スタッフ側で", "navy"), ("確認", "accent"), ("できます", "navy")]],
    },
    {
        "src": "s07_image_review_workstation.png",
        "out": "s07_image_review_workstation_telop.png",
        "lines": [[("必要に応じて", "navy")], [("画像を", "navy"), ("確認", "accent"), ("します", "navy")]],
    },
    {
        "src": "s08_hesitating_to_signal.png",
        "out": "s08_hesitating_to_signal_telop.png",
        "lines": [[("知らせていいか", "navy")], [("迷うときもあります", "navy")]],
    },
    {
        "src": "s09_staff_intercom_reassurance.png",
        "out": "s09_staff_intercom_reassurance_telop.png",
        "lines": [[("つらいときは", "navy")], [("遠慮なく", "accent"), ("知らせてください", "navy")]],
    },
    {
        "src": "s10_cta_save_smartphone.png",
        "out": "s10_cta_save_smartphone_telop.png",
        "lines": [[("不安なとき用に", "navy")], [("保存", "warn"), ("しておいてください", "navy")]],
        "centered": True,
    },
    {
        "src": "s11_cta_follow_rt_tech.png",
        "out": "s11_cta_follow_rt_tech_telop.png",
        "lines": [[("検査のこと", "navy")], [("一緒に考えていきます", "accent")]],
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


def segment_color(kind: str) -> tuple[int, int, int, int]:
    if kind == "accent":
        return ACCENT
    if kind == "warn":
        return ACCENT_WARN
    return NAVY


def measure_line(draw: ImageDraw.ImageDraw, segments: list[tuple[str, str]], fnt: ImageFont.FreeTypeFont) -> tuple[int, int]:
    width = 0
    height = 0
    for text, _ in segments:
        box = draw.textbbox((0, 0), text, font=fnt)
        width += box[2] - box[0]
        height = max(height, box[3] - box[1])
    return width, height


def measure_lines(draw: ImageDraw.ImageDraw, lines: list[list[tuple[str, str]]], fnt: ImageFont.FreeTypeFont, gap: int):
    sizes = [measure_line(draw, line, fnt) for line in lines]
    return max(width for width, _ in sizes), sum(height for _, height in sizes) + gap * (len(lines) - 1), sizes


def fit_font(draw: ImageDraw.ImageDraw, lines: list[list[tuple[str, str]]]):
    for size in range(72, 42, -2):
        fnt = font(size)
        gap = max(12, int(size * 0.22))
        width, height, sizes = measure_lines(draw, lines, fnt, gap)
        if width <= 820 and height <= 180:
            return fnt, gap, sizes, width, height
    fnt = font(42)
    gap = 12
    width, height, sizes = measure_lines(draw, lines, fnt, gap)
    return fnt, gap, sizes, width, height


def draw_telop(source: Path, frame: dict) -> Image.Image:
    base = cover_resize(Image.open(source)).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    shadow_draw = ImageDraw.Draw(shadow)

    lines = frame["lines"]
    fnt, gap, sizes, text_w, text_h = fit_font(draw, lines)
    pad_x, pad_y = 54, 34
    box_w = min(W - 140, text_w + pad_x * 2)
    box_h = text_h + pad_y * 2
    x0 = (W - box_w) // 2
    y0 = (H - box_h) // 2 if frame.get("centered") else frame.get("y", 220)
    x1, y1 = x0 + box_w, y0 + box_h

    shadow_draw.rounded_rectangle((x0 + 8, y0 + 12, x1 + 8, y1 + 12), radius=34, fill=SHADOW)
    overlay.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(11)))
    draw.rounded_rectangle((x0, y0, x1, y1), radius=34, fill=WHITE)
    draw.rounded_rectangle((x0 + 7, y0 + 7, x1 - 7, y1 - 7), radius=28, outline=PANEL_EDGE, width=4)

    yy = y0 + pad_y
    for line, (line_w, line_h) in zip(lines, sizes):
        xx = x0 + (box_w - line_w) // 2
        for text, kind in line:
            box = draw.textbbox((0, 0), text, font=fnt)
            draw.text((xx, yy - box[1]), text, font=fnt, fill=segment_color(kind))
            xx += box[2] - box[0]
        yy += line_h + gap

    return Image.alpha_composite(base, overlay).convert("RGB")


def make_contact_sheet(paths: list[Path]) -> None:
    cols, thumb_w, thumb_h, label_h = 4, 216, 384, 34
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (245, 247, 250))
    label_font = ImageFont.load_default()
    for idx, path in enumerate(paths):
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), "white")
        tile.paste(image, ((thumb_w - image.width) // 2, 0))
        ImageDraw.Draw(tile).text((8, thumb_h + 9), path.name[:30], fill=(0, 0, 0), font=label_font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
    sheet.save(CONTACT_SHEET, quality=94)


def plain_lines(lines: list[list[tuple[str, str]]]) -> list[str]:
    return ["".join(text for text, _ in line) for line in lines]


def main() -> None:
    if not FONT_PATH.exists():
        raise FileNotFoundError(FONT_PATH)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    outputs = []
    manifest_frames = []
    for frame in FRAMES:
        source = SRC_DIR / frame["src"]
        output = OUT_DIR / frame["out"]
        if not source.exists():
            raise FileNotFoundError(source)
        image = draw_telop(source, frame)
        image.save(output, quality=95)
        outputs.append(output)
        manifest_frames.append(
            {
                "source": str(source),
                "output": str(output),
                "telop": plain_lines(frame["lines"]),
            }
        )

    make_contact_sheet(outputs)
    (OUT_DIR / "telop_manifest.json").write_text(
        json.dumps(
            {
                "title": "検査中に咳が出そうなとき、我慢しなくて大丈夫？",
                "font": str(FONT_PATH),
                "style": "white rounded rectangle backing, dark navy M PLUS Rounded 1c Bold, key words only accented",
                "size": {"width": W, "height": H},
                "frames": manifest_frames,
                "contact_sheet": str(CONTACT_SHEET),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8-sig",
    )
    print(OUT_DIR)
    print(CONTACT_SHEET)


if __name__ == "__main__":
    main()
