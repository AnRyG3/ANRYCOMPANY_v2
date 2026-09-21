from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(r"F:\ANRYCAMPANY")
SRC_DIR = ROOT / "reel_assets" / "ct_series" / "ct_contrast_dominant_arm_v1_images"
OUT_DIR = ROOT / "reel_assets" / "ct_series" / "ct_contrast_dominant_arm_v1_telop_frames"
CONTACT_SHEET = OUT_DIR / "contact_sheet.png"
MANIFEST = OUT_DIR / "telop_manifest.json"

W, H = 1080, 1920
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"
NAVY = (22, 45, 78, 255)
BLUE = (42, 126, 190, 255)
WHITE_BACKING = (255, 255, 255, 153)  # 60% opacity
SHADOW = (20, 35, 52, 65)


FRAMES = [
    {
        "src": "scene_01_hook_patient_thought.png",
        "out": "scene_01_hook_patient_thought_telop.png",
        "lines": [("利き腕", "に"), ("注射しても大丈夫？",)],
        "position": "top",
    },
    {
        "src": "scene_02_action_tell_nurse.png",
        "out": "scene_02_action_tell_nurse_telop.png",
        "lines": [("「", "反対の腕", "はできますか？」"), ("注射前に伝えて大丈夫です",)],
        "position": "top",
    },
    {
        "src": "scene_03_ct_preparation.png",
        "out": "scene_03_ct_preparation_telop.png",
        "lines": [("腕は", "血管", "の状態などを見て"), ("決めます",)],
        "position": "center",
    },
    {
        "src": "scene_04_check_arm.png",
        "out": "scene_04_check_arm_telop.png",
        "lines": [("血管", "の状態や検査内容を"), ("確認します",)],
        "position": "top",
    },
    {
        "src": "scene_05_reassured_patient.png",
        "out": "scene_05_reassured_patient_telop.png",
        "lines": [("利き腕", "だから"), ("必ず避けるわけではありません",)],
        "position": "top",
    },
    {
        "src": "scene_06_share_preference.png",
        "out": "scene_06_share_preference_telop.png",
        "lines": [("希望", "を伝えることは"), ("わがままではありません",)],
        "position": "center",
    },
    {
        "src": "scene_07_staff_explains.png",
        "out": "scene_07_staff_explains_telop.png",
        "lines": [("希望に沿えないときも",), ("理由", "を聞いて大丈夫です",)],
        "position": "center",
    },
    {
        "src": "scene_08_ready_for_ct.png",
        "out": "scene_08_ready_for_ct_telop.png",
        "lines": [("理由", "がわかると"), ("安心して進めます",)],
        "position": "center",
    },
    {
        "src": "scene_09_save_cta_home.png",
        "out": "scene_09_save_cta_home_telop.png",
        "lines": [("検査前日に見返せるよう",), ("保存", "しておいてください",)],
        "position": "top",
    },
]


def cover_resize(image: Image.Image) -> Image.Image:
    image = image.convert("RGB")
    scale = max(W / image.width, H / image.height)
    size = (round(image.width * scale), round(image.height * scale))
    image = image.resize(size, Image.Resampling.LANCZOS)
    left = (image.width - W) // 2
    top = (image.height - H) // 2
    return image.crop((left, top, left + W, top + H)).convert("RGBA")


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size)


def token_color(token: str) -> tuple[int, int, int, int]:
    return BLUE if token in {"利き腕", "反対の腕", "血管", "希望", "理由", "保存"} else NAVY


def line_size(draw: ImageDraw.ImageDraw, tokens: tuple[str, ...], fnt: ImageFont.FreeTypeFont) -> tuple[int, int]:
    widths = [draw.textbbox((0, 0), token, font=fnt)[2] for token in tokens]
    box = draw.textbbox((0, 0), "あ", font=fnt)
    return sum(widths), box[3] - box[1]


def fit_font(draw: ImageDraw.ImageDraw, lines: list[tuple[str, ...]], max_width: int) -> ImageFont.FreeTypeFont:
    for size in range(80, 43, -2):
        fnt = font(size)
        if max(line_size(draw, line, fnt)[0] for line in lines) <= max_width:
            return fnt
    return font(42)


def telop_box(position: str) -> tuple[int, int, int, int]:
    if position == "top":
        return (90, 235, 990, 505)
    return (90, 770, 990, 1050)


def draw_telop(base: Image.Image, frame: dict) -> None:
    x0, y0, x1, y1 = telop_box(frame["position"])
    lines = frame["lines"]
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((x0 + 8, y0 + 10, x1 + 8, y1 + 10), radius=38, fill=SHADOW)
    base.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(10)))

    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((x0, y0, x1, y1), radius=38, fill=WHITE_BACKING)
    fnt = fit_font(draw, lines, (x1 - x0) - 90)
    _, line_height = line_size(draw, ("あ",), fnt)
    spacing = 24
    total_height = line_height * len(lines) + spacing * (len(lines) - 1)
    y = y0 + (y1 - y0 - total_height) // 2 - 5
    for tokens in lines:
        width, _ = line_size(draw, tokens, fnt)
        x = (W - width) // 2
        for token in tokens:
            draw.text((x, y), token, font=fnt, fill=token_color(token))
            x += draw.textbbox((0, 0), token, font=fnt)[2]
        y += line_height + spacing
    base.alpha_composite(canvas)


def make_contact_sheet(paths: list[Path]) -> None:
    cols, thumb_w, thumb_h, label_h = 3, 216, 384, 34
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (245, 247, 250))
    label_font = ImageFont.load_default()
    for index, path in enumerate(paths):
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), "white")
        tile.paste(image, ((thumb_w - image.width) // 2, 0))
        ImageDraw.Draw(tile).text((8, thumb_h + 9), path.stem[:31], font=label_font, fill=(0, 0, 0))
        sheet.paste(tile, ((index % cols) * thumb_w, (index // cols) * (thumb_h + label_h)))
    sheet.save(CONTACT_SHEET, quality=94)


def main() -> None:
    if not FONT_PATH.exists():
        raise FileNotFoundError(FONT_PATH)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    for frame in FRAMES:
        image = cover_resize(Image.open(SRC_DIR / frame["src"]))
        draw_telop(image, frame)
        output = OUT_DIR / frame["out"]
        image.convert("RGB").save(output, quality=95)
        outputs.append(output)
    make_contact_sheet(outputs)
    MANIFEST.write_text(json.dumps({
        "title": "造影CTの注射、利き腕でも大丈夫？",
        "font": str(FONT_PATH),
        "style": "60% white rounded backing, navy text, keyword-only blue emphasis, centered x-axis",
        "frames": [{"source": frame["src"], "output": frame["out"], "position": frame["position"], "telop": ["".join(line) for line in frame["lines"]]} for frame in FRAMES],
    }, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(OUT_DIR)
    print(CONTACT_SHEET)


if __name__ == "__main__":
    main()
