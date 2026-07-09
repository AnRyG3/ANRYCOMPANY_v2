from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


W, H = 1920, 1080
ROOT = Path(r"F:\ANRYCAMPANY")
REF = Path(r"C:\Users\maruk\OneDrive\デスクトップ\参考資料")
OUT = ROOT / "reel_assets" / "ct_longform_youtube_samples" / "frames_flow_v2_sample5"
FONT = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

NAVY = (20, 45, 68)
TEAL = (36, 126, 138)
INK = (55, 76, 90)
BG = (238, 246, 246)
WHITE = (255, 255, 255)


def font(size):
    return ImageFont.truetype(str(FONT), size)


def cover(path, size=(W, H), anchor=(0.5, 0.5)):
    img = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    iw, ih = img.size
    sw, sh = size
    scale = max(sw / iw, sh / ih)
    img = img.resize((int(iw * scale), int(ih * scale)), Image.Resampling.LANCZOS)
    rw, rh = img.size
    left = int((rw - sw) * anchor[0])
    top = int((rh - sh) * anchor[1])
    return img.crop((left, top, left + sw, top + sh))


def text_size(draw, text, fnt):
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def center_lines(draw, cx, top, text, fnt, fill=NAVY, gap=16):
    y = top
    for line in text.split("\n"):
        w, h = text_size(draw, line, fnt)
        draw.text((cx - w / 2, y), line, font=fnt, fill=fill)
        y += h + gap
    return y


def label(draw, text):
    f = font(30)
    w, _ = text_size(draw, text, f)
    draw.rounded_rectangle((104, 72, 104 + w + 52, 136), radius=8, fill=(255, 255, 255, 235))
    draw.text((130, 86), text, font=f, fill=TEAL)


def card(draw, box, title, subtitle=None, title_size=66):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=8, fill=(255, 255, 255, 238))
    title_font = font(title_size)
    sub_font = font(34)
    title_lines = title.split("\n")
    title_h = sum(text_size(draw, line, title_font)[1] for line in title_lines) + 16 * (len(title_lines) - 1)
    sub_h = text_size(draw, subtitle, sub_font)[1] if subtitle else 0
    total = title_h + (28 if subtitle else 0) + sub_h
    top = y1 + ((y2 - y1) - total) // 2
    bottom = center_lines(draw, (x1 + x2) / 2, top, title, title_font, NAVY, 16)
    if subtitle:
        w, _ = text_size(draw, subtitle, sub_font)
        draw.text(((x1 + x2 - w) / 2, bottom + 28), subtitle, font=sub_font, fill=INK)


def photo_panel(canvas, path, box, anchor=(0.5, 0.5)):
    x1, y1, x2, y2 = box
    size = (x2 - x1, y2 - y1)
    img = cover(path, size=size, anchor=anchor).convert("RGBA")
    mask = Image.new("L", size, 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((0, 0, size[0], size[1]), radius=8, fill=255)
    shadow = Image.new("RGBA", (size[0] + 30, size[1] + 30), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((15, 15, size[0] + 15, size[1] + 15), radius=8, fill=(0, 0, 0, 55))
    shadow = shadow.filter(ImageFilter.GaussianBlur(11))
    canvas.alpha_composite(shadow, (x1 - 15, y1 - 15))
    canvas.paste(img, (x1, y1), mask)


def soft_bg():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 780, W, H), fill=(224, 235, 235))
    d.rectangle((0, 0, W, 140), fill=(245, 250, 250))
    for x in (360, 720, 1080, 1440):
        d.line((x, 0, x - 80, 780), fill=(226, 236, 236), width=5)
    return img.convert("RGBA")


def frame_01():
    bg = cover(REF / "CT2.JPG").filter(ImageFilter.GaussianBlur(18))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (240, 248, 248)), 0.35).convert("RGBA")
    d = ImageDraw.Draw(bg)
    label(d, "単純CT検査")
    photo_panel(bg, REF / "CT2.JPG", (1050, 140, 1765, 895), anchor=(0.54, 0.5))
    card(d, (120, 290, 930, 735), "明日CT検査を\n受ける方へ", "当日の流れを先に確認します", 74)
    return bg


def draw_reception_scene(title):
    img = soft_bg()
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((900, 260, 1660, 720), radius=8, fill=(250, 252, 250))
    d.rectangle((940, 330, 1620, 690), fill=(232, 222, 202))
    d.rectangle((940, 640, 1620, 700), fill=(205, 188, 160))
    d.rounded_rectangle((1050, 190, 1460, 270), radius=8, fill=(255, 255, 255))
    sign_font = font(42)
    w, _ = text_size(d, title, sign_font)
    d.text((1255 - w / 2, 204), title, font=sign_font, fill=TEAL)
    d.rounded_rectangle((1120, 410, 1440, 560), radius=8, fill=(255, 255, 255))
    d.rectangle((1160, 452, 1400, 474), fill=(138, 167, 184))
    d.rectangle((1160, 500, 1340, 522), fill=(178, 196, 207))
    return img


def frame_02():
    img = soft_bg()
    d = ImageDraw.Draw(img)
    label(d, "検査前")
    for x in (250, 530, 1240, 1520):
        d.rounded_rectangle((x, 630, x + 220, 770), radius=8, fill=(205, 220, 228))
        d.rectangle((x + 18, 760, x + 202, 805), fill=(176, 198, 210))
    d.rounded_rectangle((780, 310, 1140, 460), radius=8, fill=(255, 255, 255, 225))
    d.text((845, 352), "待合", font=font(54), fill=TEAL)
    card(d, (300, 245, 1620, 570), "少し不安でも\n流れがわかると落ち着きます", "まずは病院に着いてからの流れです", 58)
    return img


def frame_03():
    img = draw_reception_scene("受付")
    d = ImageDraw.Draw(img)
    label(d, "受付")
    d.rounded_rectangle((230, 630, 610, 805), radius=8, fill=(255, 255, 255, 235))
    d.text((280, 668), "診察券", font=font(40), fill=TEAL)
    d.rectangle((280, 730, 560, 750), fill=(158, 180, 194))
    card(d, (160, 260, 820, 535), "まずは受付を\n済ませます", "案内に従って進みます", 62)
    return img


def frame_04():
    img = draw_reception_scene("放射線科 受付")
    d = ImageDraw.Draw(img)
    label(d, "待合")
    for x in (190, 440, 690):
        d.rounded_rectangle((x, 655, x + 200, 780), radius=8, fill=(198, 216, 226))
        d.rectangle((x + 20, 770, x + 180, 812), fill=(172, 193, 205))
    d.rounded_rectangle((1040, 340, 1490, 430), radius=8, fill=(232, 246, 246))
    d.text((1090, 358), "CT検査 待合", font=font(42), fill=NAVY)
    card(d, (180, 265, 850, 545), "呼ばれるまで\n待合で待ちます", "受付後、放射線科の案内に従います", 58)
    return img


def frame_05():
    img = Image.open(ROOT / "reel_assets" / "xray_clothing_wrinkles_buttons_v1" / "frame_07_metal_buttons_clothing_v1.png")
    img = ImageOps.exif_transpose(img).convert("RGB")
    bg = ImageOps.fit(img, (W, H), Image.Resampling.LANCZOS, centering=(0.5, 0.48)).filter(ImageFilter.GaussianBlur(10))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (242, 248, 248)), 0.24).convert("RGBA")
    d = ImageDraw.Draw(bg)
    label(d, "服装と金属")
    card(d, (190, 250, 1730, 600), "金属は画像に影響する\nことがあります", "ボタン、ファスナー、アクセサリーなどを確認します", 58)
    return bg


def contact_sheet(paths):
    sheet = Image.new("RGB", (1920, 370), (238, 242, 242))
    d = ImageDraw.Draw(sheet)
    f = font(24)
    for i, p in enumerate(paths):
        im = Image.open(p).resize((384, 216), Image.Resampling.LANCZOS).convert("RGB")
        x = i * 384
        sheet.paste(im, (x, 0))
        d.text((x + 16, 230), p.stem, font=f, fill=NAVY)
    sheet.save(OUT / "contact_sheet_01_05.png", quality=95)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    frames = [frame_01(), frame_02(), frame_03(), frame_04(), frame_05()]
    paths = []
    names = ["opening_ct", "pre_exam_anxiety", "reception", "radiology_waiting", "metal_clothing"]
    for i, (im, name) in enumerate(zip(frames, names), start=1):
        path = OUT / f"frame_{i:02d}_{name}.png"
        im.convert("RGB").save(path, quality=95)
        paths.append(path)
        print(path)
    contact_sheet(paths)
    print(OUT / "contact_sheet_01_05.png")


if __name__ == "__main__":
    main()
