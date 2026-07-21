from pathlib import Path
import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "mri_series" / "exam_discomfort_tell_staff_m70"
FRAME_DIR = ASSET_DIR / "text_frames"
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_video_work"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
OUT = ASSET_DIR / "検査中に苦しくなったら_伝え方.mp4"
FINAL_OUT = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形" / OUT.name

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
BGM_VOLUME = "-25dB"

FRAMES = [f"frame{index:02d}_telop.png" for index in range(1, 11)]
DISPLAY_NARRATION = [
    "検査台に横になったとき、急に息が苦しくなるように感じることがあります。",
    "これくらいで言ったら、迷惑かな。そう迷う方も少なくありません。",
    "苦しいと感じたら、我慢せずすぐに教えてください。",
    "検査中の伝え方は、ブザーやマイクなどがあります。",
    "必要に応じて、検査をいったん止めて対応します。",
    "体調の変化は、検査の妨げではなく、大切な情報です。",
    "苦しいです。気分が悪いです。そのひとことだけでも、十分伝わります。",
    "伝えることは、恥ずかしいことでも、迷惑なことでもありません。",
    "検査前に、いつでも見返せるよう保存しておいてください。",
    "フォローして、一緒に検査への不安を減らしていきましょう。",
]
VOICE_TEXT = [
    "検査台に横になったとき、急に息が苦しくなるように感じることがあります。",
    "これくらいで言ったら、迷惑かな。そう迷うかたも少なくありません。",
    "苦しいと感じたら、我慢せずすぐに教えてください。",
    "検査中の伝えかたは、ブザーやマイクなどがあります。",
    "必要に応じて、検査をいったん止めて対応します。",
    "体調の変化は、検査の妨げではなく、大切な情報です。",
    "苦しいです。気分が悪いです。そのひとことだけでも、十分伝わります。",
    "伝えることは、恥ずかしいことでも、迷惑なことでもありません。",
    "検査前に、いつでも見返せるよう保存しておいてください。",
    "フォローして、一緒に検査への不安を減らしていきましょう。",
]
MIN_DURATIONS = [4.6, 4.1, 3.7, 3.8, 3.8, 3.8, 4.2, 4.0, 3.8, 4.2]


def run(command: list[Path | str]) -> None:
    subprocess.run([str(part) for part in command], check=True)


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
        "prePhonemeLength": 0.08,
        "postPhonemeLength": 0.16,
    })
    output.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def main() -> None:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_OUT.parent.mkdir(parents=True, exist_ok=True)
    frame_paths = [FRAME_DIR / frame for frame in FRAMES]
    for required in [FFMPEG, BGM, *frame_paths]:
        if not required.exists():
            raise FileNotFoundError(required)

    padded_wavs, durations = [], []
    for index, text in enumerate(VOICE_TEXT, start=1):
        voice = AUDIO_DIR / f"voice_{index:02d}.wav"
        padded = WORK_DIR / f"voice_{index:02d}_padded.wav"
        synthesize_voice(text, voice)
        duration = max(MIN_DURATIONS[index - 1], wav_duration(voice) + 0.35)
        durations.append(duration)
        run([
            FFMPEG, "-y", "-i", voice,
            "-af", f"apad=pad_dur={duration:.3f},atrim=duration={duration:.3f}",
            "-ar", "44100", "-ac", "2", padded,
        ])
        padded_wavs.append(padded)

    frames_file = WORK_DIR / "frames.txt"
    frames_file.write_text(
        "".join(f"file '{path.as_posix()}'\nduration {duration:.3f}\n" for path, duration in zip(frame_paths, durations))
        + f"file '{frame_paths[-1].as_posix()}'\n",
        encoding="utf-8",
    )
    voices_file = WORK_DIR / "voice_segments.txt"
    voices_file.write_text("".join(f"file '{path.as_posix()}'\n" for path in padded_wavs), encoding="utf-8")

    silent_video = WORK_DIR / "silent.mp4"
    voice_all = AUDIO_DIR / "voice.wav"
    run([
        FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", frames_file,
        "-vf", "scale=1080:1920,format=yuv420p", "-r", "30",
        "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p", silent_video,
    ])
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", voices_file, "-c", "copy", voice_all])
    run([
        FFMPEG, "-y", "-i", silent_video, "-i", voice_all, "-stream_loop", "-1", "-i", BGM,
        "-filter_complex",
        f"[1:a]volume=1.45[voice];[2:a]volume={BGM_VOLUME}[bgm];"
        "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=1:normalize=0,alimiter=limit=0.95[a]",
        "-map", "0:v", "-map", "[a]", "-shortest", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", OUT,
    ])
    shutil.copy2(OUT, FINAL_OUT)

    manifest = {
        "title": "検査中に苦しくなったら、どう伝えればいい？",
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": VOICE_SPEED,
        "frames": [str(path) for path in frame_paths],
        "display_narration": DISPLAY_NARRATION,
        "voice_text": VOICE_TEXT,
        "durations_seconds": [round(value, 3) for value in durations],
        "total_seconds": round(sum(durations), 3),
        "audio": str(voice_all),
        "bgm": str(BGM),
        "asset_video": str(OUT),
        "final_video": str(FINAL_OUT),
    }
    (ASSET_DIR / "video_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(OUT)
    print(FINAL_OUT)


if __name__ == "__main__":
    main()
