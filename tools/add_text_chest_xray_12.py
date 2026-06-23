from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(r"F:\ANRYCAMPANY")
OUT = ROOT / "reel_assets" / "chest_xray_series" / "01_what_it_shows" / "text_frames_v1"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1920

sources = [
    r"C:\Users\maruk\AppData\Local\Temp\codex-clipboard-7ed569f6-db7d-436d-bdaa-562dd4bca581.png",
    r"C:\Users\maruk\AppData\Local\Temp\codex-clipboard-5f0040be-8fee-44c7-8dc4-cecd871f38a5.png",
    r"C:\Users\maruk\AppData\Local\Temp\codex-clipboard-ce0224fe-074b-4d5c-bbe0-7af0ea3229ee.png",
    r"C:\Users\maruk\AppData\Local\Temp\codex-clipboard-9d58adfd-fbd3-47d3-8626-e36f31efc6dd.png",
    r"C:\Users\maruk\AppData\Local\Temp\codex-clipboard-57cddca3-077f-4f0b-9776-127078314e13.png",
    r"C:\Users\maruk\AppData\Local\Temp\codex-clipboard-516d2096-9700-4d03-85c3-099497ae1913.png",
    r"C:\Users\maruk\AppData\Local\Temp\codex-clipboard-79b67b96-5b53-462e-bbbc-b26c3ddabb3d.png",
    r"C:\Users\maruk\AppData\Local\Temp\codex-clipboard-825de2de-aebf-4d9d-a054-28648922da94.png",
    r"C:\Users\maruk\AppData\Local\Temp\codex-clipboard-b4d5d916-296c-4a2f-86c2-1b692c72ba42.png",
    r"C:\Users\maruk\AppData\Local\Temp\codex-clipboard-1aa452a5-6f7b-4a02-a90a-a96c74abfaff.png",
    r"C:\Users\maruk\AppData\Local\Temp\codex-clipboard-1dc12049-a324-4e6c-af76-e27370ba5f3e.png",
    r"C:\Users\maruk\AppData\Local\Temp\codex-clipboard-1dc12049-a324-4e6c-af76-e27370ba5f3e.png",
]

texts = [
    ["レントゲン、", "何か見つかったら", "どうしよう…"],
    ["検査室に入るとき、", "そう思ったことは", "ありませんか？"],
    ["その不安、", "おかしくないです。"],
    ["胸のレントゲンは", "主に3つを見ています。", "肺・心臓・骨です。"],
    ["肺では、", "影や白く見える部分が", "ないかを確認します。"],
    ["心臓では、", "大きさや形を", "確認します。"],
    ["骨では、", "肋骨や背骨の状態も", "確認できます。"],
    ["1枚の写真から、", "多くの情報を", "確認できます。"],
    ["何を見てもらっているか", "わかると、", "少し気持ちが楽になります。"],
    ["異常が見つかることが", "怖いのは当然です。"],
    ["でも、見つけるための", "検査だから、", "受けてよかったと思える日が来ます。"],
    ["あとで見返せるように", "保存しておいてください"],
]


def font(size: int):
    for p in [
        r"C:\Windows\Fonts\meiryob.ttc",
        r"C:\Windows\Fonts\YuGothB.ttc",
        r"C:\Windows\Fonts\meiryo.ttc",
    ]:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def fit_cover(im: Image.Image) -> Image.Image:
    im = im.convert("RGB")
    sw, sh = im.size
    scale = max(W / sw, H / sh)
    nw, nh = round(sw * scale), round(sh * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    return im.crop(((nw - W) // 2, (nh - H) // 2, (nw + W) // 2, (nh + H) // 2))


def wrap_lines(lines, max_width, start_size=72, min_size=48):
    size = start_size
    while size >= min_size:
        f = font(size)
        if all(ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(line, font=f) <= max_width for line in lines):
            return f, size
        size -= 2
    return font(min_size), min_size


def add_text(im: Image.Image, lines, idx: int) -> Image.Image:
    im = fit_cover(im)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    top = idx in {0, 1, 2, 8}
    center = idx in {9, 10, 11}
    y0 = 170 if top else (760 if center else 170)
    max_width = 880
    f, size = wrap_lines(lines, max_width)
    line_h = int(size * 1.35)
    block_h = line_h * len(lines)
    pad_x, pad_y = 46, 36

    widths = [d.textlength(line, font=f) for line in lines]
    box_w = int(max(widths) + pad_x * 2)
    box_h = int(block_h + pad_y * 2)
    x0 = (W - box_w) // 2
    y0 = min(y0, H - box_h - 120)

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x0 + 8, y0 + 8, x0 + box_w + 8, y0 + box_h + 8), radius=22, fill=(0, 0, 0, 90))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    overlay = Image.alpha_composite(overlay, shadow)
    d = ImageDraw.Draw(overlay)
    d.rounded_rectangle((x0, y0, x0 + box_w, y0 + box_h), radius=22, fill=(255, 255, 255, 218))

    y = y0 + pad_y
    for line in lines:
        tw = d.textlength(line, font=f)
        d.text(((W - tw) / 2, y), line, font=f, fill=(28, 42, 50))
        y += line_h

    return Image.alpha_composite(im.convert("RGBA"), overlay).convert("RGB")


for i, (src, lines) in enumerate(zip(sources, texts), start=1):
    im = Image.open(src)
    out = add_text(im, lines, i - 1)
    out.save(OUT / f"{i:02d}.png", quality=95)

print(OUT)
