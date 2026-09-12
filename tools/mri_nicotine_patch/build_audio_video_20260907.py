from pathlib import Path
import json
import re
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "mri_series" / "mri_nicotine_patch_20260907_telop_frames"
FRAME_DIR = ASSET_DIR
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_video_work"
VIDEO_DIR = ASSET_DIR / "video"
QA_DIR = ASSET_DIR / "qa_midframes"
FINAL_DIR = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
OUT = VIDEO_DIR / "MRI前_禁煙パッチを貼っていたら_20260907.mp4"
FINAL_OUT = FINAL_DIR / OUT.name
MANIFEST = ASSET_DIR / "video_manifest_20260907.json"

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
BGM_VOLUME = "-26dB"
TAIL_PADDING_SECONDS = 0.04

FRAMES = [
    "telop_01_hook_patient_patch_mri.png",
    "telop_02_reception_disclose_patch.png",
    "telop_03_patch_before_mri.png",
    "telop_04_patch_mri_attention.png",
    "telop_05_confirm_timing_with_staff.png",
    "telop_06_reassured_after_explanation.png",
    "telop_07_save_and_share_cta.png",
]

DISPLAY_NARRATION = [
    "禁煙パッチをしたまま、MRIを受けていいのかな？",
    "受付で、先に伝えてください。",
    "ニコチンパッチは、MRIの前に外す必要があります。",
    "MRIの影響で貼った部分が熱くなり、やけどのおそれがあるためです。",
    "自分で判断せず、外すタイミングをスタッフに確認しましょう。",
    "先に伝えれば対応してもらえるので、大丈夫です。",
    "MRIの予約票と一緒に見返せるよう保存。禁煙中のご家族にはLINEで共有してくださいね。",
]

# Voice-only phonetic adjustments. Display wording remains unchanged.
VOICE_TEXT = [
    "禁煙パッチをしたまま、エムアールアイを受けていいのかな。",
    "受付で、先に伝えてください。",
    "ニコチンパッチは、エムアールアイの前に外す必要があります。",
    "エムアールアイの影響で、貼った部分が熱くなり、やけどのおそれがあるためです。",
    "自分で判断せず、外すタイミングをスタッフに確認しましょう。",
    "先に伝えれば、対応してもらえるので、大丈夫です。",
    "エムアールアイの予約票と一緒に見返せるよう保存。禁煙中のご家族には、ラインで共有してくださいね。",
]


def run(cmd, capture=False, check=True):
    return subprocess.run(
        [str(part) for part in cmd],
        check=check,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=capture,
    )


def post_json(path, params=None, payload=None):
    query = urllib.parse.urlencode(params or {})
    url = f"{VOICEVOX}{path}" + (f"?{query}" if query else "")
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST")
    if body is not None:
        request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def synthesize_voice(text, output):
    query = json.loads(post_json("/audio_query", {"text": text, "speaker": SPEAKER}))
    query.update({
        "speedScale": VOICE_SPEED,
        "pitchScale": 0.0,
        "intonationScale": 0.95,
        "volumeScale": 1.0,
        "prePhonemeLength": 0.03,
        "postPhonemeLength": 0.04,
    })
    output.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path):
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def media_duration(path):
    result = run([FFMPEG, "-hide_banner", "-i", path], capture=True, check=False)
    text = (result.stderr or "") + (result.stdout or "")
    match = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", text)
    if not match:
        raise RuntimeError(f"Could not parse duration for {path}")
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def cover(image, size):
    width, height = size
    scale = max(width / image.width, height / image.height)
    resized = image.resize((int(image.width * scale), int(image.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - width) // 2
    top = (resized.height - height) // 2
    return resized.crop((left, top, left + width, top + height))


def make_qa_contact_sheet(paths, output):
    cols, rows = 3, 3
    thumb_w, thumb_h, label_h = 240, 426, 34
    sheet = Image.new("RGB", (thumb_w * cols, (thumb_h + label_h) * rows), (245, 245, 245))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for index, path in enumerate(paths):
        x = (index % cols) * thumb_w
        y = (index // cols) * (thumb_h + label_h)
        sheet.paste(cover(Image.open(path).convert("RGB"), (thumb_w, thumb_h)), (x, y))
        draw.text((x + 8, y + thumb_h + 8), f"Scene {index + 1}", fill=(0, 0, 0), font=font)
    sheet.save(output, quality=92)


def main():
    for directory in [AUDIO_DIR, WORK_DIR, VIDEO_DIR, QA_DIR, FINAL_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    frame_paths = [FRAME_DIR / frame for frame in FRAMES]
    for required in [FFMPEG, BGM, *frame_paths]:
        if not required.exists():
            raise FileNotFoundError(required)
    urllib.request.urlopen(f"{VOICEVOX}/version", timeout=5).read()

    padded_wavs, durations, raw_voice_durations = [], [], []
    for index, text in enumerate(VOICE_TEXT, start=1):
        voice = AUDIO_DIR / f"voice_{index:02d}.wav"
        padded = WORK_DIR / f"voice_{index:02d}_timeline.wav"
        synthesize_voice(text, voice)
        raw_duration = wav_duration(voice)
        duration = raw_duration + TAIL_PADDING_SECONDS
        run([FFMPEG, "-y", "-loglevel", "error", "-i", voice,
             "-af", f"apad=pad_dur={TAIL_PADDING_SECONDS:.3f},atrim=duration={duration:.3f}",
             "-ar", "44100", "-ac", "2", padded])
        padded_wavs.append(padded)
        raw_voice_durations.append(raw_duration)
        durations.append(duration)

    voice_list = WORK_DIR / "voice_segments.txt"
    voice_list.write_text("".join(f"file '{path.as_posix()}'\n" for path in padded_wavs), encoding="utf-8")
    voice_all = AUDIO_DIR / "voice.wav"
    run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", voice_list, "-c", "copy", voice_all])

    clips = []
    for index, (frame, duration) in enumerate(zip(frame_paths, durations), start=1):
        clip = WORK_DIR / f"scene_{index:02d}.mp4"
        run([FFMPEG, "-y", "-loglevel", "error", "-loop", "1", "-t", f"{duration:.3f}", "-i", frame,
             "-vf", "scale=1080:1920,format=yuv420p", "-r", "30", "-c:v", "libx264",
             "-tune", "stillimage", "-pix_fmt", "yuv420p", clip])
        clips.append(clip)
    video_list = WORK_DIR / "video_segments.txt"
    video_list.write_text("".join(f"file '{path.as_posix()}'\n" for path in clips), encoding="utf-8")
    silent_video = WORK_DIR / "silent.mp4"
    run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", video_list, "-c", "copy", silent_video])

    mix = AUDIO_DIR / "voice_bgm_mix.wav"
    run([FFMPEG, "-y", "-loglevel", "error", "-i", voice_all, "-stream_loop", "-1", "-i", BGM,
         "-filter_complex", f"[0:a]volume=1.45[voice];[1:a]volume={BGM_VOLUME}[bgm];[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0.2:normalize=0,alimiter=limit=0.95[a]",
         "-map", "[a]", "-ar", "44100", "-ac", "2", mix])
    run([FFMPEG, "-y", "-loglevel", "error", "-i", silent_video, "-i", mix, "-map", "0:v", "-map", "1:a",
         "-shortest", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT])
    shutil.copy2(OUT, FINAL_OUT)

    qa_paths, elapsed = [], 0.0
    for index, duration in enumerate(durations, start=1):
        midpoint = elapsed + duration / 2
        qa_path = QA_DIR / f"qa_mid_{index:02d}.jpg"
        run([FFMPEG, "-y", "-loglevel", "error", "-ss", f"{midpoint:.3f}", "-i", OUT, "-frames:v", "1", qa_path])
        qa_paths.append(qa_path)
        elapsed += duration
    qa_contact = QA_DIR / "qa_midframes_contact_sheet.jpg"
    make_qa_contact_sheet(qa_paths, qa_contact)

    voice_seconds, video_seconds = wav_duration(voice_all), media_duration(OUT)
    manifest = {
        "title": "MRI前、禁煙パッチを貼っていたら",
        "voice_engine": "VOICEVOX",
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": VOICE_SPEED,
        "bgm": str(BGM),
        "bgm_volume": BGM_VOLUME,
        "frames": [str(path) for path in frame_paths],
        "display_narration": DISPLAY_NARRATION,
        "voice_text": VOICE_TEXT,
        "raw_voice_seconds": [round(value, 3) for value in raw_voice_durations],
        "durations_seconds": [round(value, 3) for value in durations],
        "tail_padding_seconds_each": TAIL_PADDING_SECONDS,
        "max_added_gap_seconds": TAIL_PADDING_SECONDS,
        "total_timeline_seconds": round(sum(durations), 3),
        "voice_audio_seconds": round(voice_seconds, 3),
        "video_seconds": round(video_seconds, 3),
        "voice_audio": str(voice_all),
        "voice_bgm_mix": str(mix),
        "asset_video": str(OUT),
        "final_video": str(FINAL_OUT),
        "qa_contact_sheet": str(qa_contact),
        "alignment_check": [{
            "index": index,
            "frame": FRAMES[index - 1],
            "display_narration": DISPLAY_NARRATION[index - 1],
            "voice_text": VOICE_TEXT[index - 1],
            "duration_seconds": round(durations[index - 1], 3),
        } for index in range(1, len(FRAMES) + 1)],
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(OUT)
    print(FINAL_OUT)
    print(qa_contact)
    print(f"timeline_seconds={sum(durations):.3f}")
    print(f"voice_seconds={voice_seconds:.3f}")
    print(f"video_seconds={video_seconds:.3f}")


if __name__ == "__main__":
    main()
