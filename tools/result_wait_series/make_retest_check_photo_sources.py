from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter


ROOT = Path(r"F:\ANRYCAMPANY")
OUT = ROOT / "reel_assets" / "retest_check_02_photo_sources"
FRAMES = OUT / "frames"
STORYBOARD = OUT / "storyboard_photo_sources.png"

W, H = 1080, 1920

CONSULT = ROOT / "codex_generated_images" / "019e5088-44b1-7801-a0b7-7413bae5eaf7" / "ig_0cf8f13b3253eea2016a108a6c01708191be5b139936913990.png"
WAIT_ROOT = ROOT / "reel_assets" / "result_wait_series" / "01_result_wait_mri_ct" / "sources"


def cover(img: Image.Image, zoom: float = 1.0, x_bias: float = 0.5, y_bias: float = 0.5) -> Image.Image:
    img = img.convert("RGB")
    scale = max(W / img.width, H / img.height) * zoom
    nw, nh = int(img.width * scale), int(img.height * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = int((nw - W) * x_bias)
    top = int((nh - H) * y_bias)
    left = max(0, min(left, nw - W))
    top = max(0, min(top, nh - H))
    return img.crop((left, top, left + W, top + H))


def grade(img: Image.Image, warmth: float = 1.0, contrast: float = 1.0, brightness: float = 1.0) -> Image.Image:
    img = ImageEnhance.Color(img).enhance(warmth)
    img = ImageEnhance.Contrast(img).enhance(contrast)
    img = ImageEnhance.Brightness(img).enhance(brightness)
    return img


def caption_safe_overlay(img: Image.Image, top_dark: bool = False, bottom_dark: bool = True) -> Image.Image:
    base = img.convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    if top_dark:
        for y in range(0, 720):
            alpha = int(92 * (1 - y / 720))
            draw.line((0, y, W, y), fill=(7, 24, 38, alpha))
    if bottom_dark:
        for y in range(980, H):
            alpha = int(128 * ((y - 980) / (H - 980)))
            draw.line((0, y, W, y), fill=(7, 24, 38, alpha))
    base.alpha_composite(overlay)
    return base.convert("RGB")


def soft_focus(img: Image.Image, amount: float = 0.18) -> Image.Image:
    blur = img.filter(ImageFilter.GaussianBlur(7))
    return Image.blend(img, blur, amount)


CUTS = [
    {
        "name": "01_retest_word_photo.png",
        "src": CONSULT,
        "zoom": 1.00,
        "x": 0.50,
        "y": 0.50,
        "note": "診察室で説明を受ける場面。導入「再検査です」用。",
    },
    {
        "name": "02_mind_blank_photo.png",
        "src": WAIT_ROOT / "02_waiting_area.png",
        "zoom": 1.04,
        "x": 0.48,
        "y": 0.38,
        "blur": 0.10,
        "note": "待合で書類を見る患者。不安・頭が真っ白になる場面。",
    },
    {
        "name": "03_not_confirmed_photo.png",
        "src": CONSULT,
        "zoom": 1.12,
        "x": 0.50,
        "y": 0.72,
        "note": "医師の説明と書類。異常確定ではない説明用。",
    },
    {
        "name": "04_maybe_stage_photo.png",
        "src": WAIT_ROOT / "01_after_exam.png",
        "zoom": 1.05,
        "x": 0.52,
        "y": 0.36,
        "note": "検査後に結果を待つ雰囲気。「もしかしたら」の段階用。",
    },
    {
        "name": "05_contrast_detail_photo.png",
        "src": WAIT_ROOT / "03_radiologist.png",
        "zoom": 1.00,
        "x": 0.50,
        "y": 0.50,
        "cool": True,
        "note": "画像を詳しく確認する場面。造影剤で詳しく見る説明用。",
    },
    {
        "name": "06_yes_or_no_photo.png",
        "src": WAIT_ROOT / "04_doctor_judgement.png",
        "zoom": 1.00,
        "x": 0.50,
        "y": 0.50,
        "cool": True,
        "note": "医療者が判断材料を確認する場面。「ある/ない」がわかる説明用。",
    },
    {
        "name": "07_next_step_photo.png",
        "src": WAIT_ROOT / "03_radiologist.png",
        "zoom": 1.18,
        "x": 0.62,
        "y": 0.54,
        "cool": True,
        "note": "モニター寄り。答えを出す次のステップ用。",
    },
    {
        "name": "08_not_bad_result_photo.png",
        "src": WAIT_ROOT / "05_closing.png",
        "zoom": 1.02,
        "x": 0.50,
        "y": 0.40,
        "note": "落ち着いた締め前。悪い結果ではない説明用。",
    },
    {
        "name": "09_breathe_photo.png",
        "src": WAIT_ROOT / "02_waiting_area.png",
        "zoom": 1.12,
        "x": 0.56,
        "y": 0.46,
        "warm": True,
        "blur": 0.06,
        "note": "少し落ち着いた待合。深呼吸してください、の締め用。",
    },
]


def make_frames():
    FRAMES.mkdir(parents=True, exist_ok=True)
    notes = []
    for idx, cut in enumerate(CUTS, start=1):
        img = cover(Image.open(cut["src"]), cut["zoom"], cut["x"], cut["y"])
        if cut.get("cool"):
            img = grade(img, warmth=0.86, contrast=1.04, brightness=0.98)
        elif cut.get("warm"):
            img = grade(img, warmth=1.08, contrast=0.98, brightness=1.02)
        else:
            img = grade(img, warmth=1.00, contrast=1.02, brightness=1.00)
        if cut.get("blur"):
            img = soft_focus(img, cut["blur"])
        img = caption_safe_overlay(img, top_dark=False, bottom_dark=True)
        out = FRAMES / cut["name"]
        img.save(out, quality=96)
        notes.append(f"{idx:02d}. {cut['name']} - {cut['note']}")
    (OUT / "usage_notes.txt").write_text("\n".join(notes) + "\n", encoding="utf-8")


def make_storyboard():
    thumbs = []
    for cut in CUTS:
        img = Image.open(FRAMES / cut["name"]).convert("RGB")
        thumbs.append(img.resize((216, 384), Image.Resampling.LANCZOS))
    board = Image.new("RGB", (216 * 3, 384 * 3), "white")
    for idx, thumb in enumerate(thumbs):
        x = (idx % 3) * 216
        y = (idx // 3) * 384
        board.paste(thumb, (x, y))
    board.save(STORYBOARD, quality=94)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    make_frames()
    make_storyboard()
    print(FRAMES)
    print(STORYBOARD)


if __name__ == "__main__":
    main()
