from pathlib import Path
import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "bone_density_series" / "fls_after_fracture_v1"
FRAME_DIR = ASSET_DIR / "final_text_frames"
WORK_DIR = ASSET_DIR / "_video_work"
AUDIO_DIR = ASSET_DIR / "audio"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
OUT = ASSET_DIR / "骨折後に骨の検査を勧められたら_FLSのはなし.mp4"
FINAL_OUT = (
    ROOT
    / "01_ショート動画_リール_YouTubeShorts"
    / "インスタ完成形"
    / "骨折後に骨の検査を勧められたら_FLSのはなし.mp4"
)

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
SIZE = (1080, 1920)

SLIDES = [
    (1, "また検査？\nと思ったら"),
    (2, "ひと安心した頃の\n検査案内"),
    (3, "次の骨折を\n防ぐためです"),
    (4, "おかしな案内では\nありません"),
    (5, "股関節骨折は\n早期手術が大切"),
    (6, "術後に\n骨密度検査も"),
    (7, "骨折リエゾン\nサービス（FLS）"),
    (8, "治療後の骨にも\n目を向ける仕組み"),
    (9, "不安に\n先回りで備える"),
    (10, "案内があったら\n受けてみてください"),
    (11, "次回も不安を\n解消する話をお届け"),
    (12, "ご家族のためにも\n保存してください"),
]

NARRATION = [
    "骨折の治療が終わったのに、また検査を勧められた。",
    "手術や入院が終わって、ひと安心したところでの提案。戸惑うかたも多いと思います。",
    "実はこれ、次の骨折を防ぐための取り組みなんです。",
    "追加の検査を勧められても、おかしなことではありません。",
    "たとえば股関節を骨折した場合、できるだけ早く手術を行うことが推奨されています。",
    "そして手術後、こつみつどを測る検査が行われることがあります。",
    "こうした取り組みを、骨折リエゾンサービス、FLSと呼びます。",
    "骨折の治療をした病院が、その後の骨の状態にも目を向ける仕組みです。",
    "また骨折するかも、という不安に、先回りで備える取り組みなんです。",
    "骨折の治療後に検査の案内があったら、ぜひ受けてみてください。",
    "次回も検査にまつわる不安を解消する話をお届けします。フォローして待っていてください。",
    "骨折治療を受けたご家族がいるかたも、よかったら保存しておいてください。",
]

VOICE_READING_REPLACEMENTS = {
    "骨密度": "こつみつど",
    "戸惑う方": "戸惑うかた",
    "いる方": "いるかた",
    "方も": "かたも",
    "方は": "かたは",
    "方へ": "かたへ",
    "方に": "かたに",
    "方が": "かたが",
    "方の": "かたの",
}

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
    if idx in {4, 9}:
        return (74, 1210, 1006, 1580)
    return (74, 166, 1006, 590)


def draw_text_panel(image, box):
    x1, y1, x2, y2 = box
    shadow = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(
        (x1 + 8, y1 + 12, x2 + 8, y2 + 12),
        radius=34,
        fill=(22, 30, 38, 48),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(16))
    panel = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    panel_draw = ImageDraw.Draw(panel)
    panel_draw.rounded_rectangle(box, radius=34, fill=(255, 255, 255, 218))
    return Image.alpha_composite(Image.alpha_composite(image, shadow), panel)


def draw_center_text(image, text, box, start_size):
    image = draw_text_panel(image, box)
    draw = ImageDraw.Draw(image)
    lines = text.split("\n")
    font = fit_font(draw, lines, 840, start_size)
    line_h = int(font.size * 1.32)
    total_h = line_h * len(lines)
    y = (box[1] + box[3]) // 2 - total_h // 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        x = (SIZE[0] - (bbox[2] - bbox[0])) // 2
        draw.text((x + 3, y + 3), line, font=font, fill=(255, 255, 255, 160))
        draw.text((x, y), line, font=font, fill=(27, 45, 58, 255))
        y += line_h
    return image


def make_contact_sheet(paths, out):
    thumb_w, thumb_h = 270, 480
    label_h = 34
    cols = 4
    rows = 3
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
    outputs = []
    for idx, text in SLIDES:
        bg = ASSET_DIR / f"bg_{idx:02d}_no_text.png"
        image = cover_to_size(bg)
        start_size = 72 if idx in {5, 10, 11, 12} else 80
        if idx in {1, 3, 7, 8, 9}:
            start_size = 76
        image = draw_center_text(image, text, text_box(idx), start_size)
        out = FRAME_DIR / f"frame_{idx:02d}.png"
        image.convert("RGB").save(out, quality=95)
        outputs.append(out)
    make_contact_sheet(outputs, ASSET_DIR / "_contact_sheet_final_text_frames.png")
    return outputs


def find_bgm():
    for name in ("healing_wind.mp3", "Kind_Heart.mp3"):
        candidates = list(ROOT.rglob(name))
        if candidates:
            return candidates[0]
    raise FileNotFoundError("BGM file was not found")


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
    for source, reading in VOICE_READING_REPLACEMENTS.items():
        text = text.replace(source, reading)
    query = json.loads(post_json("/audio_query", {"text": text, "speaker": SPEAKER}))
    query["speedScale"] = 1.20
    query["pitchScale"] = 0.0
    query["intonationScale"] = 1.0
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
    FINAL_OUT.parent.mkdir(parents=True, exist_ok=True)
    bgm = find_bgm()

    voice_files = []
    for idx, text in enumerate(NARRATION, start=1):
        voice = AUDIO_DIR / f"voice_{idx:02d}.wav"
        synthesize_voice(text, voice)
        voice_files.append(voice)

    padded_wavs = []
    durations = []
    for idx, voice in enumerate(voice_files, start=1):
        padded = WORK_DIR / f"voice_frame_{idx:02d}_padded.wav"
        min_duration = 3.2
        if idx in {2, 5, 8, 9, 11, 12}:
            min_duration = 4.0
        duration = max(min_duration, wav_duration(voice) + 0.45)
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
        "[1:a]volume=1.4[voice];[2:a]volume=-22dB[bgm];"
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

    manifest = {
        "title": "骨折したあと、骨の検査も勧められたら？（FLSのはなし）",
        "speaker": "VOICEVOX speaker id 20",
        "voice_speed": 1.2,
        "bgm": str(bgm),
        "bgm_volume": "-22 dB",
        "frames": [str(frame) for frame in frames],
        "durations_seconds": [round(value, 3) for value in durations],
        "total_seconds": round(sum(durations), 3),
        "narration": NARRATION,
        "asset_video": str(OUT),
        "final_video": str(FINAL_OUT),
    }
    (ASSET_DIR / "video_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main():
    for idx in range(1, 13):
        path = ASSET_DIR / f"bg_{idx:02d}_no_text.png"
        if not path.exists():
            raise FileNotFoundError(path)
    for required in (FFMPEG,):
        if not required.exists():
            raise FileNotFoundError(required)
    frames = make_frames()
    build_video(frames)
    print(FINAL_OUT)


if __name__ == "__main__":
    main()
