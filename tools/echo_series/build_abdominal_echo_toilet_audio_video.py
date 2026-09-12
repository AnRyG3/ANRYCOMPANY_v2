from pathlib import Path
import json
import math
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "echo_series" / "06_toilet_before_abdominal_echo_v1"
FRAME_DIR = ASSET_DIR / "telop_frames"
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_video_work"
VIDEO_DIR = ASSET_DIR / "video"
QA_DIR = ASSET_DIR / "qa_midframes"
FINAL_DIR = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
BGM_VOLUME = "-26dB"

OUT = VIDEO_DIR / "腹部エコー前_トイレに行ってもいい_20260909.mp4"
FINAL_OUT = FINAL_DIR / OUT.name
MANIFEST = ASSET_DIR / "video_manifest.json"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

FRAMES = [f"telop_{i:02d}.png" for i in range(1, 11)]
DISPLAY_NARRATION = [
    "腹部エコー前。トイレ、今行っていい？",
    "行きたいけれど、検査前だし。迷いますよね。",
    "迷ったら、トイレへ行く前に受付や検査担当者へひとこと。",
    "膀胱などを見るときは、尿がある方が見やすいこともあります。",
    "尿のたまりが影響しにくい部位もあります。",
    "準備は、検査内容や施設で変わります。",
    "トイレ、今行っても大丈夫ですか。と聞けば大丈夫です。",
    "つらいほど我慢せず、スタッフに伝えてください。",
    "検査前日に見返せるよう、保存しておいてください。",
    "次の検査前にも、フォローで見返せます。",
]

# Voice-only text uses punctuation that keeps VOICEVOX pauses natural and brief.
VOICE_TEXT = [
    "腹部エコーのまえ。トイレ、今行っていいのかな。",
    "行きたいけれど、検査まえだし。迷いますよね。",
    "迷ったら、トイレへ行くまえに。受付や検査担当者へ、ひとこと。",
    "ぼうこうなどを見るときは、尿があるほうが見やすいこともあります。",
    "尿のたまりが、影響しにくい部位もあります。",
    "準備は、検査内容や施設で変わります。",
    "トイレ、今行っても大丈夫ですか。と聞けば大丈夫です。",
    "つらいほど我慢せず、スタッフに伝えてください。",
    "検査前日に見返せるよう、保存しておいてください。",
    "次の検査まえにも。フォローで見返せます。",
]


def run(command: list[Path | str], capture: bool = False, check: bool = True):
    return subprocess.run(
        [str(part) for part in command],
        check=check,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=capture,
    )


def post_json(path: str, params=None, payload=None) -> bytes:
    query = urllib.parse.urlencode(params or {})
    url = f"{VOICEVOX}{path}" + (f"?{query}" if query else "")
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST")
    if body is not None:
        request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def synthesize_voice(text: str, output: Path) -> None:
    query = json.loads(post_json("/audio_query", {"text": text, "speaker": SPEAKER}))
    query.update({
        "speedScale": VOICE_SPEED,
        "pitchScale": 0.0,
        "intonationScale": 0.95,
        "volumeScale": 1.0,
        "prePhonemeLength": 0.02,
        "postPhonemeLength": 0.04,
    })
    output.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def media_duration(path: Path) -> float:
    result = run([FFMPEG, "-hide_banner", "-i", path], capture=True, check=False)
    text = (result.stderr or "") + (result.stdout or "")
    marker = "Duration: "
    start = text.find(marker)
    if start < 0:
        raise RuntimeError(f"Could not read duration: {path}")
    stamp = text[start + len(marker):].split(",", 1)[0]
    hours, minutes, seconds = stamp.split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    width, height = size
    scale = max(width / image.width, height / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - width) // 2
    top = (resized.height - height) // 2
    return resized.crop((left, top, left + width, top + height))


def make_qa_contact_sheet(paths: list[Path], output: Path) -> None:
    cols, thumb_w, thumb_h, label_h = 5, 216, 384, 34
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (246, 248, 250))
    draw = ImageDraw.Draw(sheet)
    label_font = ImageFont.truetype(str(FONT_PATH), 20)
    for i, path in enumerate(paths):
        x = (i % cols) * thumb_w
        y = (i // cols) * (thumb_h + label_h)
        image = cover(Image.open(path).convert("RGB"), (thumb_w, thumb_h))
        sheet.paste(image, (x, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill="white")
        draw.text((x + 8, y + thumb_h + 6), f"{i + 1:02d}", font=label_font, fill=(12, 34, 58))
    sheet.save(output, quality=92)


def main() -> None:
    for directory in [AUDIO_DIR, WORK_DIR, VIDEO_DIR, QA_DIR, FINAL_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    frame_paths = [FRAME_DIR / name for name in FRAMES]
    for path in [FFMPEG, BGM, *frame_paths]:
        if not path.exists():
            raise FileNotFoundError(path)
    urllib.request.urlopen(f"{VOICEVOX}/version", timeout=5).read()

    voice_paths, durations = [], []
    for index, text in enumerate(VOICE_TEXT, start=1):
        voice = AUDIO_DIR / f"voice_{index:02d}.wav"
        synthesize_voice(text, voice)
        voice_paths.append(voice)
        durations.append(wav_duration(voice))

    voice_list = WORK_DIR / "voice_segments.txt"
    voice_list.write_text("".join(f"file '{path.as_posix()}'\n" for path in voice_paths), encoding="utf-8")
    voice_all = AUDIO_DIR / "voice.wav"
    run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", voice_list, "-c", "copy", voice_all])

    clips = []
    for index, (frame, duration) in enumerate(zip(frame_paths, durations), start=1):
        clip = WORK_DIR / f"scene_{index:02d}.mp4"
        run([FFMPEG, "-y", "-loglevel", "error", "-loop", "1", "-t", f"{duration:.3f}", "-i", frame,
             "-vf", "scale=1080:1920,format=yuv420p", "-r", "30", "-c:v", "libx264", "-tune", "stillimage",
             "-pix_fmt", "yuv420p", clip])
        clips.append(clip)

    video_list = WORK_DIR / "video_segments.txt"
    video_list.write_text("".join(f"file '{path.as_posix()}'\n" for path in clips), encoding="utf-8")
    silent_video = WORK_DIR / "silent.mp4"
    run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", video_list, "-c", "copy", silent_video])

    mix = AUDIO_DIR / "voice_bgm_mix.wav"
    run([FFMPEG, "-y", "-loglevel", "error", "-i", voice_all, "-stream_loop", "-1", "-i", BGM,
         "-filter_complex", f"[0:a]volume=1.45[voice];[1:a]volume={BGM_VOLUME}[bgm];[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0.15:normalize=0,alimiter=limit=0.95[a]",
         "-map", "[a]", "-ar", "44100", "-ac", "2", mix])
    run([FFMPEG, "-y", "-loglevel", "error", "-i", silent_video, "-i", mix,
         "-map", "0:v", "-map", "1:a", "-shortest", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", OUT])
    shutil.copy2(OUT, FINAL_OUT)

    qa_paths, elapsed = [], 0.0
    for index, duration in enumerate(durations, start=1):
        midpoint = elapsed + duration / 2
        qa = QA_DIR / f"qa_mid_{index:02d}.jpg"
        run([FFMPEG, "-y", "-loglevel", "error", "-ss", f"{midpoint:.3f}", "-i", OUT, "-frames:v", "1", qa])
        qa_paths.append(qa)
        elapsed += duration
    qa_contact = QA_DIR / "qa_midframes_contact_sheet.jpg"
    make_qa_contact_sheet(qa_paths, qa_contact)

    voice_seconds = wav_duration(voice_all)
    video_seconds = media_duration(OUT)
    manifest = {
        "title": "腹部エコー前、トイレに行ってもいい？",
        "voice_engine": "VOICEVOX",
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": VOICE_SPEED,
        "bgm": str(BGM),
        "bgm_volume": BGM_VOLUME,
        "frames": [str(path.relative_to(ROOT)) for path in frame_paths],
        "display_narration": DISPLAY_NARRATION,
        "voice_text": VOICE_TEXT,
        "durations_seconds": [round(value, 3) for value in durations],
        "added_silent_gap_seconds": 0.0,
        "timeline_seconds": round(sum(durations), 3),
        "voice_audio_seconds": round(voice_seconds, 3),
        "video_seconds": round(video_seconds, 3),
        "voice_audio": str(voice_all.relative_to(ROOT)),
        "voice_bgm_mix": str(mix.relative_to(ROOT)),
        "asset_video": str(OUT.relative_to(ROOT)),
        "final_video": str(FINAL_OUT.relative_to(ROOT)),
        "qa_contact_sheet": str(qa_contact.relative_to(ROOT)),
        "alignment_check": [{
            "index": i,
            "frame": FRAMES[i - 1],
            "display_narration": DISPLAY_NARRATION[i - 1],
            "voice_text": VOICE_TEXT[i - 1],
            "duration_seconds": round(durations[i - 1], 3),
        } for i in range(1, len(FRAMES) + 1)],
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(f"timeline_seconds={sum(durations):.3f}")
    print(f"voice_seconds={voice_seconds:.3f}")
    print(f"video_seconds={video_seconds:.3f}")
    print(OUT)
    print(FINAL_OUT)
    print(qa_contact)


if __name__ == "__main__":
    main()
