from pathlib import Path
import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "bone_density_series" / "05_fracture_cascade"
FRAME_DIR = ASSET_DIR / "final_text_frames"
WORK_DIR = ASSET_DIR / "_video_work"
AUDIO_DIR = ASSET_DIR / "audio"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
OUT = ASSET_DIR / "一度骨折すると次の骨折に注意が必要です.mp4"
FINAL_OUT = (
    ROOT
    / "01_ショート動画_リール_YouTubeShorts"
    / "インスタ完成形"
    / "一度骨折すると次の骨折に注意が必要です.mp4"
)

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
SIZE = (1080, 1920)

SLIDES = [
    (
        1,
        ASSET_DIR / "sample_01_patient_home_loungewear_no_text.png",
        "一度骨折したら\n次の骨折にも注意",
        "top",
    ),
    (
        2,
        ASSET_DIR / "frame_02_one_time_problem_no_text.png",
        "骨折は\nその時だけの問題と\n思われがちです",
        "top",
    ),
    (
        3,
        ASSET_DIR / "frame_03_future_fracture_prevention_no_text.png",
        "でも一度骨折した人は\n次の骨折にも\n注意が必要です",
        "top",
    ),
    (
        4,
        ASSET_DIR / "frame_04_wrist_memory_closeup_no_text.png",
        "たとえば\n手首の骨折のあとに",
        "top",
    ),
    (
        5,
        ASSET_DIR / "frame_05_spine_hip_attention_no_text.png",
        "背骨や\n足のつけ根の骨折へ\nつながることがあります",
        "top",
    ),
    (
        6,
        ASSET_DIR / "frame_06_bone_health_check_notice_no_text.png",
        "これは\n骨が弱くなっているサインかも\nしれません",
        "top",
    ),
    (
        7,
        ASSET_DIR / "frame_07_prevention_reassurance_no_text.png",
        "でも大丈夫です\nここで気づけることが\n予防につながります",
        "top",
    ),
    (
        8,
        ASSET_DIR / "sample_02_bone_density_consult_no_text.png",
        "骨密度検査は\n次の骨折を防ぐための\n手がかりになります",
        "top",
    ),
    (
        9,
        ASSET_DIR / "frame_09_doctor_consult_no_text.png",
        "過去に骨折したことがある方は\n整形外科医師に\n相談してください",
        "top",
    ),
    (
        10,
        ASSET_DIR / "frame_10_fls_next_rt_no_text.png",
        "次回は\n骨折連鎖を防ぐ仕組み\nFLSについて話します",
        "top",
    ),
    (
        11,
        ASSET_DIR / "frame_11_fixed_cta_bg_no_text.png",
        "検査前の不安を\n安心に変える情報を発信中",
        "top",
    ),
    (
        12,
        ASSET_DIR / "frame_12_save_cta_bg_no_text.png",
        "骨密度検査の前に\n見返せるように保存",
        "top",
    ),
]

NARRATION = [
    "一度骨折したら、次の骨折にも注意が必要です。",
    "骨折は、その時だけの問題と思われがちです。",
    "でも、一度骨折した人は、次の骨折にも注意が必要になることがあります。",
    "たとえば、手首の骨折のあとに。",
    "背骨や足のつけ根の骨折へ、つながることがあります。",
    "これは、骨が弱くなっているサインかもしれません。",
    "でも大丈夫です。ここで気づけることが、予防につながります。",
    "こつみつど検査は、次の骨折を防ぐための手がかりになります。",
    "過去に骨折したことがあるかたは、整形外科の医師に相談してください。",
    "次回は、骨折連鎖を防ぐ仕組み、エフエルエスについて話します。",
    "検査前の不安を、安心に変える情報を発信中です。",
    "こつみつど検査の前に、見返せるように保存してください。",
]

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


def fit_font(draw, lines, max_width, start_size, min_size=32):
    size = start_size
    while size >= min_size:
        font = choose_font(size)
        if all(draw.textbbox((0, 0), line, font=font)[2] <= max_width for line in lines):
            return font
        size -= 2
    return choose_font(min_size)


def text_box(kind):
    if kind == "top":
        return (76, 178, 1004, 585)
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
    panel_draw.rounded_rectangle(box, radius=36, fill=(255, 255, 255, 208))
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
        draw.text((x + 3, y + 3), line, font=font, fill=(255, 255, 255, 145))
        draw.text((x, y), line, font=font, fill=(28, 44, 58, 255))
        y += line_h
    return image


def make_contact_sheet(paths):
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
    sheet.save(ASSET_DIR / "_contact_sheet_final_text_frames.png", quality=95)


def make_frames():
    FRAME_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    for idx, bg, text, kind in SLIDES:
        image = cover_to_size(bg)
        start_size = 84
        if idx in {1, 11, 12}:
            start_size = 78
        if idx in {5, 8, 9, 10}:
            start_size = 72
        image = draw_center_text(image, text, text_box(kind), start_size)
        out = FRAME_DIR / f"frame_{idx:02d}.png"
        image.convert("RGB").save(out, quality=95)
        outputs.append(out)
    make_contact_sheet(outputs)
    return outputs


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

    padded_wavs = []
    durations = []
    for frame_idx, voice in enumerate(voice_files, start=1):
        padded = WORK_DIR / f"voice_frame_{frame_idx:02d}_padded.wav"
        min_duration = 2.75
        if frame_idx in {4, 5, 8, 9, 10, 11, 12}:
            min_duration = 3.35
        duration = max(min_duration, wav_duration(voice) + 0.45)
        durations.append(duration)
        run(
            [
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
            ]
        )
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
    run(
        [
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
        ]
    )
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", voice_txt, "-c", "copy", voice_all])
    run(
        [
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
        ]
    )
    shutil.copy2(OUT, FINAL_OUT)

    manifest = {
        "title": "一度骨折すると次の骨折に注意が必要です",
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
    return FINAL_OUT


def main():
    frames = make_frames()
    final = make_video(frames)
    print(final)


if __name__ == "__main__":
    main()
