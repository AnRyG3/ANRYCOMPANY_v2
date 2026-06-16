from pathlib import Path
import json
import math
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "bone_density_series" / "06_yam70_meaning"
BG_DIR = ASSET_DIR / "backgrounds"
FRAME_DIR = ASSET_DIR / "final_text_frames"
WORK_DIR = ASSET_DIR / "_video_work"
AUDIO_DIR = ASSET_DIR / "audio"
FINAL_DIR = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
OUT = ASSET_DIR / "骨密度の結果_YAM70って何.mp4"
FINAL_OUT = FINAL_DIR / "骨密度の結果_YAM70って何.mp4"

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
SIZE = (1080, 1920)

CHAR_DIR = ROOT / "ANRYCAMPANY" / "Characters"
RT = CHAR_DIR / "RT_TECH_001" / "front.png"
RT_SMILE = CHAR_DIR / "RT_TECH_001" / "expressions" / "warm_smile.png"
DOCTOR = CHAR_DIR / "DOCTOR_001" / "front.png"
PATIENT = CHAR_DIR / "PATIENT_F50_001" / "front.png"

SLIDES = [
    "YAM70%って\n大丈夫なの?",
    "YAM70%…?\n数字だけ見ると不安",
    "大丈夫。\n意味を知れば落ち着けます",
    "YAMは\n若年成人平均値",
    "80%以上 正常\n70〜80% 骨量減少\n70%未満 骨粗しょう症",
    "70%は\n境界ラインです",
    "年齢・体型・生活習慣も\n含めて総合判断",
    "焦る気持ちは\nおかしくありません",
    "要精密検査なら\n整形外科へ",
    "検査を受けた行動は\n正解です",
    "あとで見返せるように\n保存してください",
    "骨密度シリーズは続きます\nフォローして待っていてください",
]

NARRATION = [
    "骨密度の検査結果、数字を見て不安になっていませんか。",
    "YAM70パーセントって書いてあるけど、これって大丈夫なの。そう感じる方もいます。",
    "大丈夫です。その数字には、ちゃんと意味があります。",
    "YAMとは、若年成人平均値のこと。20歳から44歳の骨密度を100パーセントとした比較です。",
    "80パーセント以上は正常。70から80パーセントは骨量減少。70パーセント未満は骨粗しょう症とされます。",
    "70パーセントという数字は、骨粗しょう症の境界ラインです。",
    "でも、数字だけで全てが決まるわけではありません。年齢、体型、生活習慣も含めて、医師が総合判断します。",
    "結果を見て焦る気持ち、おかしくないです。でも数字の意味を知ると、少し落ち着きませんか。",
    "結果に、要精密検査や骨粗しょう症と書いてあった方は、整形外科への受診をおすすめします。",
    "検査を受けたあなたの行動は、正解です。",
    "この動画、あとで見返せるように保存しておいてください。",
    "骨密度シリーズは続きます。フォローして待っていてください。",
]

PROMPTS = [
    "PATIENT_F50_001 sitting at a desk, holding a medical result paper, slightly worried.",
    "Close-up of PATIENT_F50_001 looking down at a result paper, thought bubble YAM70%.",
    "RT_TECH_001 facing camera with calm reassuring smile, one hand raised.",
    "RT_TECH_001 pointing to an explanation of YAM and 20-44 years old equals 100%.",
    "Clean chart showing 80% or more normal, 70-80% reduced bone mass, under 70% osteoporosis.",
    "Close-up of a result paper with 70% highlighted in red marker.",
    "DOCTOR_001 speaking calmly to PATIENT_F50_001 with age, body type, lifestyle cues.",
    "PATIENT_F50_001 slightly relieved, hand on chest, lightening background.",
    "RT_TECH_001 pointing toward a hospital direction sign labeled orthopedics.",
    "PATIENT_F50_001 standing upright with gentle confident smile, holding result paper.",
    "RT_TECH_001 gesturing toward a save bookmark icon.",
    "RT_TECH_001 smiling and waving, follow CTA mood with channel logo placeholder.",
]

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\YuGothB.ttc",
    r"C:\Windows\Fonts\meiryob.ttc",
    r"C:\Windows\Fonts\YuGothM.ttc",
    r"C:\Windows\Fonts\meiryo.ttc",
]


def run(cmd):
    subprocess.run([str(part) for part in cmd], check=True)


def choose_font(size, bold=True):
    paths = FONT_CANDIDATES if bold else FONT_CANDIDATES[2:] + FONT_CANDIDATES[:2]
    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def rounded_rect(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def gradient(top, bottom):
    img = Image.new("RGB", SIZE, top)
    px = img.load()
    for y in range(SIZE[1]):
        t = y / (SIZE[1] - 1)
        color = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        for x in range(SIZE[0]):
            px[x, y] = color
    return img.convert("RGBA")


def add_floor(img, y=1260):
    layer = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.rectangle((0, y, SIZE[0], SIZE[1]), fill=(240, 244, 246, 255))
    for i in range(9):
        yy = y + i * 72
        draw.line((0, yy, SIZE[0], yy - 34), fill=(218, 226, 231, 85), width=2)
    return Image.alpha_composite(img, layer)


def person(path, height):
    img = Image.open(path).convert("RGBA")
    scale = height / img.height
    return img.resize((int(img.width * scale), height), Image.Resampling.LANCZOS)


def paste_shadow(base, fg, xy, shadow=True):
    x, y = xy
    if shadow:
        mask = fg.getchannel("A").filter(ImageFilter.GaussianBlur(12))
        if mask.getextrema()[0] < 250:
            sh = Image.new("RGBA", fg.size, (0, 0, 0, 52))
            sh.putalpha(mask)
            base.alpha_composite(sh, (x + 18, y + 24))
    base.alpha_composite(fg, (x, y))


def draw_paper(draw, box, title="骨密度検査 結果", yam="YAM 70%"):
    x1, y1, x2, y2 = box
    rounded_rect(draw, box, 22, (255, 255, 255, 245), (220, 226, 230), 3)
    font_title = choose_font(36)
    font_body = choose_font(54)
    font_small = choose_font(28, bold=False)
    draw.text((x1 + 34, y1 + 30), title, font=font_title, fill=(44, 58, 70))
    draw.line((x1 + 28, y1 + 90, x2 - 28, y1 + 90), fill=(220, 226, 230), width=3)
    draw.text((x1 + 44, y1 + 134), yam, font=font_body, fill=(28, 54, 72))
    draw.text((x1 + 44, y1 + 222), "判定: 医師の総合判断", font=font_small, fill=(91, 104, 112))


def speech_bubble(draw, box, text):
    x1, y1, x2, y2 = box
    rounded_rect(draw, box, 36, (255, 255, 255, 240), (215, 224, 230), 3)
    draw.polygon([(x1 + 90, y2 - 8), (x1 + 136, y2 + 56), (x1 + 190, y2 - 8)], fill=(255, 255, 255, 240))
    font = choose_font(58)
    bbox = draw.textbbox((0, 0), text, font=font)
    draw.text(((x1 + x2 - bbox[2]) / 2, (y1 + y2 - bbox[3]) / 2 - 2), text, font=font, fill=(36, 54, 67))


def draw_chart(draw, x, y, w):
    rows = [
        ("80%以上", "正常", (76, 173, 112)),
        ("70〜80%", "骨量減少", (222, 175, 60)),
        ("70%未満", "骨粗しょう症", (207, 83, 76)),
    ]
    font_l = choose_font(48)
    font_r = choose_font(42)
    for i, (left, right, color) in enumerate(rows):
        yy = y + i * 168
        rounded_rect(draw, (x, yy, x + w, yy + 118), 26, (255, 255, 255, 242), (222, 228, 232), 2)
        rounded_rect(draw, (x + 28, yy + 28, x + 238, yy + 90), 18, color + (255,), None)
        draw.text((x + 54, yy + 36), left, font=font_l, fill=(255, 255, 255))
        draw.text((x + 300, yy + 36), "→ " + right, font=font_r, fill=(38, 55, 67))


def create_backgrounds():
    BG_DIR.mkdir(parents=True, exist_ok=True)
    rt = person(RT_SMILE if RT_SMILE.exists() else RT, 980)
    rt_big = person(RT_SMILE if RT_SMILE.exists() else RT, 1250)
    patient = person(PATIENT, 1120)
    patient_big = person(PATIENT, 1420)
    doctor = person(DOCTOR, 1180)

    outputs = []
    for idx in range(1, 13):
        img = gradient((236, 247, 252), (255, 250, 239))
        img = add_floor(img)
        draw = ImageDraw.Draw(img)

        if idx == 1:
            draw.rounded_rectangle((120, 1180, 960, 1330), 30, fill=(203, 180, 146, 255))
            paste_shadow(img, patient, (110, 510))
            draw_paper(draw, (590, 790, 990, 1115))
        elif idx == 2:
            crop = patient_big.crop((120, 0, min(patient_big.width, 760), 1000))
            paste_shadow(img, crop, (220, 500))
            speech_bubble(draw, (210, 245, 870, 430), "YAM70%…?")
            draw_paper(draw, (235, 1225, 845, 1585), yam="YAM 70%")
        elif idx == 3:
            paste_shadow(img, rt_big, (230, 500))
            speech_bubble(draw, (155, 230, 925, 430), "大丈夫です")
        elif idx == 4:
            paste_shadow(img, rt, (70, 660))
            rounded_rect(draw, (420, 520, 1000, 1060), 34, (255, 255, 255, 235), (222, 229, 233), 3)
            draw.text((470, 575), "YAM =", font=choose_font(58), fill=(29, 54, 72))
            draw.text((470, 660), "若年成人平均値", font=choose_font(50), fill=(29, 54, 72))
            rounded_rect(draw, (480, 800, 940, 900), 22, (227, 242, 249, 255), None)
            draw.text((525, 823), "20〜44歳 = 100%", font=choose_font(38), fill=(37, 87, 111))
            draw.line((500, 980, 930, 980), fill=(75, 146, 178), width=12)
            for x in (500, 930):
                draw.ellipse((x - 14, 966, x + 14, 994), fill=(75, 146, 178))
        elif idx == 5:
            rounded_rect(draw, (110, 445, 970, 1088), 42, (250, 252, 253, 245), (225, 232, 236), 3)
            draw_chart(draw, 180, 550, 720)
        elif idx == 6:
            rounded_rect(draw, (170, 455, 910, 1230), 32, (255, 255, 255, 255), (218, 224, 229), 4)
            draw.text((230, 535), "骨密度検査 結果", font=choose_font(50), fill=(42, 58, 70))
            draw.line((225, 625, 855, 625), fill=(222, 228, 232), width=4)
            draw.text((260, 760), "YAM", font=choose_font(68), fill=(50, 66, 77))
            draw.text((470, 742), "70%", font=choose_font(112), fill=(38, 55, 67))
            draw.ellipse((430, 700, 815, 895), outline=(220, 62, 60), width=14)
            draw.line((250, 1060, 820, 1060), fill=(230, 235, 238), width=6)
            draw.line((250, 1130, 760, 1130), fill=(230, 235, 238), width=6)
        elif idx == 7:
            paste_shadow(img, doctor, (80, 580))
            paste_shadow(img, patient, (610, 700))
            rounded_rect(draw, (305, 1140, 775, 1265), 26, (255, 255, 255, 225), (223, 230, 234), 2)
            for i, label in enumerate(["年齢", "体型", "生活"]):
                cx = 375 + i * 150
                draw.ellipse((cx - 38, 1170, cx + 38, 1246), fill=(229, 244, 248, 255), outline=(94, 151, 176), width=3)
                draw.text((cx - 28, 1190), label[0], font=choose_font(34), fill=(43, 92, 115))
        elif idx == 8:
            img = gradient((229, 236, 243), (255, 246, 225))
            img = add_floor(img)
            draw = ImageDraw.Draw(img)
            paste_shadow(img, patient_big, (230, 455))
            draw.ellipse((735, 300, 1115, 680), fill=(255, 240, 178, 70))
        elif idx == 9:
            paste_shadow(img, rt, (80, 660))
            rounded_rect(draw, (485, 540, 955, 705), 28, (255, 255, 255, 245), (210, 222, 230), 3)
            draw.text((555, 585), "整形外科", font=choose_font(58), fill=(34, 58, 74))
            draw.polygon([(895, 622), (815, 570), (815, 674)], fill=(72, 147, 177))
            draw.rectangle((660, 705, 745, 1325), fill=(210, 220, 226))
        elif idx == 10:
            img = gradient((255, 244, 214), (242, 249, 252))
            img = add_floor(img)
            draw = ImageDraw.Draw(img)
            paste_shadow(img, patient_big, (260, 405))
            draw_paper(draw, (640, 1040, 990, 1335), yam="YAM 70%")
        elif idx == 11:
            paste_shadow(img, rt_big, (105, 480))
            rounded_rect(draw, (710, 550, 920, 780), 44, (255, 255, 255, 245), (214, 226, 232), 3)
            draw.line((760, 610, 760, 735), fill=(61, 125, 154), width=16)
            draw.line((870, 610, 870, 735), fill=(61, 125, 154), width=16)
            draw.line((760, 610, 870, 610), fill=(61, 125, 154), width=16)
            draw.polygon([(760, 735), (815, 685), (870, 735)], fill=(61, 125, 154))
            draw.ellipse((650, 500, 980, 830), outline=(255, 213, 91, 160), width=12)
        elif idx == 12:
            paste_shadow(img, rt_big, (205, 500))
            rounded_rect(draw, (735, 315, 1010, 425), 28, (255, 255, 255, 235), (212, 224, 230), 2)
            draw.text((775, 344), "ANRY", font=choose_font(44), fill=(55, 103, 126))

        out = BG_DIR / f"bg_{idx:02d}_no_text.png"
        img.convert("RGB").save(out, quality=95)
        outputs.append(out)
    return outputs


def text_box(idx):
    if idx in {6, 7, 9, 10}:
        return (76, 1350, 1004, 1685)
    return (76, 170, 1004, 535)


def fit_font(draw, lines, max_width, start_size, min_size=34):
    size = start_size
    while size >= min_size:
        font = choose_font(size)
        if all(draw.textbbox((0, 0), line, font=font)[2] <= max_width for line in lines):
            return font
        size -= 2
    return choose_font(min_size)


def draw_text_panel(image, text, box, start_size=76):
    x1, y1, x2, y2 = box
    shadow = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x1 + 8, y1 + 12, x2 + 8, y2 + 12), 36, fill=(22, 32, 40, 45))
    shadow = shadow.filter(ImageFilter.GaussianBlur(16))
    panel = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rounded_rectangle(box, 36, fill=(255, 255, 255, 220))
    image = Image.alpha_composite(Image.alpha_composite(image, shadow), panel)
    draw = ImageDraw.Draw(image)
    lines = text.split("\n")
    font = fit_font(draw, lines, 830, start_size)
    line_h = int(font.size * 1.34)
    total_h = line_h * len(lines)
    y = (y1 + y2) // 2 - total_h // 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        x = (SIZE[0] - (bbox[2] - bbox[0])) // 2
        draw.text((x + 3, y + 3), line, font=font, fill=(255, 255, 255, 165))
        draw.text((x, y), line, font=font, fill=(28, 46, 60, 255))
        y += line_h
    return image


def make_frames():
    FRAME_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    for idx, text in enumerate(SLIDES, start=1):
        image = Image.open(BG_DIR / f"bg_{idx:02d}_no_text.png").convert("RGBA")
        start = 78
        if idx in {5, 7, 12}:
            start = 64
        image = draw_text_panel(image, text, text_box(idx), start)
        out = FRAME_DIR / f"frame_{idx:02d}.png"
        image.convert("RGB").save(out, quality=95)
        outputs.append(out)
    make_contact_sheet(outputs, ASSET_DIR / "_contact_sheet_final_text_frames.png")
    return outputs


def make_contact_sheet(paths, out):
    thumb_w, thumb_h = 270, 480
    label_h = 34
    cols = 4
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (thumb_w * cols, (thumb_h + label_h) * rows), (245, 247, 250))
    draw = ImageDraw.Draw(sheet)
    font = choose_font(20)
    for idx, path in enumerate(paths):
        im = Image.open(path).convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (idx % cols) * thumb_w
        y = (idx // cols) * (thumb_h + label_h)
        sheet.paste(im, (x, y))
        draw.text((x + 8, y + thumb_h + 7), path.name, fill=(30, 40, 50), font=font)
    sheet.save(out, quality=95)


def find_bgm():
    for name in ("Kind_Heart.mp3", "healing_wind.mp3"):
        candidates = list(ROOT.rglob(name))
        if candidates:
            return candidates[0]
    raise FileNotFoundError("BGM mp3 not found")


def post_json(path, params=None, payload=None):
    query = urllib.parse.urlencode(params or {})
    url = f"{VOICEVOX}{path}"
    if query:
        url += f"?{query}"
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    if body is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.read()


def synthesize_voice(text, out):
    query = json.loads(post_json("/audio_query", {"text": text, "speaker": SPEAKER}))
    query["speedScale"] = 1.20
    query["pitchScale"] = 0.0
    query["intonationScale"] = 0.95
    query["volumeScale"] = 1.0
    query["prePhonemeLength"] = 0.08
    query["postPhonemeLength"] = 0.14
    out.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path):
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def build_video(frames):
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    bgm = find_bgm()
    required = [FFMPEG, bgm, RT, DOCTOR, PATIENT, *frames]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)

    padded_wavs = []
    durations = []
    min_durations = [3.0, 3.8, 2.7, 4.4, 5.8, 3.4, 5.5, 4.4, 4.6, 3.2, 3.4, 3.6]
    for idx, text in enumerate(NARRATION, start=1):
        voice = AUDIO_DIR / f"voice_{idx:02d}.wav"
        padded = WORK_DIR / f"voice_{idx:02d}_padded.wav"
        synthesize_voice(text, voice)
        duration = max(min_durations[idx - 1], wav_duration(voice) + 0.42)
        durations.append(duration)
        run([
            FFMPEG,
            "-y",
            "-i",
            voice,
            "-af",
            f"apad=pad_dur={duration:.3f},atrim=duration={duration:.3f}",
            "-ar",
            "44100",
            "-ac",
            "2",
            padded,
        ])
        padded_wavs.append(padded)

    frames_txt = WORK_DIR / "frames.txt"
    with frames_txt.open("w", encoding="utf-8") as f:
        for frame, duration in zip(frames, durations):
            f.write(f"file '{frame.as_posix()}'\n")
            f.write(f"duration {duration:.3f}\n")
        f.write(f"file '{frames[-1].as_posix()}'\n")

    voice_txt = WORK_DIR / "voice_segments.txt"
    with voice_txt.open("w", encoding="utf-8") as f:
        for wav in padded_wavs:
            f.write(f"file '{wav.as_posix()}'\n")

    silent = WORK_DIR / "silent.mp4"
    voice_all = AUDIO_DIR / "voice.wav"
    run([
        FFMPEG,
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        frames_txt,
        "-vf",
        "scale=1080:1920,format=yuv420p",
        "-r",
        "30",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        silent,
    ])
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", voice_txt, "-c", "copy", voice_all])
    run([
        FFMPEG,
        "-y",
        "-i",
        silent,
        "-i",
        voice_all,
        "-stream_loop",
        "-1",
        "-i",
        bgm,
        "-filter_complex",
        "[1:a]volume=1.45[voice];[2:a]volume=-26dB[bgm];"
        "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=1:normalize=0,"
        "alimiter=limit=0.95[a]",
        "-map",
        "0:v",
        "-map",
        "[a]",
        "-shortest",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        OUT,
    ])
    shutil.copy2(OUT, FINAL_OUT)
    return bgm, durations


def write_manifest(frames, bgm, durations):
    manifest = {
        "title": "骨密度の結果、YAM70%って何？",
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": "1.20x",
        "bgm": str(bgm),
        "narration": NARRATION,
        "slide_text": SLIDES,
        "image_prompts_source": PROMPTS,
        "durations_seconds": [round(value, 3) for value in durations],
        "total_seconds": round(sum(durations), 3),
        "backgrounds": [str(BG_DIR / f"bg_{idx:02d}_no_text.png") for idx in range(1, 13)],
        "frames": [str(path) for path in frames],
        "asset_video": str(OUT),
        "final_video": str(FINAL_OUT),
    }
    (ASSET_DIR / "video_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main():
    create_backgrounds()
    frames = make_frames()
    bgm, durations = build_video(frames)
    write_manifest(frames, bgm, durations)
    print(FINAL_OUT)


if __name__ == "__main__":
    main()
