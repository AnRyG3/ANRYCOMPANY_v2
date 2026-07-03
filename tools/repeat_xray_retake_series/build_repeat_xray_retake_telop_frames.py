from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "repeat_xray_retake_series"
BG_DIR = ASSET_DIR / "background_frames_no_text"
OUT_DIR = ASSET_DIR / "telop_frames"
CONTACT_SHEET = ASSET_DIR / "contact_sheet_telop_frames.png"

W, H = 1080, 1920
NAVY = (8, 30, 54, 255)
PANEL = (255, 255, 255, 238)
PANEL_EDGE = (255, 255, 255, 255)
SHADOW = (16, 26, 38, 70)
ACCENT = (57, 139, 154, 255)
ACCENT_YELLOW = (255, 213, 86, 255)

FONT_Noto_BOLD = [
    r"F:\ANRYCAMPANY\reel_assets\fonts\M_PLUS_Rounded_1c\MPLUSRounded1c-Bold.ttf",
    r"C:\Windows\Fonts\NotoSansJP-VF.ttf",
    r"C:\Windows\Fonts\YuGothB.ttc",
    r"C:\Windows\Fonts\BIZ-UDGothicB.ttc",
    r"C:\Windows\Fonts\meiryob.ttc",
]
FONT_ROUNDED_BOLD = [
    r"F:\ANRYCAMPANY\reel_assets\fonts\M_PLUS_Rounded_1c\MPLUSRounded1c-Bold.ttf",
    r"C:\Windows\Fonts\NotoSansJP-VF.ttf",
    r"C:\Windows\Fonts\YuGothB.ttc",
    r"C:\Windows\Fonts\meiryob.ttc",
]


FRAMES = [
    {
        "src": "01_patient_question.png",
        "out": "01_patient_question_telop.png",
        "lines": ["もう一度撮ってって", "言われた…", "私が動いちゃったから？"],
        "kind": "rounded",
        "accent": "yellow",
    },
    {
        "src": "02_empathy_corridor_bench.png",
        "out": "02_empathy_corridor_bench_telop.png",
        "lines": ["呼び戻されて", "不安になる気持ち", "おかしくありません"],
        "kind": "rounded",
    },
    {
        "src": "03_doctor_instruction.png",
        "out": "03_doctor_instruction_telop.png",
        "lines": ["診断に必要な情報を", "もう少しそろえるために"],
        "kind": "standard",
        "accent": "green",
    },
    {
        "src": "04_not_patient_fault.png",
        "out": "04_not_patient_fault_telop.png",
        "lines": ["角度・位置・見たい範囲など", "理由はいくつかあります"],
        "kind": "standard",
    },
    {
        "src": "05_not_blaming_voice.png",
        "out": "05_not_blaming_voice_telop.png",
        "lines": ["「もう一度お願いします」は", "責めている言葉ではありません"],
        "kind": "rounded",
        "box": (54, 150, 1026, 430),
    },
    {
        "src": "06_called_back_anxiety.png",
        "out": "06_called_back_anxiety_telop.png",
        "lines": ["急に呼び戻されると", "不安になりますよね"],
        "kind": "rounded",
    },
    {
        "src": "07_positioning_v2.png",
        "out": "07_positioning_v2_telop.png",
        "lines": ["診療放射線技師は", "医師の意図に応えて", "撮影します"],
        "kind": "standard",
        "accent": "green",
    },
    {
        "src": "08_no_fault_reassurance.png",
        "out": "08_no_fault_reassurance_telop.png",
        "lines": ["患者さんに", "落ち度はありません"],
        "kind": "rounded",
        "accent": "yellow",
    },
    {
        "src": "09_relief_after_exam.png",
        "out": "09_relief_after_exam_telop.png",
        "lines": ["再撮影でも", "責められているわけでは", "ありません"],
        "kind": "rounded",
    },
    {
        "src": "10_cta_save_background.png",
        "out": "10_cta_save_telop.png",
        "lines": ["あとで見返せるように", "保存しておくと便利です"],
        "kind": "rounded",
        "box": (72, 700, 1008, 1000),
        "accent": "green",
    },
    {
        "src": "11_cta_follow_background.png",
        "out": "11_cta_follow_telop.png",
        "lines": ["検査の疑問に", "診療放射線技師が答えます", "フォローしてお待ちください"],
        "kind": "rounded",
        "box": (54, 640, 1026, 1040),
        "accent": "green",
    },
]


def choose_font(size: int, kind: str):
    candidates = FONT_ROUNDED_BOLD if kind == "rounded" else FONT_Noto_BOLD
    for font_path in candidates:
        if Path(font_path).exists():
            return ImageFont.truetype(font_path, size=size)
    return ImageFont.load_default()


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
    spacing = 16
    for size in range(78, 40, -2):
        font = choose_font(size, kind)
        width, height, _ = measure_lines(draw, lines, font, spacing)
        if width <= max_w and height <= max_h:
            return font, spacing
    return choose_font(40, kind), 12


def draw_soft_readability(img: Image.Image) -> None:
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, W, 520), fill=(255, 255, 255, 20))
    img.alpha_composite(overlay)


def draw_telop(img: Image.Image, frame: dict) -> None:
    x0, y0, x1, y1 = frame.get("box", (72, 150, 1008, 430))
    lines = frame["lines"]
    kind = frame["kind"]

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x0 + 10, y0 + 12, x1 + 10, y1 + 12), radius=36, fill=SHADOW)
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(12)))

    draw = ImageDraw.Draw(img, "RGBA")
    draw.rounded_rectangle((x0, y0, x1, y1), radius=34, fill=PANEL)
    draw.rounded_rectangle((x0 + 8, y0 + 8, x1 - 8, y1 - 8), radius=28, outline=PANEL_EDGE, width=5)

    accent = frame.get("accent")
    if accent:
        color = ACCENT_YELLOW if accent == "yellow" else ACCENT
        draw.rounded_rectangle((x0 + 60, y1 - 34, x1 - 60, y1 - 24), radius=5, fill=color)

    font, spacing = fit_font(draw, lines, kind, (x1 - x0) - 96, (y1 - y0) - 88)
    _, total_h, heights = measure_lines(draw, lines, font, spacing)
    yy = y0 + ((y1 - y0) - total_h) // 2 - 6
    for line, line_h in zip(lines, heights):
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        draw.text(((x0 + x1 - line_w) // 2, yy), line, font=font, fill=NAVY)
        yy += line_h + spacing


def make_contact_sheet(paths: list[Path]) -> None:
    cols = 4
    thumb_w, thumb_h = 216, 384
    label_h = 36
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (245, 247, 250))
    label_font = ImageFont.load_default()
    for idx, path in enumerate(paths):
        img = Image.open(path).convert("RGB")
        img.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), "white")
        tile.paste(img, ((thumb_w - img.width) // 2, 0))
        ImageDraw.Draw(tile).text((8, thumb_h + 10), path.name[:30], fill=(0, 0, 0), font=label_font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
    sheet.save(CONTACT_SHEET, quality=94)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    manifest_frames = []
    for frame in FRAMES:
        src = BG_DIR / frame["src"]
        out = OUT_DIR / frame["out"]
        img = cover_resize(Image.open(src)).convert("RGBA")
        draw_soft_readability(img)
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
        "title": "レントゲンで再撮影になるのは失敗ですか？",
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
