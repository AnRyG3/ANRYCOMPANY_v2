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
ASSET_DIR = ROOT / "reel_assets" / "pre_exam_series"
FRAME_DIR = ASSET_DIR / "21_heattech_under_gown_v1_telop"
AUDIO_DIR = ASSET_DIR / "21_heattech_under_gown_v1_audio"
WORK_DIR = ASSET_DIR / "21_heattech_under_gown_v1_video_work"
VIDEO_DIR = ASSET_DIR / "21_heattech_under_gown_v1_video"
FINAL_DIR = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
TAIL_SECONDS = 0.06
MIN_DURATION = 1.25
BGM_VOLUME = "-27dB"

TITLE = "検査着の下_ヒートテック_20260922"
OUT = VIDEO_DIR / f"{TITLE}.mp4"
FINAL_OUT = FINAL_DIR / OUT.name
MANIFEST = ASSET_DIR / "21_heattech_under_gown_v1_video_manifest.json"

FRAMES = [
    "frame_01_question_telop.png",
    "frame_02_cold_day_telop.png",
    "frame_03_ask_before_changing_telop.png",
    "frame_04_material_check_telop.png",
    "frame_05_exam_type_telop.png",
    "frame_06_mri_telop.png",
    "frame_07_reassurance_telop.png",
    "frame_08_show_and_confirm_telop.png",
    "frame_09_asking_is_welcome_telop.png",
    "frame_10_save_cta_telop.png",
]

DISPLAY_NARRATION = [
    "検査着の下。ヒートテック、着たままでいいかな。",
    "寒い日に、ヒートテックを着てきたら、気になりますよね。",
    "着替える前に、ひと声かければ大丈夫です。",
    "素材によっては、確認が必要なこともあります。",
    "検査の種類や撮影部位で、対応は変わります。",
    "MRIでは、脱ぐのが基本です。",
    "防寒のために着てきても、気にしなくて大丈夫です。",
    "見せて、このままで大丈夫ですか、と確認すれば大丈夫です。",
    "確認することは、面倒なお願いではありません。",
    "検査前日に見返せるよう、保存しておいてください。",
]

# Kana and punctuation are deliberately chosen for stable VOICEVOX reading.
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
    query.update(
        {
            "speedScale": VOICE_SPEED,
            "pitchScale": 0.0,
            "intonationScale": 0.95,
            "volumeScale": 1.0,
            "prePhonemeLength": 0.03,
            "postPhonemeLength": 0.04,
        }
    )
    output.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav_file:
        return wav_file.getnframes() / wav_file.getframerate()


def concat_list(paths: list[Path], destination: Path) -> None:
    destination.write_text("".join(f"file '{path.as_posix()}'\n" for path in paths), encoding="utf-8")


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
        run(
            [
                FFMPEG,
                "-y",
                "-i",
                voice,
                "-af",
                f"apad=pad_dur={cut_duration:.3f},atrim=duration={cut_duration:.3f}",
                "-ar",
                "44100",
                "-ac",
                "2",
                padded,
            ]
        )
        voice_durations.append(voice_duration)
        cut_durations.append(cut_duration)
        padded_wavs.append(padded)

    segments: list[Path] = []
    for index, (frame, duration) in enumerate(zip(frame_paths, cut_durations), start=1):
        segment = WORK_DIR / f"segment_{index:02d}.mp4"
        run(
            [
                FFMPEG,
                "-y",
                "-loop",
                "1",
                "-t",
                f"{duration:.3f}",
                "-i",
                frame,
                "-vf",
                "scale=1080:1920,format=yuv420p",
                "-r",
                "30",
                "-c:v",
                "libx264",
                "-tune",
                "stillimage",
                "-pix_fmt",
                "yuv420p",
                segment,
            ]
        )
        segments.append(segment)

    voice_list = WORK_DIR / "voice_segments.txt"
    video_list = WORK_DIR / "video_segments.txt"
    voice_all = AUDIO_DIR / "voice_all.wav"
    silent_video = WORK_DIR / "silent_video.mp4"
    concat_list(padded_wavs, voice_list)
    concat_list(segments, video_list)
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", voice_list, "-c", "copy", voice_all])
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", video_list, "-c", "copy", silent_video])
    run(
        [
            FFMPEG,
            "-y",
            "-i",
            silent_video,
            "-i",
            voice_all,
            "-stream_loop",
            "-1",
            "-i",
            BGM,
            "-filter_complex",
            f"[1:a]volume=1.45[voice];[2:a]volume={BGM_VOLUME}[bgm];"
            "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,alimiter=limit=0.95[a]",
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
            "-movflags",
            "+faststart",
            OUT,
        ]
    )
    shutil.copy2(OUT, FINAL_OUT)

    info = media_info(OUT)
    total_voice_duration = wav_duration(voice_all)
    qa = {
        "resolution": f"{info['width']}x{info['height']}",
        "has_audio_stream": info["has_audio"],
        "video_duration_seconds": round(info["duration"], 3),
        "voice_duration_seconds": round(total_voice_duration, 3),
        "audio_video_duration_difference_seconds": round(abs(info["duration"] - total_voice_duration), 3),
        "frame_count": len(FRAMES),
        "narration_segment_count": len(VOICE_TEXT),
        "voice_to_frame_mapping": "one narration segment per matching telop frame",
        "duration_strategy": "voice duration plus 0.06 seconds per frame; no fixed long silent gaps",
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
