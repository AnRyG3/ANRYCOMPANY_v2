from __future__ import annotations

import json
import re
import subprocess
import urllib.parse
import urllib.request
import wave
from pathlib import Path


ROOT = Path(r"F:\ANRYCAMPANY")
UNIT = ROOT / "reel_assets" / "pre_exam_series" / "22_barium_morning_smoking_v1"
TELOP_DIR = UNIT / "telop"
AUDIO_DIR = UNIT / "audio"
WORK_DIR = UNIT / "_video_work"
VIDEO_DIR = UNIT / "video"
PRODUCTION_MANIFEST = UNIT / "production_manifest.md"
TELOP_MANIFEST = TELOP_DIR / "telop_manifest.json"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
TAIL_SECONDS = 0.03
FINAL_TAIL_SECONDS = 1.0
MIN_DURATION = 1.6
BGM_VOLUME = "-27dB"
OUT = VIDEO_DIR / "バリウム検査の朝_タバコと水とコーヒー_20261005.mp4"

FRAMES = [
    "telop_01_hook_smoking_morning.png",
    "telop_02_check_instruction.png",
    "telop_03_facility_guidance.png",
    "telop_04_record_intake.png",
    "telop_05_facility_judgment.png",
    "telop_06_medicine_check.png",
    "telop_07_call_before_departure.png",
    "telop_08_tell_as_is.png",
    "telop_09_follow_guidance.png",
    "telop_10_save_night_before.png",
    "telop_11_four_item_cta.png",
]

DISPLAY_NARRATION = [
    "いつもの癖でタバコを吸ってしまった。今日、胃のバリウム検査なのに。どうしよう。",
    "まずは、案内書を確認して、施設へ伝えてください。",
    "食事、水分、喫煙の制限は、施設ごとに違います。",
    "水やコーヒーも含めて、何を、いつごろ、どのくらい口にしたか。喫煙した時刻と本数も伝えましょう。",
    "検査を受けられるかどうかは、施設が判断します。",
    "薬は自己判断でやめず、案内書か予約先に確認してください。",
    "検査前に分かったときは、早めに予約先へ連絡を。",
    "食べたこと、飲んだこと、吸ったことを、そのまま伝えてください。",
    "一人で決めず、施設からの案内に任せましょう。",
    "検査前日の夜に見返せるよう、この投稿を保存しておいてください。",
    "確認するのは四つ。食事、水分、喫煙は何時からか。そして薬です。",
]

# Voice-only substitutions; display text remains unchanged.
VOICE_TEXT = [
    "いつものくせでタバコを吸ってしまった。きょう、胃のバリウム検査なのに。どうしよう。",
    "まずは、案内書を確認して、施設へ伝えてください。",
    "食事、水分、喫煙の制限は、施設ごとに違います。",
    "水やコーヒーも含めて、なにを、いつごろ、どのくらい口にしたか。喫煙した時刻と本数も伝えましょう。",
    "検査を受けられるかどうかは、施設が判断します。",
    "薬は自己判断でやめず、案内書か予約先に確認してください。",
    "検査前に分かったときは、早めに予約先へ連絡を。",
    "食べたこと、飲んだこと、吸ったことを、そのまま伝えてください。",
    "一人で決めず、施設からの案内に任せましょう。",
    "検査前日の夜に見返せるよう、この投稿を保存しておいてください。",
    "確認するのは四つ。食事、水分、喫煙はなんじからか。そして薬です。",
]


def run(command: list[str | Path]) -> None:
    subprocess.run([str(part) for part in command], check=True)


def post_json(path: str, params: dict | None = None, payload: dict | None = None) -> bytes:
    query = urllib.parse.urlencode(params or {})
    request = urllib.request.Request(
        f"{VOICEVOX}{path}" + (f"?{query}" if query else ""),
        data=None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        method="POST",
    )
    if payload is not None:
        request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def synthesize(text: str, output: Path) -> None:
    query = json.loads(post_json("/audio_query", {"text": text, "speaker": SPEAKER}))
    query.update({"speedScale": VOICE_SPEED, "pitchScale": 0.0, "intonationScale": 0.95, "volumeScale": 1.0, "prePhonemeLength": 0.0, "postPhonemeLength": 0.03})
    output.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def media_duration(path: Path) -> float:
    result = subprocess.run([str(FFMPEG), "-i", str(path)], capture_output=True)
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", result.stderr.decode("utf-8", errors="ignore"))
    if not match:
        raise RuntimeError(f"Could not determine duration for {path}")
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def concat_list(paths: list[Path], destination: Path) -> None:
    destination.write_text("".join(f"file '{path.as_posix()}'\n" for path in paths), encoding="utf-8")


def assert_source_lock() -> list[Path]:
    markdown = PRODUCTION_MANIFEST.read_text(encoding="utf-8")
    approved_images = [path for path in re.findall(r"`([A-Za-z]:\\[^`]+\\images\\[^`]+\.png)`", markdown)]
    telop_data = json.loads(TELOP_MANIFEST.read_text(encoding="utf-8-sig"))
    telop_sources = [frame["source"] for frame in telop_data["frames"]]
    telop_outputs = [Path(frame["output"]) for frame in telop_data["frames"]]
    expected_outputs = [TELOP_DIR / name for name in FRAMES]
    if approved_images != telop_sources or telop_outputs != expected_outputs:
        raise RuntimeError("Production manifest, telop source order, and telop output order must match one-to-one.")
    if len(approved_images) != len(FRAMES) or not all(path.exists() for path in expected_outputs):
        raise RuntimeError("An approved source or required telop frame is missing.")
    return expected_outputs


def main() -> None:
    frame_paths = assert_source_lock()
    for directory in [AUDIO_DIR, WORK_DIR, VIDEO_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    for required in [FFMPEG, BGM, *frame_paths]:
        if not required.exists():
            raise FileNotFoundError(required)

    padded, durations, cut_durations = [], [], []
    for index, text in enumerate(VOICE_TEXT, start=1):
        voice = AUDIO_DIR / f"voice_{index:02d}.wav"
        padded_voice = WORK_DIR / f"voice_{index:02d}_padded.wav"
        synthesize(text, voice)
        duration = wav_duration(voice)
        tail_seconds = FINAL_TAIL_SECONDS if index == len(VOICE_TEXT) else TAIL_SECONDS
        cut_duration = max(MIN_DURATION, duration + tail_seconds)
        run([FFMPEG, "-y", "-i", voice, "-af", f"apad=pad_dur={cut_duration:.3f},atrim=duration={cut_duration:.3f}", "-ar", "44100", "-ac", "2", padded_voice])
        durations.append(duration)
        cut_durations.append(cut_duration)
        padded.append(padded_voice)

    segments = []
    for index, (frame, duration) in enumerate(zip(frame_paths, cut_durations), start=1):
        segment = WORK_DIR / f"segment_{index:02d}.mp4"
        run([FFMPEG, "-y", "-loop", "1", "-t", f"{duration:.3f}", "-i", frame, "-vf", "scale=1080:1920,format=yuv420p", "-r", "30", "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p", segment])
        segments.append(segment)

    voice_list, video_list = WORK_DIR / "voice_segments.txt", WORK_DIR / "video_segments.txt"
    concat_list(padded, voice_list)
    concat_list(segments, video_list)
    voice_all, silent_video = AUDIO_DIR / "voice_all.wav", WORK_DIR / "silent_video.mp4"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", voice_list, "-c", "copy", voice_all])
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", video_list, "-c", "copy", silent_video])
    run([
        FFMPEG, "-y", "-i", silent_video, "-i", voice_all, "-stream_loop", "-1", "-i", BGM,
        "-filter_complex", f"[1:a]volume=1.45[voice];[2:a]volume={BGM_VOLUME}[bgm];[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,alimiter=limit=0.95[a]",
        "-map", "0:v", "-map", "[a]", "-shortest", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT,
    ])

    qa = {
        "video_duration_seconds": round(media_duration(OUT), 3),
        "audio_duration_seconds": round(media_duration(voice_all), 3),
        "voice_to_telop_mapping": "one narration segment per matching telop frame in cut order",
        "cut_tail_seconds": [round(cut - voice, 3) for voice, cut in zip(durations, cut_durations)],
        "pacing": "0.03-second tail between cuts; 1.0-second final hold after the last narration",
    }
    (VIDEO_DIR / "video_manifest.json").write_text(json.dumps({
        "title": "バリウム検査の朝、タバコと水とコーヒーは？",
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": VOICE_SPEED,
        "display_narration": DISPLAY_NARRATION,
        "voice_text": VOICE_TEXT,
        "telop_frames": [str(path) for path in frame_paths],
        "voice_durations_seconds": [round(value, 3) for value in durations],
        "cut_durations_seconds": [round(value, 3) for value in cut_durations],
        "voice_audio": str(voice_all),
        "video": str(OUT),
        "qa": qa,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8-sig")
    print(OUT)
    print(json.dumps(qa, ensure_ascii=False))


if __name__ == "__main__":
    main()
