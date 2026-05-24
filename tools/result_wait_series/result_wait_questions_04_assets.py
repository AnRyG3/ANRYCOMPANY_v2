from pathlib import Path
from shutil import copy2
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
OUT = ROOT / "reel_assets" / "result_wait_series" / "04_questions"
NO_TEXT = OUT / "01_no_text"
SHORT_TEXT = OUT / "03_short_text"
GUIDE = OUT / "02_text_safe_guide"

FONT_CANDIDATES = [
    Path(r"C:\Windows\Fonts\YuGothB.ttc"),
    Path(r"C:\Windows\Fonts\YuGothM.ttc"),
    Path(r"C:\Windows\Fonts\meiryo.ttc"),
    Path(r"C:\Windows\Fonts\msgothic.ttc"),
]

SOURCE_DIR = Path(r"C:\Users\maruk\.codex\generated_images\019e595e-55dc-7311-a4a8-52a74813f503")

SOURCE_BY_TIME = [
    "ig_000eae47dcccb371016a12c8b6c3a48191a946b158d004d707.png",
    "ig_000eae47dcccb371016a12c90b2a4481918c3f495b024de536.png",
    "ig_000eae47dcccb371016a12c9576a28819188f04cc1889dc6b3.png",
    "ig_000eae47dcccb371016a12c9a3a25081919ae35c9825a47856.png",
    "ig_000eae47dcccb371016a12c9f425d8819191c0bf725418cc80.png",
    "ig_000eae47dcccb371016a12ca3a4314819194a178829237c470.png",
    "ig_000eae47dcccb371016a12ca83e174819194d0e8b26218b835.png",
    "ig_000eae47dcccb371016a12cadb7ae881918d741e342d26e181.png",
    "ig_000eae47dcccb371016a12cb3d85548191bd5858c5e7886db5.png",
    "ig_000eae47dcccb371016a12cbffd72481918c2c8321ce9167d9.png",
    "ig_000eae47dcccb371016a12cc9c2c348191acca2e2f076bae20.png",
]

# Generated order was based on the first draft. This maps it to the revised finale script.
CUTS = [
    (1, "01_forget_questions", 0, "質問が飛ぶ"),
    (2, "02_nervous_is_natural", 7, "あたりまえ"),
    (3, "03_write_questions", 1, "メモしておく"),
    (4, "04_abnormality", 2, "異常の有無"),
    (5, "05_future_course", 3, "経過の見通し"),
    (6, "06_revisit_timing", 4, "再診の目安"),
    (7, "07_daily_life", 5, "生活の注意"),
    (8, "08_four_questions", 6, "4つを持つ"),
    (9, "09_one_memo", 8, "メモ1枚で"),
    (10, "10_series_closing", 9, "安心して帰れる"),
    (11, "11_follow_cta", 10, "次の検査にも"),
]

SCRIPT = [
    ("01_forget_questions.png", "診察室に入ると、\n聞きたいことが飛んでしまうことがあります。"),
    ("02_nervous_is_natural.png", "それは、緊張や不安のせいで\nあたりまえに起きることです。"),
    ("03_write_questions.png", "だから、事前に\n質問をメモしておきましょう。"),
    ("04_abnormality.png", "まず、異常があるかどうか。\n白黒はっきりさせます。"),
    ("05_future_course.png", "今後どうなるか、\n経過の見通し。"),
    ("06_revisit_timing.png", "いつ再診すればいいか、\n目安。"),
    ("07_daily_life.png", "生活で気をつけることが\nあるか。"),
    ("08_four_questions.png", "この4つを持っていくと、\nあとから不安になりにくくなります。"),
    ("09_one_memo.png", "メモ1枚あるだけで、\n診察室での安心感が変わります。"),
    ("10_series_closing.png", "検査を受けた人が、\n少しでも安心して帰れますように。"),
    ("11_follow_cta.png", "フォローしておくと、\n次の検査のときにまた役立てます。"),
]

PROMPT_NOTES = [
    "同じ40代前後の日本人女性。短い黒髪、白ブラウス、ベージュカーディガン、紺パンツ、紺の肩掛けバッグ。",
    "実写寄り。現代的な日本のクリニック。暖色ベージュ、やわらかい自然光。図解、アイコン、赤い警告表現は避ける。",
    "縦9:16。下中央にCapCut用テロップの安全域を残す。最上部、最下部、右端に重要要素を置かない。",
    "画像内文字は入れない。書類やノートの文字は読めないようにする。",
]

IMAGE_PROMPTS = [
    ("01_forget_questions.png", "診察室に入る同じ女性。医師の手元が少し見え、緊張で聞きたいことが飛んでしまった表情。下中央にテロップ余白。文字なし。"),
    ("02_nervous_is_natural.png", "同じ女性がノートを持ち、少し不安そうに考えている。緊張や不安が自然に伝わるが、煽らない表情。文字なし。"),
    ("03_write_questions.png", "同じ女性が診察前に小さなノートへ質問を書いている。ノートの文字は読めない。下中央に余白。文字なし。"),
    ("04_abnormality.png", "同じ女性が診察室で医師に向き合い、異常の有無を確認するようにノートを持って聞いている。医師は脇役。文字なし。"),
    ("05_future_course.png", "同じ女性が医師の説明を聞きながら、今後の経過について確認している。落ち着いた相談場面。文字なし。"),
    ("06_revisit_timing.png", "同じ女性が再診の目安を聞いている。医師がやさしくジェスチャーし、女性は真剣に聞く。文字なし。"),
    ("07_daily_life.png", "同じ女性が生活で気をつけることをメモしている。日常の注意を確認する落ち着いた雰囲気。文字なし。"),
    ("08_four_questions.png", "同じ女性が待合で結果用紙とノートを持ち、4つを聞けて少し安心した表情。文字なし。"),
    ("09_one_memo.png", "同じ女性がノートを胸元に持ち、メモ1枚で診察室に入りやすくなる安心感を表す。文字なし。"),
    ("10_series_closing.png", "同じ女性が診察後にクリニックを出る。検査後に少し安心して帰るシリーズ最終回の温かい締め。文字なし。"),
    ("11_follow_cta.png", "同じ女性が待合で穏やかにカメラ方向を見る。次の検査のときにも役立つアカウントとしてフォローを促す締め。文字なし。"),
]


def font(size: int) -> ImageFont.FreeTypeFont:
    for candidate in FONT_CANDIDATES:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size, index=0)
    return ImageFont.load_default()


def rounded_rectangle(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_centered_text(draw, xy, lines, image_width, main_font, small_font=None):
    x, y = xy
    line_gap = 22
    total_h = 0
    metrics = []
    for i, line in enumerate(lines):
        f = small_font if small_font and i == 0 and len(lines) > 1 else main_font
        bbox = draw.textbbox((0, 0), line, font=f)
        h = bbox[3] - bbox[1]
        w = bbox[2] - bbox[0]
        metrics.append((line, f, w, h))
        total_h += h
    total_h += line_gap * (len(lines) - 1)
    cy = y - total_h / 2
    for line, f, w, h in metrics:
        draw.text((image_width / 2 - w / 2, cy), line, font=f, fill=(255, 255, 255))
        cy += h + line_gap


def add_short_text(src: Path, dest: Path, label: str):
    im = Image.open(src).convert("RGBA")
    w, h = im.size
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    box_w = int(w * 0.78)
    box_h = int(h * 0.145)
    x0 = (w - box_w) // 2
    y0 = int(h * 0.66)
    x1 = x0 + box_w
    y1 = y0 + box_h
    rounded_rectangle(draw, (x0, y0, x1, y1), 20, fill=(12, 35, 48, 226), outline=(240, 244, 247, 230), width=3)
    draw.rounded_rectangle((x0, y0 - 8, x1, y0 + 9), radius=10, fill=(244, 206, 72, 255))

    tiny = font(28)
    main = font(72 if len(label) <= 7 else 64)
    draw_centered_text(draw, (w / 2, y0 + box_h / 2), ["知っておきたいこと", label], w, main, tiny)
    Image.alpha_composite(im, overlay).convert("RGB").save(dest, quality=95)


def storyboard(image_paths, dest, columns=4):
    thumbs = []
    for path in image_paths:
        im = Image.open(path).convert("RGB")
        im.thumbnail((360, 640), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (360, 640), (245, 245, 245))
        canvas.paste(im, ((360 - im.width) // 2, (640 - im.height) // 2))
        thumbs.append(canvas)
    rows = (len(thumbs) + columns - 1) // columns
    board = Image.new("RGB", (columns * 360, rows * 640), (232, 232, 232))
    for idx, thumb in enumerate(thumbs):
        x = (idx % columns) * 360
        y = (idx // columns) * 640
        board.paste(thumb, (x, y))
    board.save(dest, quality=92)


def write_text_assets():
    (OUT / "final_script.txt").write_text(
        "\n\n".join(f"{i + 1}. {text}" for i, (_, text) in enumerate(SCRIPT)),
        encoding="utf-8-sig",
    )
    (OUT / "short_text_keywords.txt").write_text(
        "\n".join(f"{file}: {label}" for file, label in zip([s[0] for s in SCRIPT], [c[3] for c in CUTS])),
        encoding="utf-8-sig",
    )
    (OUT / "image_prompt_notes.txt").write_text("\n".join(f"- {line}" for line in PROMPT_NOTES), encoding="utf-8-sig")
    (OUT / "image_prompts_by_cut.txt").write_text(
        "\n\n".join(f"{file}\n{prompt}" for file, prompt in IMAGE_PROMPTS),
        encoding="utf-8-sig",
    )
    (OUT / "caption_and_cta.txt").write_text(
        "投稿タイトル:\n結果を聞くとき、何を質問すればいいか\n\n"
        "説明文:\n"
        "検査結果を聞く場面では、緊張や不安で聞きたいことが飛んでしまうことがあります。\n"
        "結果を聞く前に、異常の有無、今後の経過、再診の目安、生活で気をつけることをメモしておくと、あとから不安になりにくくなります。\n\n"
        "検査を受けた人が、少しでも安心して帰れますように。\n"
        "私は診療放射線技師です。個別の検査結果や症状については、医師・医療機関へご相談ください。\n\n"
        "CTA:\n"
        "次の検査のときに見返せるように、フォローして保存しておいてください。\n",
        encoding="utf-8-sig",
    )


def main():
    for folder in [OUT, NO_TEXT, SHORT_TEXT, GUIDE]:
        folder.mkdir(parents=True, exist_ok=True)

    no_text_paths = []
    short_text_paths = []
    for cut_no, slug, source_idx, keyword in CUTS:
        src = SOURCE_DIR / SOURCE_BY_TIME[source_idx]
        dest_name = f"{cut_no:02d}_{slug}.png"
        no_text_dest = NO_TEXT / dest_name
        copy2(src, no_text_dest)
        no_text_paths.append(no_text_dest)
        add_short_text(no_text_dest, SHORT_TEXT / dest_name, keyword)
        add_short_text(no_text_dest, GUIDE / dest_name, keyword)
        short_text_paths.append(SHORT_TEXT / dest_name)

    storyboard(no_text_paths, OUT / "storyboard_no_text.png")
    storyboard(short_text_paths, OUT / "storyboard_short_text.png")
    write_text_assets()


if __name__ == "__main__":
    main()
