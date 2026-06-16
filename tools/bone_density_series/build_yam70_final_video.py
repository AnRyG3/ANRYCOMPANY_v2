from pathlib import Path
import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "bone_density_series" / "06_yam70_meaning"
BG_DIR = ASSET_DIR / "generated_backgrounds"
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

SLIDE_TEXT = [
    "YAM70%って\n何？",
    "数字だけ見ると\n不安になりますよね",
    "大丈夫。\n数字には意味があります",
    "YAMは\n若年成人平均値",
    "70%は\n境界ライン",
    "数字だけで\n全ては決まりません",
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

MIN_DURATIONS = [3.1, 3.8, 2.8, 4.4, 5.8, 3.5, 5.6, 4.4, 4.5, 3.1, 3.4, 3.8]

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\YuGothB.ttc",
    r"C:\Windows\Fonts\meiryob.ttc",
    r"C:\Windows\Fonts\YuGothM.ttc",
    r"C:\Windows\Fonts\meiryo.ttc",
]


def run(cmd):
    subprocess.run([str(part) for part in cmd], check=True)


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


def fit_font(draw, lines, max_width, start_size, min_size=34):
    size = start_size
    while size >= min_size:
        font = choose_font(size)
        if all(draw.textbbox((0, 0), line, font=font)[2] <= max_width for line in lines):
            return font
        size -= 2
    return choose_font(min_size)


def text_box(idx):
    if idx in {4, 5, 6, 7, 8, 9, 11, 12}:
        return (74, 140, 1006, 500)
    return (74, 1230, 1006, 1588)


def draw_text_panel(image, text, idx):
    x1, y1, x2, y2 = text_box(idx)
    shadow = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x1 + 8, y1 + 12, x2 + 8, y2 + 12), 34, fill=(22, 30, 38, 48))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))

    panel = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rounded_rectangle((x1, y1, x2, y2), 34, fill=(255, 255, 255, 218))
    image = Image.alpha_composite(Image.alpha_composite(image, shadow), panel)

    draw = ImageDraw.Draw(image)
    lines = text.split("\n")
    start = 78 if idx not in {7, 12} else 62
    font = fit_font(draw, lines, 820, start)
    line_h = int(font.size * 1.34)
    total_h = line_h * len(lines)
    y = (y1 + y2) // 2 - total_h // 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        x = (SIZE[0] - (bbox[2] - bbox[0])) // 2
        draw.text((x + 3, y + 3), line, font=font, fill=(255, 255, 255, 160))
        draw.text((x, y), line, font=font, fill=(26, 43, 58, 255))
        y += line_h
    return image


def make_contact_sheet(paths, out):
    thumb_w, thumb_h, label_h = 270, 480, 34
    cols = 4
    rows = (len(paths) + cols - 1) // cols
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


def make_frames():
    FRAME_DIR.mkdir(parents=True, exist_ok=True)
    frames = []
    for idx, text in enumerate(SLIDE_TEXT, start=1):
        bg = BG_DIR / f"bg_{idx:02d}_no_text.png"
        if not bg.exists():
            raise FileNotFoundError(bg)
        image = cover_to_size(bg)
        image = draw_text_panel(image, text, idx)
        out = FRAME_DIR / f"frame_{idx:02d}.png"
        image.convert("RGB").save(out, quality=95)
        frames.append(out)
    make_contact_sheet(frames, ASSET_DIR / "_contact_sheet_final_text_frames.png")
    return frames


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
    for required in [FFMPEG, bgm, *frames]:
        if not required.exists():
            raise FileNotFoundError(required)

    padded_wavs = []
    durations = []
    for idx, text in enumerate(NARRATION, start=1):
        voice = AUDIO_DIR / f"voice_{idx:02d}.wav"
        padded = WORK_DIR / f"voice_{idx:02d}_padded.wav"
        synthesize_voice(text, voice)
        duration = max(MIN_DURATIONS[idx - 1], wav_duration(voice) + 0.42)
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
        "slide_text": SLIDE_TEXT,
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
    frames = make_frames()
    bgm, durations = build_video(frames)
    write_manifest(frames, bgm, durations)
    print(FINAL_OUT)


if __name__ == "__main__":
    main()
