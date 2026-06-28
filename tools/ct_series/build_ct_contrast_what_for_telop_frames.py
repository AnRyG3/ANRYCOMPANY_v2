from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "ct_series" / "ct_contrast_what_for_v1"
SRC_DIR = ASSET_DIR / "frames"
OUT_DIR = ASSET_DIR / "telop_frames"
CONTACT_SHEET = ASSET_DIR / "contact_sheet_telop_frames.png"

W, H = 1080, 1920
FONT_BOLD = r"C:\Windows\Fonts\YuGothB.ttc"
FONT_REG = r"C:\Windows\Fonts\YuGothM.ttc"

NAVY = (7, 31, 60, 238)
WHITE = (255, 255, 255, 255)
ACCENT = (79, 153, 193, 245)


FRAMES = [
    {
        "src": "S01_home_appointment.png",
        "out": "S01_home_appointment_telop.png",
        "lines": ["造影剤を使うと言われて", "不安になっていませんか？"],
        "box": (88, 150, 992, 370),
    },
    {
        "src": "S02_reassured_patient.png",
        "out": "S02_reassured_patient_telop.png",
        "lines": ["造影剤は", "CTをより正確にする薬"],
        "box": (92, 150, 940, 355),
    },
    {
        "src": "S03_ct_room_wide.png",
        "out": "S03_ct_room_wide_telop.png",
        "lines": ["血管や組織の見え方が", "より鮮明に"],
        "box": (90, 155, 990, 360),
    },
    {
        "src": "S04_ct_monitor.png",
        "out": "S04_ct_monitor_telop.png",
        "lines": ["判断しにくい部分を", "はっきり確認するため"],
        "box": (90, 150, 990, 355),
    },
    {
        "src": "S05_iv_line.png",
        "out": "S05_iv_line_telop.png",
        "lines": ["腕の静脈から注射", "点滴と同じイメージ"],
        "box": (90, 145, 930, 350),
    },
    {
        "src": "S06_on_ct_table.png",
        "out": "S06_on_ct_table_telop.png",
        "lines": ["体が温かくなることも", "異常ではありません"],
        "box": (90, 145, 970, 350),
    },
    {
        "src": "S07_control_room.png",
        "out": "S07_control_room_telop.png",
        "lines": ["医師や診療放射線技師が", "状態を確認しています"],
        "box": (80, 135, 1000, 342),
    },
    {
        "src": "S08_doctor_explanation.png",
        "out": "S08_doctor_explanation_telop.png",
        "lines": ["造影が必要＝", "より正確に確認したい判断"],
        "box": (90, 145, 990, 355),
    },
    {
        "src": "S09_empty_corridor.png",
        "out": "S09_empty_corridor_telop.png",
        "lines": ["毎日多くの方が受ける", "よくある検査です"],
        "box": (90, 145, 990, 355),
    },
    {
        "src": "S10_window_reassured.png",
        "out": "S10_window_reassured_telop.png",
        "lines": ["不安に感じるのは", "おかしくありません"],
        "box": (90, 145, 950, 350),
    },
    {
        "src": "S11_next_preview_phone.png",
        "out": "S11_next_preview_phone_telop.png",
        "lines": ["次回", "絶食や水分制限はなぜ？"],
        "box": (96, 145, 960, 355),
        "accent_label": "NEXT",
    },
    {
        "src": "S12_cta_phone_hands.png",
        "out": "S12_cta_phone_hands_telop.png",
        "lines": ["保存とフォローで", "次の投稿も見られます"],
        "box": (92, 145, 980, 355),
        "accent_label": "CHECK",
    },
]


def font(size: int, bold: bool = True):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def cover_resize(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")
    scale = max(W / img.width, H / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - W) // 2
    top = (nh - H) // 2
    return resized.crop((left, top, left + W, top + H))


def text_bbox(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont):
    return draw.multiline_textbbox((0, 0), text, font=fnt, spacing=16, align="center")


def fit_font(draw: ImageDraw.ImageDraw, text: str, max_w: int, max_h: int):
    size = 74
    while size >= 42:
        fnt = font(size, True)
        box = text_bbox(draw, text, fnt)
        if box[2] - box[0] <= max_w and box[3] - box[1] <= max_h:
            return fnt
        size -= 2
    return font(42, True)


def add_vignette(base: Image.Image):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, W, 430), fill=(255, 255, 255, 18))
    draw.rectangle((0, H - 300, W, H), fill=(0, 0, 0, 28))
    base.alpha_composite(overlay)


def draw_telop(base: Image.Image, item: dict):
    x0, y0, x1, y1 = item["box"]
    text = "\n".join(item["lines"])
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x0 + 8, y0 + 10, x1 + 8, y1 + 10), radius=38, fill=(0, 0, 0, 75))
    shadow = shadow.filter(ImageFilter.GaussianBlur(9))
    base.alpha_composite(shadow)

    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle((x0, y0, x1, y1), radius=38, fill=NAVY)
    draw.rounded_rectangle((x0, y0, x1, y0 + 14), radius=7, fill=ACCENT)

    label = item.get("accent_label")
    top_pad = 42
    if label:
        label_font = font(30, False)
        draw.text((x0 + 52, y0 + 44), label, font=label_font, fill=(255, 255, 255, 218), anchor="lm")
        top_pad = 70

    fnt = fit_font(draw, text, (x1 - x0) - 88, (y1 - y0) - top_pad - 34)
    bbox = text_bbox(draw, text, fnt)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (x0 + x1) // 2
    ty = y0 + top_pad + ((y1 - y0 - top_pad) - th) // 2
    draw.multiline_text(
        (tx, ty),
        text,
        font=fnt,
        fill=WHITE,
        anchor="ma",
        align="center",
        spacing=16,
    )
    base.alpha_composite(overlay)


def make_contact_sheet(paths: list[Path]):
    cols = 4
    thumb_w, thumb_h = 216, 384
    label_h = 36
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (245, 247, 250))
    label_font = ImageFont.load_default()
    for idx, path in enumerate(paths):
        img = Image.open(path).convert("RGB")
        img.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), "white")
        tile.paste(img, ((thumb_w - img.width) // 2, 0))
        ImageDraw.Draw(tile).text((8, thumb_h + 10), path.name[:32], fill=(0, 0, 0), font=label_font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
    sheet.save(CONTACT_SHEET, quality=94)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    for item in FRAMES:
        src = SRC_DIR / item["src"]
        out = OUT_DIR / item["out"]
        img = cover_resize(Image.open(src)).convert("RGBA")
        add_vignette(img)
        draw_telop(img, item)
        img.convert("RGB").save(out, quality=95)
        outputs.append(out)

    make_contact_sheet(outputs)
    manifest = {
        "title": "造影剤って何のために使うの？",
        "size": {"width": W, "height": H},
        "source_dir": str(SRC_DIR),
        "output_dir": str(OUT_DIR),
        "contact_sheet": str(CONTACT_SHEET),
        "frames": [
            {"source": item["src"], "output": str(OUT_DIR / item["out"]), "telop": item["lines"]}
            for item in FRAMES
        ],
    }
    (OUT_DIR / "telop_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8-sig",
    )
    print(OUT_DIR)
    print(CONTACT_SHEET)


if __name__ == "__main__":
    main()
