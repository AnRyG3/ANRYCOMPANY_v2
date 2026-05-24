from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
OUT = ROOT / "reel_assets" / "retest_check_02"
FRAMES = OUT / "telop_frames"
STORYBOARD = OUT / "storyboard_retest_check_02.png"

W, H = 1080, 1920
FONT_BOLD = r"C:\Windows\Fonts\YuGothB.ttc"
FONT_REG = r"C:\Windows\Fonts\YuGothM.ttc"

NAVY = "#15324a"
TEAL = "#0f7b83"
MINT = "#bfe9df"
CREAM = "#fff7e6"
CORAL = "#e95b5b"
GREEN = "#6bbf84"
YELLOW = "#f6c85f"
SLATE = "#587184"
DISCLAIMER = "※個別の判断は医療機関へご相談ください"


def font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def text_width(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, max_w: int):
    lines = []
    for paragraph in text.split("\n"):
        current = ""
        for ch in paragraph:
            test = current + ch
            if text_width(draw, test, fnt) <= max_w or not current:
                current = test
            else:
                lines.append(current)
                current = ch
        if current:
            lines.append(current)
    return lines


def fit_text(draw: ImageDraw.ImageDraw, text: str, max_w: int, max_lines: int, start: int, minimum: int = 40):
    size = start
    while size >= minimum:
        fnt = font(size, True)
        lines = wrap_text(draw, text, fnt, max_w)
        if len(lines) <= max_lines and all(text_width(draw, line, fnt) <= max_w for line in lines):
            return fnt, lines
        size -= 2
    fnt = font(minimum, True)
    return fnt, wrap_text(draw, text, fnt, max_w)


def gradient_bg(top: str, bottom: str) -> Image.Image:
    img = Image.new("RGB", (W, H), top)
    draw = ImageDraw.Draw(img)
    tr, tg, tb = Image.new("RGB", (1, 1), top).getpixel((0, 0))
    br, bg, bb = Image.new("RGB", (1, 1), bottom).getpixel((0, 0))
    for y in range(H):
        t = y / (H - 1)
        r = int(tr + (br - tr) * t)
        g = int(tg + (bg - tg) * t)
        b = int(tb + (bb - tb) * t)
        draw.line((0, y, W, y), fill=(r, g, b))
    return img.convert("RGBA")


def draw_soft_clinic_bg(base: Image.Image):
    draw = ImageDraw.Draw(base)
    shapes = [
        (150, 240, 280, 190, (255, 255, 255, 95)),
        (930, 410, 310, 220, (255, 255, 255, 72)),
        (150, 1540, 360, 230, (15, 123, 131, 34)),
        (930, 1600, 360, 260, (233, 91, 91, 28)),
        (540, 1120, 620, 160, (255, 255, 255, 40)),
    ]
    for cx, cy, rx, ry, color in shapes:
        draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=color)
    for x in range(-200, W + 200, 160):
        draw.line((x, 0, x + 680, H), fill=(255, 255, 255, 24), width=8)


def draw_person(draw: ImageDraw.ImageDraw, x: int, y: int, anxious: bool = False):
    draw.ellipse((x - 95, y - 250, x + 95, y - 60), fill=CREAM, outline=NAVY, width=8)
    eye_y = y - 155
    if anxious:
        draw.arc((x - 64, eye_y - 24, x - 22, eye_y + 28), 190, 340, fill=NAVY, width=6)
        draw.arc((x + 22, eye_y - 24, x + 64, eye_y + 28), 200, 350, fill=NAVY, width=6)
        draw.arc((x - 48, y - 90, x + 48, y - 20), 205, 335, fill=CORAL, width=8)
    else:
        draw.ellipse((x - 48, eye_y, x - 32, eye_y + 16), fill=NAVY)
        draw.ellipse((x + 32, eye_y, x + 48, eye_y + 16), fill=NAVY)
        draw.arc((x - 45, y - 110, x + 45, y - 42), 20, 160, fill=NAVY, width=7)
    draw.rounded_rectangle((x - 185, y - 50, x + 185, y + 410), radius=92, fill=TEAL)
    draw.line((x - 170, y + 80, x - 270, y + 230), fill=NAVY, width=24)
    draw.line((x + 170, y + 80, x + 270, y + 230), fill=NAVY, width=24)


def draw_report(draw: ImageDraw.ImageDraw, x1: int, y1: int, x2: int, y2: int, mark: str = ""):
    draw.rounded_rectangle((x1, y1, x2, y2), radius=44, fill=(255, 255, 255, 232), outline=(143, 169, 183, 190), width=4)
    draw.rectangle((x1 + 60, y1 + 95, x2 - 60, y1 + 170), fill=MINT)
    for i, width in enumerate([420, 340, 390, 290]):
        y = y1 + 300 + i * 105
        draw.line((x1 + 90, y, x1 + 90 + width, y), fill="#9fb8c5", width=15)
    if mark == "question":
        draw.text(((x1 + x2) // 2, y2 - 230), "?", font=font(170, True), fill=YELLOW, anchor="mm")
    elif mark == "cross":
        draw.line((x1 + 115, y2 - 150, x2 - 115, y1 + 250), fill=CORAL, width=26)
        draw.line((x1 + 115, y1 + 250, x2 - 115, y2 - 150), fill=CORAL, width=26)
    elif mark == "check":
        draw.line((x1 + 140, y2 - 210, x1 + 275, y2 - 80), fill=GREEN, width=28)
        draw.line((x1 + 275, y2 - 80, x2 - 115, y1 + 250), fill=GREEN, width=28)


def draw_scan(draw: ImageDraw.ImageDraw, x: int, y: int):
    draw.rounded_rectangle((x - 360, y - 290, x + 220, y + 290), radius=40, fill=(255, 255, 255, 230), outline=(143, 169, 183, 180), width=4)
    for i in range(6):
        lx = x - 300 + i * 82
        shade = 96 + i * 22
        draw.rounded_rectangle((lx, y - 185, lx + 58, y + 185), radius=12, fill=(shade, shade + 12, shade + 24))
    draw.ellipse((x + 35, y - 150, x + 350, y + 165), outline=NAVY, width=28)
    draw.line((x + 280, y + 105, x + 420, y + 245), fill=NAVY, width=34)


def draw_yes_no(draw: ImageDraw.ImageDraw):
    draw.rounded_rectangle((150, 500, 930, 1130), radius=54, fill=(255, 255, 255, 228), outline=(143, 169, 183, 170), width=4)
    draw.ellipse((250, 690, 445, 885), outline=TEAL, width=24)
    draw.text((350, 970), "ある", font=font(60, True), fill=TEAL, anchor="mm")
    draw.line((640, 705, 810, 875), fill=CORAL, width=24)
    draw.line((810, 705, 640, 875), fill=CORAL, width=24)
    draw.text((725, 970), "ない", font=font(60, True), fill=CORAL, anchor="mm")
    draw.line((520, 610, 520, 1060), fill=(143, 169, 183, 160), width=8)


def draw_steps(draw: ImageDraw.ImageDraw):
    points = [(240, 780), (540, 610), (840, 780), (670, 1080), (350, 1080)]
    for a, b in zip(points, points[1:]):
        draw.line((a[0], a[1], b[0], b[1]), fill=SLATE, width=18)
    for i, (x, y) in enumerate(points, start=1):
        fill = TEAL if i < 5 else GREEN
        draw.ellipse((x - 90, y - 90, x + 90, y + 90), fill=fill, outline=(255, 255, 255, 230), width=8)
        draw.text((x, y + 5), str(i), font=font(72, True), fill="white", anchor="mm")


def draw_breath(draw: ImageDraw.ImageDraw):
    draw_person(draw, 540, 920, anxious=False)
    for r, alpha in [(180, 70), (260, 44), (340, 28)]:
        draw.ellipse((540 - r, 520 - r, 540 + r, 520 + r), outline=(15, 123, 131, alpha), width=14)
    draw.text((540, 520), "深呼吸", font=font(96, True), fill=TEAL, anchor="mm")


def draw_scene(base: Image.Image, scene: str):
    draw = ImageDraw.Draw(base)
    draw_soft_clinic_bg(base)
    if scene == "word":
        draw_report(draw, 250, 410, 830, 1160, "question")
        draw.rounded_rectangle((225, 1210, 855, 1400), radius=46, fill=(21, 50, 74, 235))
        draw.text((540, 1305), "再検査です", font=font(86, True), fill="white", anchor="mm")
    elif scene == "blank":
        draw_person(draw, 540, 920, anxious=True)
        draw.ellipse((360, 480, 720, 650), fill=(255, 255, 255, 224), outline=(143, 169, 183, 150), width=4)
        draw.text((540, 565), "・・・", font=font(95, True), fill=SLATE, anchor="mm")
    elif scene == "not_confirmed":
        draw_report(draw, 240, 420, 840, 1200, "cross")
    elif scene == "maybe":
        draw_report(draw, 245, 410, 835, 1180, "question")
        draw.text((540, 1325), "もしかしたら…", font=font(78, True), fill=NAVY, anchor="mm")
    elif scene == "contrast":
        draw_scan(draw, 485, 790)
        draw.rounded_rectangle((730, 520, 860, 980), radius=42, fill=(255, 255, 255, 230), outline=TEAL, width=10)
        draw.rectangle((760, 590, 830, 885), fill=MINT)
        draw.line((795, 520, 795, 450), fill=TEAL, width=14)
    elif scene == "yes_no":
        draw_yes_no(draw)
    elif scene == "step":
        draw_steps(draw)
    elif scene == "not_bad":
        draw_report(draw, 245, 420, 835, 1180, "check")
        draw.line((250, 1305, 830, 1305), fill=CORAL, width=18)
        draw.text((540, 1240), "悪い結果", font=font(84, True), fill=CORAL, anchor="mm")
    elif scene == "breath":
        draw_breath(draw)


def add_telop(base: Image.Image, headline: str, body: str, accent: str, y: int):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    box_h = 500
    draw.rounded_rectangle((82, y, 998, y + box_h), radius=46, fill=(9, 39, 62, 236))
    draw.rounded_rectangle((82, y, 998, y + 20), radius=10, fill=accent)

    draw.text((540, y + 72), headline, font=font(40, True), fill=(255, 255, 255, 230), anchor="mm")
    body_f, lines = fit_text(draw, body, 810, 4, 66)
    line_h = body_f.size + 24
    total_h = line_h * len(lines)
    start_y = y + 305 - total_h // 2
    for i, line in enumerate(lines):
        draw.text((540, start_y + i * line_h), line, font=body_f, fill="white", anchor="mm")

    draw.text((540, H - 108), DISCLAIMER, font=font(30, False), fill=(15, 50, 74, 230), anchor="mm")
    base.alpha_composite(overlay)


CUTS = [
    ("01_retest_word.png", "word", "その言葉で", "「再検査です」", CORAL, 1360, 1.8),
    ("02_mind_blank.png", "blank", "不安になりますよね", "その言葉を聞いた瞬間、\n頭が真っ白になる方もいます。", CORAL, 1220, 3.2),
    ("03_not_confirmed.png", "not_confirmed", "でも大丈夫", "再検査は\n“異常が確定した”\nという意味ではありません。", YELLOW, 1200, 3.8),
    ("04_maybe_stage.png", "maybe", "最初の検査では", "「もしかしたら…」という\n段階にしかなりません。", TEAL, 1220, 3.2),
    ("05_contrast_detail.png", "contrast", "より詳しく見るために", "造影剤を使って\nより詳しく見ることで、", TEAL, 1220, 3.0),
    ("06_yes_or_no.png", "yes_no", "ここで判断に近づきます", "はじめて\n「ある」か「ない」かが\nわかります。", GREEN, 1210, 3.5),
    ("07_next_step.png", "step", "つまり", "再検査は、答えを出すための\n次のステップです。", TEAL, 1220, 3.3),
    ("08_not_bad_result.png", "not_bad", "覚えておいてください", "再検査＝悪い結果\nではありません。", YELLOW, 1220, 2.8),
    ("09_breathe.png", "breath", "最後に", "怖い気持ちはわかります。\nでもまず、深呼吸してください。", GREEN, 1220, 3.4),
]


def make_frames():
    FRAMES.mkdir(parents=True, exist_ok=True)
    for name, scene, headline, body, accent, y, _ in CUTS:
        img = gradient_bg("#e8f8f4", "#fff0d0")
        draw_scene(img, scene)
        add_telop(img, headline, body, accent, y)
        img.convert("RGB").save(FRAMES / name, quality=96)


def make_storyboard():
    thumbs = []
    for item in CUTS:
        img = Image.open(FRAMES / item[0]).convert("RGB")
        thumbs.append(img.resize((216, 384), Image.Resampling.LANCZOS))
    board = Image.new("RGB", (216 * 3, 384 * 3), "white")
    for idx, thumb in enumerate(thumbs):
        x = (idx % 3) * 216
        y = (idx // 3) * 384
        board.paste(thumb, (x, y))
    board.save(STORYBOARD, quality=94)


def write_caption():
    (OUT / "script.txt").write_text(
        "「再検査です」\n\n"
        "その言葉を聞いた瞬間、\n"
        "頭が真っ白になる方もいます。\n\n"
        "でも、再検査は\n"
        "\"異常が確定した\"という意味ではありません。\n\n"
        "最初の検査では、\n"
        "「もしかしたら…」という段階にしかなりません。\n\n"
        "造影剤を使ってより詳しく見ることで、\n"
        "はじめて「ある」か「ない」かがわかります。\n\n"
        "つまり再検査は、答えを出すための次のステップです。\n\n"
        "再検査＝悪い結果　ではありません。\n\n"
        "怖い気持ちはわかります。\n"
        "でもまず、深呼吸してください。\n",
        encoding="utf-8",
    )


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    make_frames()
    make_storyboard()
    write_caption()
    print(FRAMES)
    print(STORYBOARD)


if __name__ == "__main__":
    main()
