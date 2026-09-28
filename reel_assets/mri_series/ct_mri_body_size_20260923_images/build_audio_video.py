from __future__ import annotations

import json
import re
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave
from pathlib import Path


ROOT = Path(r"F:\ANRYCAMPANY")
BASE = ROOT / "reel_assets" / "mri_series" / "ct_mri_body_size_20260923_images"
FRAME_DIR = BASE / "telop_frames"
AUDIO_DIR = BASE / "audio"
WORK_DIR = BASE / "video_work"
ASSET_VIDEO = BASE / "体格が気になる、CTやMRIの検査台に乗れる？.mp4"
FINAL_VIDEO = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形" / ASSET_VIDEO.name
MANIFEST = BASE / "video_manifest.json"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
BGM_VOLUME = "-25dB"

# Each telop frame has exactly one spoken segment. The frame duration is the
# measured WAV duration: no transition padding and no inserted silent gap.
SEGMENTS = [
    ("01_hook.png", "シーティーやエムアールアイの検査台。私でも乗れるかな。"),
    ("02_consult.png", "心配なときは、予約のときに相談できます。"),
    ("03_equipment_conditions.png", "シーティーやエムアールアイは、装置ごとに、検査台の耐荷重や、かいこうぶの広さが異なります。"),
    ("04_check_items.png", "検査部位や体格によって、確認する内容も変わります。"),
    ("05_tell_body_size.png", "予約のときに、体重や体格を伝えてください。"),
    ("06_advance_check.png", "事前にわかれば、使う装置や検査方法を確認しやすくなります。"),
    ("07_for_safety.png", "これは、安全に検査を行うために必要な確認です。"),
    ("08_ask_reservation_desk.png", "受けられないと決める前に、まず予約先へ相談してみてください。"),
    ("09_save_cta.png", "検査前日や予約前に見返せるよう、この投稿を保存してください。"),
    ("10_follow_cta.png", "役に立ったら、フォローしてもらえるとうれしいです。"),
]


def run(command: list[str | Path]) -> None:
    subprocess.run([str(value) for value in command], check=True)


def post_json(path: str, params: dict | None = None, payload: dict | None = None) -> bytes:
    query = urllib.parse.urlencode(params or {})
    url = f"{VOICEVOX}{path}" + (f"?{query}" if query else "")
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=data, method="POST")
    if data is not None:
        request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def synthesize(text: str, output: Path) -> None:
    query = json.loads(post_json("/audio_query", {"text": text, "speaker": SPEAKER}))
    query.update({
        "speedScale": VOICE_SPEED,
        "pitchScale": 0.0,
        "intonationScale": 0.96,
        "pauseLengthScale": 0.32,
        "prePhonemeLength": 0.02,
        "postPhonemeLength": 0.04,
        "volumeScale": 1.0,
    })
    output.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def duration(path: Path) -> float:
    with wave.open(str(path), "rb") as audio:
        return audio.getnframes() / audio.getframerate()


def concat_list(paths: list[Path], output: Path) -> None:
    output.write_text("".join(f"file '{path.as_posix()}'\n" for path in paths), encoding="utf-8")


def media_duration(path: Path) -> float:
    result = subprocess.run(
        [str(FFMPEG), "-i", str(path)],
        check=False,
        capture_output=True,
    )
    stderr = (result.stderr or b"").decode("utf-8", errors="ignore")
    match = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", stderr)
    if match is None:
        raise RuntimeError(f"Could not determine duration for {path}")
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def main() -> None:
    required = [FFMPEG, BGM, *[FRAME_DIR / frame for frame, _ in SEGMENTS]]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required files: " + ", ".join(missing))

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_VIDEO.parent.mkdir(parents=True, exist_ok=True)

    voice_paths: list[Path] = []
    timings: list[dict] = []
    cursor = 0.0
    for index, (frame_name, voice_text) in enumerate(SEGMENTS, start=1):
        voice_path = AUDIO_DIR / f"voice_{index:02d}.wav"
        synthesize(voice_text, voice_path)
        segment_duration = duration(voice_path)
        voice_paths.append(voice_path)
        timings.append({
            "index": index,
            "frame": frame_name,
            "voice": voice_text,
            "start_seconds": round(cursor, 3),
            "duration_seconds": round(segment_duration, 3),
            "end_seconds": round(cursor + segment_duration, 3),
        })
        cursor += segment_duration

    voice_list = WORK_DIR / "voice_segments.txt"
    concat_list(voice_paths, voice_list)
    voice_all = AUDIO_DIR / "voice.wav"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", voice_list, "-c", "copy", voice_all])

    video_segments: list[Path] = []
    for item in timings:
        source = FRAME_DIR / item["frame"]
        output = WORK_DIR / f"segment_{item['index']:02d}.mp4"
        run([
            FFMPEG, "-y", "-loop", "1", "-t", f"{item['duration_seconds']:.3f}", "-i", source,
            "-vf", "scale=1080:1920,format=yuv420p", "-r", "30", "-c:v", "libx264",
            "-tune", "stillimage", "-pix_fmt", "yuv420p", output,
        ])
        video_segments.append(output)

    video_list = WORK_DIR / "video_segments.txt"
    concat_list(video_segments, video_list)
    silent_video = WORK_DIR / "silent_video.mp4"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", video_list, "-c", "copy", silent_video])
    run([
        FFMPEG, "-y", "-i", silent_video, "-i", voice_all, "-stream_loop", "-1", "-i", BGM,
        "-filter_complex", f"[1:a]volume=1.4[voice];[2:a]volume={BGM_VOLUME}[bgm];"
        "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,alimiter=limit=0.95[a]",
        "-map", "0:v", "-map", "[a]", "-shortest", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", ASSET_VIDEO,
    ])
    shutil.copy2(ASSET_VIDEO, FINAL_VIDEO)

    audio_seconds = duration(voice_all)
    video_seconds = media_duration(ASSET_VIDEO)
    MANIFEST.write_text(json.dumps({
        "title": "体格が気になる、CTやMRIの検査台に乗れる？",
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": VOICE_SPEED,
        "transition_silence_seconds": 0.0,
        "pause_length_scale": 0.32,
        "frames_and_voice": timings,
        "audio_seconds": round(audio_seconds, 3),
        "video_seconds": round(video_seconds, 3),
        "audio_video_difference_seconds": round(abs(audio_seconds - video_seconds), 3),
        "audio": str(voice_all),
        "asset_video": str(ASSET_VIDEO),
        "final_video": str(FINAL_VIDEO),
    }, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(ASSET_VIDEO)
    print(FINAL_VIDEO)
    print(json.dumps({"audio_seconds": round(audio_seconds, 3), "video_seconds": round(video_seconds, 3)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
