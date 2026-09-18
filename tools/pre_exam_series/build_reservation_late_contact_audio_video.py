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
ASSET_DIR = ROOT / "reel_assets" / "pre_exam_series" / "14_reservation_late_contact_v1_images"
FRAME_DIR = ASSET_DIR / "telop"
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_video_work"
VIDEO_DIR = ASSET_DIR / "video"
FINAL_DIR = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
TAIL_SECONDS = 0.05
MIN_DURATION = 1.2
BGM_VOLUME = "-27dB"

TITLE = "予約時間に遅れそう_まず連絡先を確認_20260918"
OUT = VIDEO_DIR / f"{TITLE}.mp4"
FINAL_OUT = FINAL_DIR / OUT.name
MANIFEST = ASSET_DIR / "video_manifest.json"

FRAMES = [
    "01_station_late_telop.png",
    "02_train_delay_telop.png",
    "03_find_contact_number_telop.png",
    "04_call_appointment_contact_telop.png",
    "05_after_call_relief_telop.png",
    "06_follow_guidance_telop.png",
    "07_confirm_guidance_telop.png",
    "08_check_contact_beforehand_telop.png",
    "09_save_for_exam_day_telop.png",
    "10_follow_cta_prepared_departure_telop.png",
]

# 画像・テロップと一対一に対応する、音声専用の読み上げ原稿。
DISPLAY_NARRATION = [
    "検査の予約、遅れそう…。",
    "電車が遅れて、間に合いそうにない。",
    "そんなときは、迷ったらまず、予約票の連絡先を確認しましょう。",
    "予約した窓口や、案内された電話番号に連絡すれば大丈夫です。",
    "遅れてしまって申し訳ないと、気を使いすぎなくても大丈夫です。",
    "対応は、施設や検査によって異なります。",
    "到着前に連絡して、案内を確認しましょう。",
    "予約票の連絡先を、事前に確認しておくと安心です。",
    "検査前日に見返せるよう、この投稿を保存しておいてください。",
    "検査前後の小さな迷いに答える発信を続けています。次の投稿も、フォローで。",
]
VOICE_TEXT = DISPLAY_NARRATION[:]


def run(command: list[Path | str]) -> None:
    subprocess.run([str(value) for value in command], check=True)


def post_json(path: str, params: dict | None = None, payload: dict | None = None) -> bytes:
    query = urllib.parse.urlencode(params or {})
    url = f"{VOICEVOX}{path}" + (f"?{query}" if query else "")
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST")
    if body is not None:
        request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def synthesize(text: str, output: Path) -> None:
    query = json.loads(post_json("/audio_query", {"text": text, "speaker": SPEAKER}))
    query.update({
        "speedScale": VOICE_SPEED,
        "pitchScale": 0.0,
        "intonationScale": 0.95,
        "volumeScale": 1.0,
        "prePhonemeLength": 0.04,
        "postPhonemeLength": 0.08,
    })
    output.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav_file:
        return wav_file.getnframes() / wav_file.getframerate()


def media_info(path: Path) -> dict:
    result = subprocess.run([str(FFMPEG), "-i", str(path)], capture_output=True)
    output = result.stderr.decode("utf-8", errors="ignore")
    duration = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", output)
    resolution = re.search(r"Video:.*?(\d{3,4})x(\d{3,4})", output)
    if duration is None or resolution is None:
        raise RuntimeError(f"Could not inspect media: {path}")
    hours, minutes, seconds = duration.groups()
    return {
        "duration": int(hours) * 3600 + int(minutes) * 60 + float(seconds),
        "width": int(resolution.group(1)),
        "height": int(resolution.group(2)),
        "has_audio": "Audio:" in output,
    }


def concat_list(paths: list[Path], destination: Path) -> None:
    destination.write_text("".join(f"file '{path.as_posix()}'\n" for path in paths), encoding="utf-8")


def main() -> None:
    for directory in [AUDIO_DIR, WORK_DIR, VIDEO_DIR, FINAL_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

    frame_paths = [FRAME_DIR / name for name in FRAMES]
    for required in [FFMPEG, BGM, *frame_paths]:
        if not required.exists():
            raise FileNotFoundError(required)

    padded_wavs: list[Path] = []
    voice_durations: list[float] = []
    cut_durations: list[float] = []
    for index, text in enumerate(VOICE_TEXT, start=1):
        voice = AUDIO_DIR / f"voice_{index:02d}.wav"
        padded = WORK_DIR / f"voice_{index:02d}_padded.wav"
        synthesize(text, voice)
        voice_duration = wav_duration(voice)
        cut_duration = max(MIN_DURATION, voice_duration + TAIL_SECONDS)
        run([
            FFMPEG, "-y", "-i", voice,
            "-af", f"apad=pad_dur={cut_duration:.3f},atrim=duration={cut_duration:.3f}",
            "-ar", "44100", "-ac", "2", padded,
        ])
        voice_durations.append(voice_duration)
        cut_durations.append(cut_duration)
        padded_wavs.append(padded)

    segments: list[Path] = []
    for index, (frame, duration) in enumerate(zip(frame_paths, cut_durations), start=1):
        segment = WORK_DIR / f"segment_{index:02d}.mp4"
        run([
            FFMPEG, "-y", "-loop", "1", "-t", f"{duration:.3f}", "-i", frame,
            "-vf", "scale=1080:1920,format=yuv420p", "-r", "30",
            "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p", segment,
        ])
        segments.append(segment)

    voice_list = WORK_DIR / "voice_segments.txt"
    video_list = WORK_DIR / "video_segments.txt"
    concat_list(padded_wavs, voice_list)
    concat_list(segments, video_list)
    voice_all = AUDIO_DIR / "voice_all.wav"
    silent_video = WORK_DIR / "silent_video.mp4"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", voice_list, "-c", "copy", voice_all])
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", video_list, "-c", "copy", silent_video])
    run([
        FFMPEG, "-y", "-i", silent_video, "-i", voice_all, "-stream_loop", "-1", "-i", BGM,
        "-filter_complex",
        f"[1:a]volume=1.45[voice];[2:a]volume={BGM_VOLUME}[bgm];"
        "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,alimiter=limit=0.95[a]",
        "-map", "0:v", "-map", "[a]", "-shortest", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", OUT,
    ])
    shutil.copy2(OUT, FINAL_OUT)

    video_info = media_info(OUT)
    video_duration = video_info["duration"]
    voice_duration = wav_duration(voice_all)
    qa = {
        "resolution": f"{video_info['width']}x{video_info['height']}",
        "has_audio_stream": video_info["has_audio"],
        "video_duration_seconds": round(video_duration, 3),
        "voice_duration_seconds": round(voice_duration, 3),
        "audio_video_duration_difference_seconds": round(abs(video_duration - voice_duration), 3),
        "voice_to_frame_mapping": "one narration segment per matching telop frame",
        "duration_strategy": "each frame remains through its matching narration plus only 0.05 seconds; no fixed long silent pause",
    }
    manifest = {
        "title": TITLE,
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": VOICE_SPEED,
        "bgm": str(BGM),
        "bgm_volume": BGM_VOLUME,
        "tail_seconds_per_cut": TAIL_SECONDS,
        "frames": [str(path) for path in frame_paths],
        "display_narration": DISPLAY_NARRATION,
        "voice_text": VOICE_TEXT,
        "voice_durations_seconds": [round(value, 3) for value in voice_durations],
        "cut_durations_seconds": [round(value, 3) for value in cut_durations],
        "voice_audio": str(voice_all),
        "asset_video": str(OUT),
        "final_video": str(FINAL_OUT),
        "qa": qa,
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8-sig")
    print(json.dumps({"video": str(OUT), "final": str(FINAL_OUT), "qa": qa}, ensure_ascii=False))


if __name__ == "__main__":
    main()
