from pathlib import Path
import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "bone_density_series" / "04_low_bone_density_fracture_risk"
BG_DIR = ASSET_DIR / "background_frames"
FRAME_DIR = ASSET_DIR / "final_text_frames"
WORK_DIR = ASSET_DIR / "_video_work"
AUDIO_DIR = ASSET_DIR / "audio"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
OUT = ASSET_DIR / "骨密度が低いとすぐ骨折するの.mp4"
FINAL_OUT = (
    ROOT
    / "01_ショート動画_リール_YouTubeShorts"
    / "インスタ完成形"
    / "骨密度が低いとすぐ骨折するの.mp4"
)

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
SIZE = (1080, 1920)

SLIDES = [
    (1, "骨密度が低い＝\nすぐ骨折？", "center"),
    (2, "そう思うと\n不安ですよね", "top"),
    (3, "でも、結果だけでは\n決まりません", "center"),
    (4, "骨折リスクは\n総合的に見ます", "center"),
    (5, "年齢\n骨折歴\n転倒リスク\n薬の影響\n生活環境", "bullet"),
    (6, "だから決めつけなくて\n大丈夫", "top"),
    (7, "大事なのは\n今後の注意点", "center"),
    (9, "気になる時は\n医師や施設へ", "center"),
    (10, "骨を守るための\n入口です", "top"),
    (11, "検査前の不安を\n安心に変える情報を発信中", "center"),
    (12, "骨密度検査の前に\n保存", "center"),
]

NARRATION = [
    "骨密度が低いと言われると、すぐ骨折するの？と不安になりますよね。",
    "でも、骨密度の結果だけで、必ず骨折すると決まるわけではありません。",
    "骨折のしやすさは、年齢やこれまでの骨折歴、転倒リスク、薬の影響、生活環境なども含めて考えます。",
    "だから、低いイコールすぐ骨折、と決めつけなくて大丈夫です。",
    "大事なのは、今の自分にどんな注意が必要かを知ること。",
    "気になる結果が出たときは、自己判断せず、医師や施設の説明を確認してください。",
    "骨密度検査は、不安を増やすためではなく、これからの骨を守るための入口です。",
    "検査前の不安を、安心に変える情報を発信中。",
    "骨密度検査の前に見返せるように、保存しておいてください。",
]

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\YuGothB.ttc",
    r"C:\Windows\Fonts\meiryob.ttc",
    r"C:\Windows\Fonts\YuGothM.ttc",
    r"C:\Windows\Fonts\meiryo.ttc",
]

# Voice-only text. Keep difficult medical readings in kana so VOICEVOX does not guess.
NARRATION = [
    "こつみつどが低いと、すぐ骨折しますか。",
    "そう思うと、不安になりますよね。",
    "でも、結果だけで決まるわけではありません。",
    "骨折リスクは、いくつかの要素を合わせて見ます。",
    "年齢、骨折歴、転倒リスク、薬の影響、生活環境などです。",
    "だから、あたいが低い。イコール。骨折。と決めつけなくて大丈夫です。",
    "大事なのは、今後の注意点を知ることです。",
    "気になる時は、自己判断せず、医師や施設へ確認してください。",
    "こつみつど検査は、これからの骨を守るための入口です。",
    "検査前の不安を、安心に変える情報を発信中です。",
    "こつみつど検査の前に、見返せるように保存しておいてください。",
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


def fit_font(draw, lines, max_width, start_size, min_size=30):
    size = start_size
    while size >= min_size:
        font = choose_font(size)
        if all(draw.textbbox((0, 0), line, font=font)[2] <= max_width for line in lines):
            return font
        size -= 2
    return choose_font(min_size)


def panel_box(kind):
    if kind == "top":
        return (76, 185, 1004, 555)
    if kind == "bullet":
        return (96, 455, 984, 1395)
    return (76, 760, 1004, 1165)


def draw_text_panel(image, box):
    shadow = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    x1, y1, x2, y2 = box
    shadow_draw.rounded_rectangle(
        (x1 + 8, y1 + 12, x2 + 8, y2 + 12),
        radius=36,
        fill=(30, 35, 38, 38),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    panel = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    panel_draw = ImageDraw.Draw(panel)
    panel_draw.rounded_rectangle(box, radius=36, fill=(255, 255, 255, 204))
    return Image.alpha_composite(Image.alpha_composite(image, shadow), panel)


def draw_center_text(image, text, box, start_size):
    image = draw_text_panel(image, box)
    draw = ImageDraw.Draw(image)
    lines = text.split("\n")
    font = fit_font(draw, lines, 820, start_size)
    line_h = int(font.size * 1.32)
    total_h = line_h * len(lines)
    y = (box[1] + box[3]) // 2 - total_h // 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        x = (SIZE[0] - (bbox[2] - bbox[0])) // 2
        draw.text((x + 3, y + 3), line, font=font, fill=(255, 255, 255, 150))
        draw.text((x, y), line, font=font, fill=(28, 44, 58, 255))
        y += line_h
    return image


def draw_bullet_text(image, text, box):
    image = draw_text_panel(image, box)
    draw = ImageDraw.Draw(image)
    font = choose_font(70)
    bullet_font = choose_font(72)
    items = text.split("\n")
    y = box[1] + 120
    for item in items:
        draw.text((238, y), "・", font=bullet_font, fill=(38, 74, 92, 255))
        draw.text((320, y), item, font=font, fill=(26, 42, 54, 255))
        y += 146
    return image


def make_frames():
    FRAME_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    for idx, text, kind in SLIDES:
        image = cover_to_size(BG_DIR / f"bg_{idx:02d}.png")
        box = panel_box(kind)
        if kind == "bullet":
            image = draw_bullet_text(image, text, box)
        else:
            start_size = 90 if idx in {1, 8} else 82
            if idx in {6, 10, 11}:
                start_size = 76
            image = draw_center_text(image, text, box, start_size)
        out = FRAME_DIR / f"frame_{idx:02d}.png"
        image.convert("RGB").save(out, quality=95)
        outputs.append(out)
    make_contact_sheet(outputs)
    return outputs


def make_contact_sheet(paths):
    thumb_w, thumb_h = 270, 480
    label_h = 34
    cols = 6
    rows = 2
    sheet = Image.new("RGB", (thumb_w * cols, (thumb_h + label_h) * rows), (245, 247, 250))
    draw = ImageDraw.Draw(sheet)
    font = choose_font(20)
    for idx, path in enumerate(paths):
        im = Image.open(path).convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (idx % cols) * thumb_w
        y = (idx // cols) * (thumb_h + label_h)
        sheet.paste(im, (x, y))
        draw.text((x + 8, y + thumb_h + 7), path.name, fill=(30, 40, 50), font=font)
    sheet.save(ASSET_DIR / "_contact_sheet_final_text_frames.png", quality=95)


def find_bgm():
    candidates = list(ROOT.rglob("healing_wind.mp3"))
    if candidates:
        return candidates[0]
    candidates = list(ROOT.rglob("Kind_Heart.mp3"))
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
    query["intonationScale"] = 1.0
    query["volumeScale"] = 1.0
    query["prePhonemeLength"] = 0.08
    query["postPhonemeLength"] = 0.14
    out.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path):
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def make_video(frames):
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_OUT.parent.mkdir(parents=True, exist_ok=True)
    bgm = find_bgm()

    for required in [*frames, FFMPEG, bgm]:
        if not required.exists():
            raise FileNotFoundError(required)

    voice_files = []
    for idx, text in enumerate(NARRATION, start=1):
        voice = AUDIO_DIR / f"voice_{idx:02d}.wav"
        synthesize_voice(text, voice)
        voice_files.append(voice)

    frame_count = len(frames)
    voice_to_frame = {idx: [idx] for idx in range(1, frame_count + 1)}
    frame_durations = [2.8] * frame_count
    for voice_idx, frame_numbers in voice_to_frame.items():
        duration = max(2.8 * len(frame_numbers), wav_duration(voice_files[voice_idx - 1]) + 0.45)
        per_frame = duration / len(frame_numbers)
        for frame_number in frame_numbers:
            frame_durations[frame_number - 1] = per_frame

    padded_wavs = []
    for voice_idx, voice in enumerate(voice_files, start=1):
        padded = WORK_DIR / f"voice_{voice_idx:02d}_padded.wav"
        frame_numbers = voice_to_frame[voice_idx]
        duration = sum(frame_durations[number - 1] for number in frame_numbers)
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
        for frame, duration in zip(frames, frame_durations):
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
        "title": "骨密度が低いとすぐ骨折するの",
        "speaker": "VOICEVOX speaker id 20",
        "voice_speed": 1.2,
        "bgm": str(bgm),
        "bgm_volume": "-22 dB",
        "frames": [str(frame) for frame in frames],
        "durations_seconds": [round(value, 3) for value in frame_durations],
        "total_seconds": round(sum(frame_durations), 3),
        "narration": NARRATION,
        "asset_video": str(OUT),
        "final_video": str(FINAL_OUT),
    }
    (ASSET_DIR / "video_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return FINAL_OUT


def main():
    frames = make_frames()
    final = make_video(frames)
    print(final)


if __name__ == "__main__":
    main()
