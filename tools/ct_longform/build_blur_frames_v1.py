from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


W, H = 1920, 1080
ROOT = Path(r"F:\ANRYCAMPANY")
REF = Path(r"C:\Users\maruk\OneDrive\デスクトップ\参考資料")
SRC = ROOT / "reel_assets" / "ct_longform_youtube_samples"
OUT = SRC / "frames_blur_v1"
FONT = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

NAVY = (21, 45, 68)
TEAL = (36, 126, 138)
INK = (54, 74, 88)
WHITE = (255, 255, 255)


def load_font(size):
    return ImageFont.truetype(str(FONT), size)


def cover(img, size=(W, H), anchor=(0.5, 0.5)):
    img = ImageOps.exif_transpose(img).convert("RGB")
    sw, sh = size
    iw, ih = img.size
    scale = max(sw / iw, sh / ih)
    resized = img.resize((int(iw * scale), int(ih * scale)), Image.Resampling.LANCZOS)
    rw, rh = resized.size
    left = int((rw - sw) * anchor[0])
    top = int((rh - sh) * anchor[1])
    return resized.crop((left, top, left + sw, top + sh))


def rounded_mask(size, radius):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
    return mask


def fit_inside(img, box_size):
    img = ImageOps.exif_transpose(img).convert("RGB")
    bw, bh = box_size
    iw, ih = img.size
    scale = min(bw / iw, bh / ih)
    out = img.resize((int(iw * scale), int(ih * scale)), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", box_size, (245, 248, 248))
    x = (bw - out.size[0]) // 2
    y = (bh - out.size[1]) // 2
    canvas.paste(out, (x, y))
    return canvas


def make_bg(path, anchor=(0.5, 0.5), blur=18):
    base = cover(Image.open(path), anchor=anchor).filter(ImageFilter.GaussianBlur(blur))
    wash = Image.new("RGB", (W, H), (245, 250, 250))
    base = Image.blend(base, wash, 0.34).convert("RGBA")
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(shade)
    for y in range(H):
        alpha = int(44 * (y / H))
        d.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
    return Image.alpha_composite(base, shade)


def text_size(draw, text, font):
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def draw_center_text(draw, center_x, y, text, font, fill=NAVY, line_gap=18):
    lines = text.split("\n")
    heights = []
    widths = []
    for line in lines:
        w, h = text_size(draw, line, font)
        widths.append(w)
        heights.append(h)
    total_h = sum(heights) + line_gap * (len(lines) - 1)
    cy = y - total_h // 2
    for line, w, h in zip(lines, widths, heights):
        draw.text((center_x - w // 2, cy), line, font=font, fill=fill)
        cy += h + line_gap


def measure_lines(draw, text, font, line_gap):
    lines = text.split("\n")
    boxes = [draw.textbbox((0, 0), line, font=font) for line in lines]
    widths = [box[2] - box[0] for box in boxes]
    heights = [box[3] - box[1] for box in boxes]
    total_h = sum(heights) + line_gap * (len(lines) - 1)
    return lines, widths, heights, total_h


def draw_lines_center(draw, center_x, top, text, font, fill=NAVY, line_gap=14):
    lines, widths, heights, _ = measure_lines(draw, text, font, line_gap)
    y = top
    for line, width, height in zip(lines, widths, heights):
        draw.text((center_x - width // 2, y), line, font=font, fill=fill)
        y += height + line_gap
    return y


def draw_lines_left(draw, x, top, text, font, fill=NAVY, line_gap=14):
    lines = text.split("\n")
    y = top
    for line in lines:
        _, height = text_size(draw, line, font)
        draw.text((x, y), line, font=font, fill=fill)
        y += height + line_gap
    return y


def wrap_text(draw, text, font, max_width):
    lines = []
    current = ""
    for ch in text:
        test = current + ch
        if text_size(draw, test, font)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = ch
    if current:
        lines.append(current)
    return "\n".join(lines)


def draw_badge(draw, text, x=104, y=74):
    font = load_font(32)
    w, h = text_size(draw, text, font)
    draw.rounded_rectangle((x, y, x + w + 52, y + 64), radius=8, fill=(255, 255, 255, 232))
    draw.text((x + 26, y + 13), text, font=font, fill=TEAL)


def draw_card(draw, box, title, subtitle=None, title_size=70, subtitle_size=34, align="center"):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=8, fill=(255, 255, 255, 236))
    title_font = load_font(title_size)
    sub_font = load_font(subtitle_size)
    if align == "center":
        title_gap = 16
        sub_gap = 10
        _, _, _, title_h = measure_lines(draw, title, title_font, title_gap)
        wrapped = wrap_text(draw, subtitle, sub_font, x2 - x1 - 120) if subtitle else ""
        sub_h = measure_lines(draw, wrapped, sub_font, sub_gap)[3] if wrapped else 0
        total_h = title_h + (24 if wrapped else 0) + sub_h
        top = y1 + max(34, ((y2 - y1) - total_h) // 2)
        after_title = draw_lines_center(draw, (x1 + x2) // 2, top, title, title_font, NAVY, title_gap)
        if subtitle:
            draw_lines_center(draw, (x1 + x2) // 2, after_title + 24, wrapped, sub_font, INK, sub_gap)
    else:
        after_title = draw_lines_left(draw, x1 + 52, y1 + 42, title, title_font, NAVY, 14)
        if subtitle:
            wrapped = wrap_text(draw, subtitle, sub_font, x2 - x1 - 104)
            draw.multiline_text((x1 + 52, after_title + 18), wrapped, font=sub_font, fill=INK, spacing=12)


def paste_photo(canvas, path, box, mode="cover", anchor=(0.5, 0.5)):
    x1, y1, x2, y2 = box
    size = (x2 - x1, y2 - y1)
    img = cover(Image.open(path), size=size, anchor=anchor) if mode == "cover" else fit_inside(Image.open(path), size)
    img = img.convert("RGBA")
    mask = rounded_mask(size, 8)
    shadow = Image.new("RGBA", (size[0] + 28, size[1] + 28), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((14, 14, size[0] + 14, size[1] + 14), radius=8, fill=(0, 0, 0, 54))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    canvas.alpha_composite(shadow, (x1 - 14, y1 - 14))
    canvas.paste(img, (x1, y1), mask)


def make_frame(idx, spec):
    bg_path = spec.get("bg", REF / "CT2.JPG")
    img = make_bg(bg_path, anchor=spec.get("bg_anchor", (0.5, 0.5)), blur=spec.get("blur", 18))
    draw = ImageDraw.Draw(img)
    draw_badge(draw, spec["section"])

    if "photo" in spec:
        paste_photo(img, spec["photo"], spec.get("photo_box", (1050, 150, 1776, 890)), spec.get("photo_mode", "cover"), spec.get("photo_anchor", (0.5, 0.5)))

    draw_card(
        draw,
        spec.get("card", (120, 650, 1800, 900)),
        spec["title"],
        spec.get("subtitle"),
        spec.get("title_size", 68),
        spec.get("subtitle_size", 34),
        spec.get("align", "center"),
    )

    if spec.get("note"):
        note_font = load_font(26)
        note = spec["note"]
        w, _ = text_size(draw, note, note_font)
        draw.rounded_rectangle((128, 934, 164 + w, 986), radius=8, fill=(255, 255, 255, 215))
        draw.text((146, 944), note, font=note_font, fill=INK)

    out_path = OUT / f"frame_{idx:02d}_{spec['slug']}.png"
    img.convert("RGB").save(out_path, quality=95)
    return out_path


def make_contact_sheet(paths):
    thumbs = []
    for p in paths:
        im = Image.open(p).resize((384, 216), Image.Resampling.LANCZOS).convert("RGB")
        thumbs.append((p, im))
    sheet_w = 384 * 4
    sheet_h = 260 * 5
    sheet = Image.new("RGB", (sheet_w, sheet_h), (238, 242, 242))
    d = ImageDraw.Draw(sheet)
    f = load_font(22)
    for i, (p, im) in enumerate(thumbs):
        x = (i % 4) * 384
        y = (i // 4) * 260
        sheet.paste(im, (x, y))
        d.text((x + 14, y + 224), p.stem[:30], font=f, fill=NAVY)
    sheet.save(OUT / "contact_sheet_frames_01_20.png", quality=95)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ct1 = REF / "CT1.JPG"
    ct2 = REF / "CT2.JPG"
    ct3 = REF / "CT3.JPG"
    ct4 = REF / "CT4.JPG"
    pov_room = SRC / "patient_pov_ct_room_still.jpg"
    pov_table = SRC / "pov1_table_11s.jpg"
    pov_gantry = SRC / "pov3_gantry_32s.jpg"

    specs = [
        {"section": "単純CT検査", "slug": "opening", "bg": ct2, "photo": ct2, "photo_box": (1040, 138, 1760, 894), "title": "明日CT検査を\n受ける方へ", "subtitle": "流れがわかると、少し落ち着けます", "card": (112, 278, 915, 735), "title_size": 74, "subtitle_size": 32, "note": "※今回は造影剤を使わないCT検査のご案内です"},
        {"section": "はじめに", "slug": "flow_reason", "bg": ct3, "photo": ct3, "title": "何をする検査か\n先に見ておきましょう", "subtitle": "受付から検査終了、会計まで順番に確認します", "card": (116, 610, 1804, 870)},
        {"section": "受付と準備", "slug": "reception", "bg": ct4, "photo": ct4, "photo_box": (1080, 130, 1768, 860), "title": "まずは受付と準備", "subtitle": "案内に従って、検査の受付や待合へ向かいます", "card": (116, 660, 980, 892), "align": "left"},
        {"section": "服装と金属", "slug": "metal_check", "bg": ct1, "title": "金属は画像に影響する\nことがあります", "subtitle": "ボタン、ファスナー、ホック、アクセサリーなどは確認されることがあります", "card": (170, 320, 1750, 760)},
        {"section": "服装と金属", "slug": "change_clothes", "bg": ct2, "title": "検査する場所によっては\n検査着に着替えます", "subtitle": "迷ったら、その場でスタッフに確認して大丈夫です", "card": (210, 338, 1710, 750)},
        {"section": "検査室へ", "slug": "enter_room", "bg": pov_room, "photo": pov_room, "photo_box": (1030, 136, 1772, 890), "title": "検査室へ入ります", "subtitle": "装置は大きく見えますが、検査の流れはシンプルです", "card": (118, 664, 988, 896), "align": "left"},
        {"section": "CT装置", "slug": "donut_shape", "bg": ct1, "photo": ct1, "photo_box": (1034, 106, 1768, 896), "title": "長いトンネルではなく\n輪の中を通ります", "subtitle": "寝台がゆっくり動いて撮影します", "card": (114, 318, 945, 686)},
        {"section": "寝台へ", "slug": "on_table", "bg": ct3, "photo": ct3, "photo_box": (1018, 128, 1774, 890), "title": "検査台に寝て\n位置を合わせます", "subtitle": "きれいな画像を撮るために大切な準備です", "card": (116, 632, 980, 888), "align": "left"},
        {"section": "撮影中", "slug": "table_moves", "bg": pov_table, "photo": pov_table, "photo_box": (1080, 140, 1746, 884), "title": "寝台がゆっくり動きます", "subtitle": "体に何かが触れたり、押されたりする検査ではありません", "card": (112, 660, 1010, 900), "align": "left"},
        {"section": "息止め", "slug": "breath_hold", "bg": ct2, "title": "息止めは、\nがんばりすぎなくて大丈夫", "subtitle": "ふだんの深呼吸くらいで、すっと吸って止めます", "card": (210, 320, 1710, 760)},
        {"section": "息止め", "slug": "breath_tip", "bg": ct3, "title": "すっと吸って、止める", "subtitle": "力を入れすぎると、かえって体が動きやすくなることがあります", "card": (220, 330, 1700, 750)},
        {"section": "検査終了", "slug": "finish", "bg": ct1, "photo": ct1, "photo_box": (1068, 124, 1762, 886), "title": "終わったら、\nゆっくり起き上がります", "subtitle": "必要があれば着替えて、案内に従って進みます", "card": (116, 636, 1002, 892), "align": "left"},
        {"section": "検査時間", "slug": "short_exam", "bg": ct2, "title": "思っていたより早かった、\nという方も多い検査です", "subtitle": "撮影そのものは短く、位置合わせや確認の時間が多くなります", "card": (180, 318, 1740, 760)},
        {"section": "よくある疑問", "slug": "radiation_zero", "bg": ct4, "title": "被ばくがゼロでは\nありません", "subtitle": "CTはX線を使う検査です。心配な点は検査前に相談できます", "card": (220, 318, 1700, 760)},
        {"section": "被ばく", "slug": "doctor_judges", "bg": ct3, "title": "必要性を医師が判断して\n行う検査です", "subtitle": "症状や診察内容から、体の中を詳しく確認する必要があるときに選ばれます", "card": (190, 310, 1730, 770)},
        {"section": "被ばく", "slug": "consult", "bg": ct1, "title": "心配なことは、\n検査前に相談してください", "subtitle": "妊娠の可能性や、最近のCT検査が気になる場合も相談できます", "card": (190, 318, 1730, 760)},
        {"section": "費用", "slug": "cost", "bg": ct2, "title": "3割負担で\n5,000円〜7,000円前後が目安", "subtitle": "検査部位、診察料、ほかの検査の有無で変わります", "card": (185, 310, 1735, 770), "title_size": 62, "subtitle_size": 34, "note": "※費用は医療機関や当日の内容によって変わります"},
        {"section": "結果", "slug": "result_timing", "bg": ct4, "title": "結果説明のタイミングは\n病院によって違います", "subtitle": "当日説明される場合も、次回診察で説明される場合もあります", "card": (200, 318, 1720, 760)},
        {"section": "結果", "slug": "reading_flow", "bg": ct4, "title": "放射線科医の読影\n＋\n主治医の総合判断", "subtitle": "施設によって流れは異なりますが、画像や報告書などを合わせて説明されます", "card": (240, 268, 1680, 820), "title_size": 62},
        {"section": "まとめ", "slug": "ending", "bg": ct2, "photo": ct2, "photo_box": (1120, 116, 1774, 722), "title": "検査を受ける方は、\nどうぞ落ち着いて\nいってらっしゃい", "subtitle": "検査前の不安を、少しでも軽く", "card": (116, 228, 1010, 800), "title_size": 58, "subtitle_size": 32, "note": "右側はYouTube終了画面にも使いやすい余白として残せます"},
    ]
    paths = [make_frame(i, spec) for i, spec in enumerate(specs, 1)]
    make_contact_sheet(paths)
    for path in paths:
        print(path)
    print(OUT / "contact_sheet_frames_01_20.png")


if __name__ == "__main__":
    main()
