from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "bone_density_series" / "07_bone_density_screening_age"
OUT_DIR = ASSET_DIR / "final_text_frames"
SIZE = (1080, 1920)

FRAMES = [
    ("frame_01_hook_patient_f50_home.png", "骨密度検査って\nいつから受ければいいの？"),
    ("frame_02_young_enough_patient_f50.png", "まだ若いから大丈夫\nそう思っているうちに\n骨は静かに変化しています"),
    ("frame_03_reassurance_rt.png", "大丈夫です\n受けるタイミングを知るだけで\n安心につながります"),
    ("frame_04_forties_patient_f40.png", "女性は40代から意識を\n閉経後は骨密度が\n下がりやすくなります"),
    ("frame_05_recommended_age_no_person.png", "65歳以上の女性\n70歳以上の男性は\nすすめられることがあります"),
    ("frame_06_consult_triggers_rt.png", "年齢に関係なく\nこんな方は相談を"),
    ("frame_07_triggers_still_life.png", "骨折したことがある\n閉経した\n身長が縮んできた"),
    ("frame_08_no_pain_dxa_room.png", "骨粗しょう症は\n痛みがないまま\n進むことがあります"),
    ("frame_09_not_too_early_patient_f50.png", "まだ早いはありません\n知ることが\n骨を守る第一歩"),
    ("frame_10_timing_known_patient_f50.png", "この動画を見たあなたは\n受けるタイミングを\n知っています"),
    ("frame_11_save_cta_rt.png", "検査前の不安を\n安心に変える情報を発信中"),
    ("frame_12_follow_cta_rt.png", "この情報を\nあとで確認できるように\n保存してください"),
]

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\BIZ-UDGothicB.ttc",
    r"C:\Windows\Fonts\YuGothB.ttc",
    r"C:\Windows\Fonts\meiryob.ttc",
    r"C:\Windows\Fonts\BIZ-UDGothicR.ttc",
    r"C:\Windows\Fonts\YuGothM.ttc",
    r"C:\Windows\Fonts\meiryo.ttc",
]


def choose_font(size):
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def cover_to_size(path):
    img = Image.open(path).convert("RGB")
    iw, ih = img.size
    scale = max(SIZE[0] / iw, SIZE[1] / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - SIZE[0]) // 2
    top = (nh - SIZE[1]) // 2
    return img.crop((left, top, left + SIZE[0], top + SIZE[1])).convert("RGBA")


def fit_font(draw, lines, max_width, start_size=72, min_size=38):
    size = start_size
    while size >= min_size:
        font = choose_font(size)
        widths = [
            draw.textbbox((0, 0), line, font=font, stroke_width=2)[2]
            for line in lines
        ]
        if max(widths) <= max_width:
            return font
        size -= 2
    return choose_font(min_size)


def panel_bounds(line_count):
    x1, x2 = 72, 1008
    if line_count <= 2:
        return x1, 150, x2, 410
    return x1, 120, x2, 470


def draw_telop(image, text):
    lines = text.split("\n")
    x1, y1, x2, y2 = panel_bounds(len(lines))

    shadow = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow, "RGBA")
    sd.rounded_rectangle((x1 + 8, y1 + 12, x2 + 8, y2 + 12), 34, fill=(20, 28, 36, 52))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))

    panel = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel, "RGBA")
    pd.rounded_rectangle((x1, y1, x2, y2), 34, fill=(255, 255, 255, 226))
    pd.rounded_rectangle((x1, y1, x2, y2), 34, outline=(230, 237, 240, 220), width=3)

    image = Image.alpha_composite(Image.alpha_composite(image, shadow), panel)
    draw = ImageDraw.Draw(image)
    font = fit_font(draw, lines, x2 - x1 - 100, start_size=72 if len(lines) <= 2 else 62)
    line_h = int(font.size * 1.38)
    total_h = line_h * len(lines)
    y = (y1 + y2) // 2 - total_h // 2 + 4

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=2)
        text_w = bbox[2] - bbox[0]
        x = (SIZE[0] - text_w) // 2
        draw.text(
            (x, y),
            line,
            font=font,
            fill=(24, 49, 63, 255),
            stroke_width=2,
            stroke_fill=(255, 255, 255, 255),
        )
        y += line_h
    return image


def make_contact_sheet(paths):
    thumb_w, thumb_h, label_h = 270, 480, 34
    cols = 4
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (thumb_w * cols, (thumb_h + label_h) * rows), (246, 248, 250))
    draw = ImageDraw.Draw(sheet)
    font = choose_font(18)
    for idx, path in enumerate(paths):
        im = Image.open(path).convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (idx % cols) * thumb_w
        y = (idx // cols) * (thumb_h + label_h)
        sheet.paste(im, (x, y))
        draw.text((x + 8, y + thumb_h + 7), path.name, fill=(30, 40, 50), font=font)
    out = ASSET_DIR / "_contact_sheet_final_text_frames.png"
    sheet.save(out, quality=95)
    return out


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    for idx, (source_name, text) in enumerate(FRAMES, start=1):
        image = cover_to_size(ASSET_DIR / source_name)
        image = draw_telop(image, text)
        out = OUT_DIR / f"frame_{idx:02d}.png"
        image.convert("RGB").save(out, quality=95)
        outputs.append(out)

    contact_sheet = make_contact_sheet(outputs)
    manifest = {
        "title": "骨密度検査、何歳から受ければいい？",
        "asset_dir": str(ASSET_DIR),
        "final_text_frames": [str(path) for path in outputs],
        "contact_sheet": str(contact_sheet),
        "size": {"width": SIZE[0], "height": SIZE[1]},
        "note": "テロップ入り12枚。音声・動画生成は未実施。",
    }
    (OUT_DIR / "frame_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(contact_sheet)


if __name__ == "__main__":
    main()
