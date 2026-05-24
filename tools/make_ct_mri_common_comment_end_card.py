from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
COMMON = ROOT / "reel_assets" / "common"
OUT_VARIANTS = ROOT / "reel_assets" / "ct_mri_difference_v1" / "final_telop_variants"
OUT_FRAMES = ROOT / "reel_assets" / "ct_mri_difference_v1" / "telop_frames"

W, H = 1080, 1920
FONT_BOLD = r"C:\Windows\Fonts\YuGothB.ttc"
FONT_REG = r"C:\Windows\Fonts\YuGothM.ttc"


def font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def center(draw: ImageDraw.ImageDraw, xywh, text, fnt, fill):
    x, y, w, h = xywh
    box = draw.multiline_textbbox((0, 0), text, font=fnt, spacing=18, align="center")
    tw, th = box[2] - box[0], box[3] - box[1]
    draw.multiline_text((x + w / 2 - tw / 2, y + h / 2 - th / 2), text, font=fnt, fill=fill, spacing=18, align="center")


def rounded_rect(draw, xy, radius, fill):
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def draw_comment_icon(draw, cx, cy, color):
    stroke = 18
    draw.ellipse((cx - 118, cy - 88, cx + 118, cy + 88), outline=color, width=stroke)
    draw.line((cx - 45, cy + 80, cx - 78, cy + 148, cx + 14, cy + 94), fill=color, width=stroke, joint="curve")


def main():
    OUT_VARIANTS.mkdir(parents=True, exist_ok=True)
    OUT_FRAMES.mkdir(parents=True, exist_ok=True)

    # Recreate the common comment end-card style with CT/MRI-specific wording.
    img = Image.new("RGB", (W, H), "#fff7df")
    draw = ImageDraw.Draw(img)

    # Soft diagonal stripe background, matching the common cards.
    for i in range(-H, W, 74):
        draw.line((i, 0, i + H, H), fill="#ffffff", width=8)

    navy = "#0f172a"
    yellow = "#facc15"

    center(draw, (90, 250, 900, 80), "縺ゅ↑縺溘・縺ｩ縺｣縺｡・・, font(42), navy)
    center(draw, (80, 360, 920, 240), "CT縺ｨMRI\n縺ｩ縺｣縺｡縺御ｸ榊ｮ会ｼ・, font(74), navy)

    rounded_rect(draw, (140, 720, 940, 1290), 44, "#ffffff")
    rounded_rect(draw, (140, 720, 940, 740), 10, yellow)
    draw_comment_icon(draw, 540, 930, yellow)

    center(draw, (200, 1060, 680, 180), "繧ｳ繝｡繝ｳ繝医〒\n謨吶∴縺ｦ縺上□縺輔＞", font(54), navy)
    draw.line((300, 1240, 780, 1240), fill=yellow, width=18)

    center(draw, (120, 1540, 840, 70), "豌苓ｻｽ縺ｫ蜿ょ刈縺励※縺上□縺輔＞", font(44), "#334155")
    center(draw, (120, 1648, 840, 48), "窶ｻ蛟句挨縺ｮ蛹ｻ逋ら嶌隲・・蛹ｻ逋よｩ滄未縺ｸ", font(28, False), "#64748b")

    variant_path = OUT_VARIANTS / "final_b_comment_common.png"
    frame_path = OUT_FRAMES / "cut_06.png"
    img.save(variant_path)
    img.save(frame_path)
    print(variant_path)
    print(frame_path)


if __name__ == "__main__":
    main()


