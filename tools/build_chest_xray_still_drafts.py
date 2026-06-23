from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

ROOT = Path(r"F:\ANRYCAMPANY")
OUT = ROOT / "reel_assets" / "chest_xray_series" / "01_what_it_shows" / "still_drafts_v1"
OUT.mkdir(parents=True, exist_ok=True)

PATIENT = Path(r"C:\Users\maruk\AppData\Local\Temp\codex-clipboard-304888e0-6a6d-4ffa-8192-dc2588ce9791.png")
XRAY_DIR = ROOT / "reel_assets" / "reference_photos" / "equipment" / "20260618" / "chest_radiography"
XRAY_NORMAL = XRAY_DIR / "成人男性　胸写真.jpg"
XRAY_RIB_REMOVED = XRAY_DIR / "肋骨除去.jpg"
RT_FRONT = ROOT / "ANRYCAMPANY" / "Characters" / "RT_TECH_001" / "front.png"

W, H = 1080, 1920


def font(size: int):
    for p in [
        r"C:\Windows\Fonts\meiryob.ttc",
        r"C:\Windows\Fonts\meiryo.ttc",
        r"C:\Windows\Fonts\YuGothB.ttc",
        r"C:\Windows\Fonts\YuGothM.ttc",
    ]:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def cover(im: Image.Image, box, target=(W, H)) -> Image.Image:
    crop = im.crop(box)
    cw, ch = crop.size
    scale = max(target[0] / cw, target[1] / ch)
    nw, nh = round(cw * scale), round(ch * scale)
    resized = crop.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - target[0]) // 2
    top = (nh - target[1]) // 2
    return resized.crop((left, top, left + target[0], top + target[1]))


def soft_canvas(color=(241, 246, 247)):
    im = Image.new("RGB", (W, H), color)
    d = ImageDraw.Draw(im)
    for y in range(H):
        a = y / H
        c = (
            int(color[0] * (1 - a) + 232 * a),
            int(color[1] * (1 - a) + 239 * a),
            int(color[2] * (1 - a) + 240 * a),
        )
        d.line((0, y, W, y), fill=c)
    return im


def save(im: Image.Image, name: str):
    im.convert("RGB").save(OUT / name, quality=95)


def add_vignette(im, opacity=70):
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    mask = Image.new("L", im.size, 0)
    d = ImageDraw.Draw(mask)
    d.rectangle((0, 0, W, H), fill=opacity)
    d.ellipse((-180, -120, W + 180, H + 160), fill=0)
    overlay.putalpha(mask.filter(ImageFilter.GaussianBlur(90)))
    return Image.alpha_composite(im.convert("RGBA"), overlay).convert("RGB")


def rounded_rect(d, xy, r, fill, outline=None, width=1):
    d.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)


patient = Image.open(PATIENT).convert("RGB")
xray = Image.open(XRAY_NORMAL).convert("RGB")
xray_lung = Image.open(XRAY_RIB_REMOVED).convert("RGB")

# 01: corridor waiting, no stretch and no visible equipment.
save(cover(patient, (0, 434, 620, 1536)), "01_patient_corridor_anxious.png")

# 02: quiet waiting feeling, close crop with subdued tone.
im = cover(patient, (0, 320, 760, 1560))
im = ImageEnhance.Color(im).enhance(0.82)
im = ImageEnhance.Brightness(im).enhance(0.97)
im = add_vignette(im, 35)
save(im, "02_patient_waiting_quiet.png")

# 03: reassurance scene without forced character compositing. The patient looks toward an unseen staff member.
im = cover(patient, (0, 250, 640, 1370))
im = ImageEnhance.Brightness(im).enhance(1.04)
im = ImageEnhance.Color(im).enhance(1.02)
save(im, "03_rt_reassurance_no_machine.png")

# 04: approved chest photo concept.
base = soft_canvas((236, 242, 243))
xr = cover(xray, (0, 0, xray.width, xray.height), target=(960, 1180))
base.paste(xr, (60, 470))
d = ImageDraw.Draw(base)
labels = [("肺", "#05b8d8", 132), ("心臓", "#f0a000", 416), ("骨", "#3bd36a", 704)]
for text, color, x in labels:
    rounded_rect(d, (x, 1610, x + 244, 1710), 34, (250, 252, 252), color, 7)
    tw = d.textlength(text, font=font(56))
    d.text((x + (244 - tw) / 2, 1624), text, fill=color, font=font(56))
save(base, "04_chest_xray_lung_heart_bone.png")

# 05: lungs, external-body impression without X-ray as main view.
im = cover(patient, (0, 380, 760, 1450))
ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(ov)
d.ellipse((375, 760, 525, 1000), outline=(0, 185, 216, 190), width=8)
d.ellipse((555, 760, 705, 1000), outline=(0, 185, 216, 190), width=8)
d.line((540, 730, 540, 1010), fill=(0, 185, 216, 170), width=6)
im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
save(im, "05_lung_external_breath.png")

# 06: heart cue, natural chest area focus.
im = cover(patient, (120, 360, 760, 1420))
ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(ov)
d.ellipse((510, 790, 675, 955), outline=(236, 145, 45, 205), width=9)
d.arc((530, 805, 620, 900), 200, 520, fill=(236, 145, 45, 180), width=8)
im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
save(im, "06_heart_chest_focus.png")

# 07: bone, use normal X-ray because bone visibility is the point.
base = soft_canvas((237, 242, 241))
xr = cover(xray, (0, 0, xray.width, xray.height), target=(900, 1260))
base.paste(xr, (90, 430))
d = ImageDraw.Draw(base, "RGBA")
d.rounded_rectangle((150, 500, 930, 760), radius=40, outline=(59, 211, 106, 230), width=10)
d.rounded_rectangle((245, 780, 835, 1410), radius=45, outline=(59, 211, 106, 180), width=8)
save(base, "07_bone_normal_xray_highlight.png")

# 08: one photo, much information, no machine.
base = soft_canvas((235, 241, 242))
xr = cover(xray_lung, (0, 0, xray_lung.width, xray_lung.height), target=(880, 1180))
base.paste(xr, (100, 380))
d = ImageDraw.Draw(base, "RGBA")
for xy, c in [((175, 560, 455, 1030), (0, 185, 216, 210)), ((500, 650, 675, 960), (240, 160, 0, 220)), ((245, 420, 845, 650), (59, 211, 106, 190))]:
    d.rounded_rectangle(xy, radius=36, outline=c, width=9)
save(base, "08_one_photo_many_clues.png")

# 09: after exam, softened expression.
im = cover(patient, (0, 300, 700, 1510))
im = ImageEnhance.Brightness(im).enhance(1.04)
im = ImageEnhance.Color(im).enhance(1.03)
save(im, "09_after_exam_corridor.png")

# 10: relief near window.
im = cover(patient, (0, 180, 700, 1320))
layer = Image.new("RGBA", (W, H), (255, 255, 255, 36))
im = Image.alpha_composite(im.convert("RGBA"), layer).convert("RGB")
save(im, "10_relieved_by_window.png")

# 11-12: CTA backgrounds only, calm and readable.
for name, lines in [
    ("11_cta_info_background.png", ["検査前の不安を", "安心に変える情報を発信中"]),
    ("12_cta_save_background.png", ["あとで見返せるように", "保存しておいてください"]),
]:
    base = soft_canvas((234, 241, 242))
    small = cover(xray, (0, 0, xray.width, xray.height), target=(680, 880))
    small = ImageEnhance.Contrast(small).enhance(0.9)
    base.paste(small, (200, 330))
    veil = Image.new("RGBA", (W, H), (247, 250, 250, 155))
    base = Image.alpha_composite(base.convert("RGBA"), veil).convert("RGB")
    d = ImageDraw.Draw(base)
    y = 1240
    for line in lines:
        tw = d.textlength(line, font=font(58))
        d.text(((W - tw) / 2, y), line, fill=(42, 58, 66), font=font(58))
        y += 92
    save(base, name)

print(OUT)
