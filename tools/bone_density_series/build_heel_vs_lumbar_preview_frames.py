from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reel_assets" / "bone_density_series" / "02_heel_vs_lumbar" / "preview_backgrounds"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1920


def rounded(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def soft_shadow(base, box, radius=40, offset=(0, 14), blur=24, alpha=60):
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    x1, y1, x2, y2 = box
    ox, oy = offset
    sd.rounded_rectangle((x1 + ox, y1 + oy, x2 + ox, y2 + oy), radius=radius, fill=(80, 92, 95, alpha))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(shadow)


def background():
    img = Image.new("RGBA", (W, H), (248, 252, 250, 255))
    d = ImageDraw.Draw(img)
    for y in range(H):
        c = int(252 - y * 10 / H)
        d.line((0, y, W, y), fill=(c, min(255, c + 2), min(255, c + 1), 255))
    d.rectangle((0, 1320, W, H), fill=(238, 244, 240, 255))
    for x in range(-120, W, 120):
        d.line((x, 1320, x + 330, H), fill=(229, 236, 231, 120), width=2)
    d.rectangle((0, 0, W, 290), fill=(252, 254, 253, 255))
    return img


def draw_patient_on_dxa(img, x=225, y=1035, scale=1.0):
    d = ImageDraw.Draw(img)
    # Body on table
    d.ellipse((x + 322, y - 180, x + 404, y - 98), fill=(238, 202, 176, 255))
    d.polygon(
        [(x + 110, y - 92), (x + 610, y - 122), (x + 675, y - 18), (x + 150, y + 22)],
        fill=(224, 233, 245, 255),
    )
    d.line((x + 190, y - 48, x + 625, y - 74), fill=(188, 203, 218, 255), width=5)
    d.polygon([(x + 592, y - 40), (x + 765, y + 42), (x + 745, y + 88), (x + 570, y + 0)], fill=(232, 214, 196, 255))
    d.polygon([(x + 200, y - 15), (x + 88, y + 90), (x + 122, y + 130), (x + 255, y + 18)], fill=(232, 214, 196, 255))
    d.ellipse((x + 750, y + 48, x + 820, y + 88), fill=(235, 214, 193, 255))
    d.ellipse((x + 70, y + 104, x + 138, y + 140), fill=(235, 214, 193, 255))
    # Hair
    d.pieslice((x + 312, y - 188, x + 408, y - 96), 190, 25, fill=(60, 48, 42, 255))


def draw_horizon_like_dxa(img):
    d = ImageDraw.Draw(img)
    # Exam table, long low bed inspired by Horizon-style DXA tables, without logo.
    table = (145, 1030, 970, 1250)
    soft_shadow(img, table, radius=64, offset=(0, 28), blur=30, alpha=70)
    rounded(d, table, 60, (235, 241, 244, 255), outline=(205, 218, 224, 255), width=3)
    rounded(d, (175, 1070, 940, 1190), 44, (248, 251, 252, 255))
    rounded(d, (172, 1218, 943, 1272), 26, (156, 177, 188, 255))
    rounded(d, (210, 1264, 330, 1340), 22, (130, 151, 160, 255))
    rounded(d, (800, 1264, 920, 1340), 22, (130, 151, 160, 255))

    # Overhead scanning arm: simplified Horizon-like moving arm.
    rounded(d, (228, 830, 862, 910), 38, (226, 236, 241, 255), outline=(190, 210, 219, 255), width=3)
    rounded(d, (500, 888, 590, 1088), 36, (215, 228, 235, 255), outline=(186, 204, 213, 255), width=3)
    rounded(d, (420, 1040, 672, 1138), 36, (240, 247, 249, 255), outline=(190, 210, 219, 255), width=3)
    d.ellipse((520, 1074, 572, 1126), fill=(183, 209, 220, 255))

    # Monitor cart
    rounded(d, (760, 720, 1000, 880), 28, (232, 242, 245, 255), outline=(193, 211, 219, 255), width=3)
    rounded(d, (790, 748, 970, 842), 16, (170, 199, 212, 255))
    d.rectangle((870, 880, 900, 1188), fill=(172, 190, 198, 255))
    rounded(d, (805, 1178, 966, 1228), 24, (215, 226, 231, 255), outline=(180, 198, 206, 255), width=2)

    draw_patient_on_dxa(img)


def draw_technologist(img):
    d = ImageDraw.Draw(img)
    x, y = 78, 760
    d.ellipse((x + 58, y, x + 168, y + 110), fill=(235, 199, 174, 255))
    d.pieslice((x + 46, y - 6, x + 174, y + 118), 180, 360, fill=(56, 47, 42, 255))
    rounded(d, (x + 30, y + 108, x + 202, y + 415), 44, (255, 255, 255, 255), outline=(218, 228, 232, 255), width=2)
    d.polygon([(x + 68, y + 122), (x + 118, y + 180), (x + 168, y + 122)], fill=(225, 238, 243, 255))
    d.line((x + 116, y + 180, x + 116, y + 396), fill=(220, 230, 234, 255), width=3)
    d.polygon([(x + 196, y + 180), (x + 278, y + 300), (x + 246, y + 330), (x + 178, y + 228)], fill=(248, 248, 248, 255))


def frame_dxa_room():
    img = background()
    draw_horizon_like_dxa(img)
    draw_technologist(img)
    d = ImageDraw.Draw(img)
    # Caption-safe translucent guide area, intentionally visual only, no text.
    rounded(d, (150, 310, 930, 655), 44, (255, 255, 255, 38))
    return img.convert("RGB")


def frame_comparison():
    img = background()
    d = ImageDraw.Draw(img)
    # Left heel device
    soft_shadow(img, (80, 1050, 455, 1325), radius=52, offset=(0, 20), blur=24, alpha=50)
    rounded(d, (80, 1050, 455, 1325), 52, (230, 235, 236, 255), outline=(198, 210, 215, 255), width=3)
    rounded(d, (118, 1088, 418, 1240), 34, (251, 253, 253, 255))
    rounded(d, (232, 1150, 388, 1222), 24, (168, 178, 184, 255))
    d.polygon([(230, 1140), (348, 1094), (410, 1130), (366, 1210), (230, 1210)], fill=(236, 210, 188, 255))
    d.ellipse((212, 1180, 260, 1216), fill=(236, 210, 188, 255))

    # Right DXA table miniature
    soft_shadow(img, (552, 1032, 1012, 1240), radius=56, offset=(0, 20), blur=24, alpha=50)
    rounded(d, (552, 1032, 1012, 1240), 54, (235, 241, 244, 255), outline=(205, 218, 224, 255), width=3)
    rounded(d, (590, 1072, 976, 1175), 32, (248, 251, 252, 255))
    rounded(d, (620, 912, 945, 970), 30, (226, 236, 241, 255), outline=(190, 210, 219, 255), width=3)
    rounded(d, (765, 956, 828, 1078), 28, (215, 228, 235, 255), outline=(186, 204, 213, 255), width=3)
    d.polygon([(620, 1094), (900, 1078), (946, 1130), (656, 1160)], fill=(224, 233, 245, 255))
    d.ellipse((780, 1040, 832, 1092), fill=(238, 202, 176, 255))

    # Middle comparison mark, no text.
    d.line((500, 980, 500, 1370), fill=(202, 218, 220, 255), width=4)
    d.ellipse((466, 1156, 534, 1224), fill=(180, 211, 218, 255))
    d.line((482, 1190, 518, 1190), fill=(255, 255, 255, 255), width=6)
    d.line((500, 1172, 500, 1208), fill=(255, 255, 255, 255), width=6)
    rounded(d, (130, 310, 950, 650), 44, (255, 255, 255, 42))
    return img.convert("RGB")


def main():
    frames = {
        "preview_07_horizon_like_dxa_room.png": frame_dxa_room(),
        "preview_10_heel_vs_horizon_like_dxa_comparison.png": frame_comparison(),
    }
    for name, img in frames.items():
        img.save(OUT / name, quality=95)
    sheet = Image.new("RGB", (W * 2, H), (245, 248, 247))
    sheet.paste(frames["preview_07_horizon_like_dxa_room.png"], (0, 0))
    sheet.paste(frames["preview_10_heel_vs_horizon_like_dxa_comparison.png"], (W, 0))
    sheet = sheet.resize((1080, 960))
    sheet.save(OUT / "_contact_sheet_horizon_preview.png", quality=95)


if __name__ == "__main__":
    main()
