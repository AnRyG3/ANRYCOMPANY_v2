from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave
from pathlib import Path


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "ct_series" / "ct_previous_hospital_contrast_v1_samples"
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
FINAL_BGM_TAIL_SECONDS = 1.0
BGM_VOLUME = "-25dB"
TITLE = "20261006_前の病院でCTを撮ったのに_また造影CT"
OUT = VIDEO_DIR / f"{TITLE}.mp4"
FINAL_OUT = FINAL_DIR / f"{TITLE}.mp4"
MANIFEST = ASSET_DIR / "video_manifest.json"

FRAMES = [
    "01_hook_patient_ct_room_telop.png",
    "02_ct_room_injector_telop.png",
    "03_injector_detail_telop.png",
    "04_ct_room_wide_telop.png",
    "05_patient_waiting_telop.png",
    "06_patient_corridor_telop.png",
    "07_patient_reception_telop.png",
    "08_patient_ct_room_telop.png",
]

DISPLAY_NARRATION = [
    "前の病院でCTを撮ったのに、また造影CT？",
    "単純CTだけでは分からないことがないか、造影CTで確認することがあります。",
    "造影剤を使うと、血管や臓器、病変の見え方が変わります。",
    "必要な情報に応じて、造影CTを追加することがあります。",
    "前の病院でCTを撮っていても、今回の診察で確認したいことがあれば、造影CTを行うことがあります。",
    "造影CTが必要かどうかは、医師が判断します。",
    "以前、造影剤で気分が悪くなったことがある方は、事前に伝えてください。",
    "気になることがあれば、検査前にスタッフへ確認してください。",
]

# Voice-only text: kana is used where the engine could misread the words.
VOICE_TEXT = [
    "前の病院でしーてぃーを撮ったのに、またぞうえいしーてぃーになると、気になりますよね。",
    "たんじゅんしーてぃーだけでは、分からないことがないか。ぞうえいしーてぃーで、確認することがあります。",
    "ぞうえいざいを使うと、けっかんやぞうき、びょうへんの見え方が変わります。",
    "必要な情報に応じて、ぞうえいしーてぃーを追加することがあります。",
    "前の病院でしーてぃーを撮っていても、今回の診察で確認したいことがあれば、ぞうえいしーてぃーを行うことがあります。",
    "ぞうえいしーてぃーが必要かどうかは、医師が判断します。",
    "以前、ぞうえいざいで気分が悪くなったことがあるかたは、事前に伝えてください。",
    "気になることがあれば、検査前にスタッフへ確認してください。",
]


def run(command: list[Path | str], capture: bool = False, check: bool = True) -> subprocess.CompletedProcess[str] | None:
    result = subprocess.run(
        [str(part) for part in command],
        check=check,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=capture,
    )
    return result if capture else None


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
            "pauseLengthScale": 0.75,
            "prePhonemeLength": 0.03,
            "postPhonemeLength": 0.03,
        }
    )
    output.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav_file:
        return wav_file.getnframes() / wav_file.getframerate()


def write_concat(paths: list[Path], output: Path) -> None:
    output.write_text("".join(f"file '{path.as_posix()}'\n" for path in paths), encoding="utf-8")


def probe_video(path: Path) -> dict:
    result = run([FFMPEG, "-hide_banner", "-i", path], capture=True, check=False)
    details = (result.stdout or "") + (result.stderr or "")
    duration = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", details)
    resolution = re.search(r"Video:.*?(\d{3,4})x(\d{3,4})", details)
    if duration is None or resolution is None:
        raise RuntimeError(f"Could not inspect video: {path}")
    hours, minutes, seconds = duration.groups()
    return {
        "duration_seconds": round(int(hours) * 3600 + int(minutes) * 60 + float(seconds), 3),
        "resolution": f"{resolution.group(1)}x{resolution.group(2)}",
        "has_audio_stream": "Audio:" in details,
    }


def main() -> None:
    for directory in [AUDIO_DIR, WORK_DIR, VIDEO_DIR, QA_DIR, FINAL_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

    frame_paths = [FRAME_DIR / name for name in FRAMES]
    for required in [FFMPEG, BGM, *frame_paths]:
        if not required.exists():
            raise FileNotFoundError(required)
    if OUT.exists() or FINAL_OUT.exists():
        raise FileExistsError("Output already exists; use a new title rather than overwriting.")
    urllib.request.urlopen(f"{VOICEVOX}/version", timeout=5).read()

    voice_paths: list[Path] = []
    voice_durations: list[float] = []
    for index, text in enumerate(VOICE_TEXT, start=1):
        voice_path = AUDIO_DIR / f"voice_{index:02d}.wav"
        synthesize(text, voice_path)
        voice_paths.append(voice_path)
        voice_durations.append(wav_duration(voice_path))

    voice_list = WORK_DIR / "voice_segments.txt"
    write_concat(voice_paths, voice_list)
    voice_all = AUDIO_DIR / "voice_all.wav"
    run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", voice_list, "-c", "copy", voice_all])

    segment_paths: list[Path] = []
    video_durations: list[float] = []
    for index, (frame, voice_duration) in enumerate(zip(frame_paths, voice_durations), start=1):
        duration = math.ceil(voice_duration * 30) / 30
        if index == len(frame_paths):
            duration += FINAL_BGM_TAIL_SECONDS
        segment = WORK_DIR / f"segment_{index:02d}.mp4"
        run(
            [
                FFMPEG, "-y", "-loglevel", "error", "-loop", "1", "-t", f"{duration:.3f}", "-i", frame,
                "-vf", "scale=1080:1920,format=yuv420p", "-r", "30", "-c:v", "libx264",
                "-tune", "stillimage", "-pix_fmt", "yuv420p", segment,
            ]
        )
        segment_paths.append(segment)
        video_durations.append(duration)

    video_list = WORK_DIR / "video_segments.txt"
    write_concat(segment_paths, video_list)
    silent_video = WORK_DIR / "silent_video.mp4"
    run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", video_list, "-c", "copy", silent_video])

    run(
        [
            FFMPEG, "-y", "-loglevel", "error", "-i", silent_video, "-i", voice_all,
            "-stream_loop", "-1", "-i", BGM,
            "-filter_complex",
            f"[1:a]apad=pad_dur={FINAL_BGM_TAIL_SECONDS:.3f},volume=1.35[voice];"
            f"[2:a]volume={BGM_VOLUME}[bgm];"
            "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,alimiter=limit=0.95[a]",
            "-map", "0:v", "-map", "[a]", "-shortest", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", OUT,
        ]
    )
    shutil.copy2(OUT, FINAL_OUT)

    elapsed = 0.0
    qa_frames: list[Path] = []
    for index, duration in enumerate(video_durations, start=1):
        midpoint = elapsed + min(voice_durations[index - 1] / 2, duration / 2)
        qa_frame = QA_DIR / f"qa_mid_{index:02d}.jpg"
        run([FFMPEG, "-y", "-loglevel", "error", "-ss", f"{midpoint:.3f}", "-i", OUT, "-frames:v", "1", qa_frame])
        qa_frames.append(qa_frame)
        elapsed += duration

    video_info = probe_video(OUT)
    expected_audio_duration = sum(voice_durations) + FINAL_BGM_TAIL_SECONDS
    manifest = {
        "title": "前の病院でCTを撮ったのに、また造影CT？",
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": VOICE_SPEED,
        "bgm": str(BGM),
        "bgm_volume": BGM_VOLUME,
        "display_narration": DISPLAY_NARRATION,
        "voice_text": VOICE_TEXT,
        "frames": [str(path) for path in frame_paths],
        "voice_durations_seconds": [round(value, 3) for value in voice_durations],
        "video_durations_seconds": [round(value, 3) for value in video_durations],
        "voice_audio": str(voice_all),
        "asset_video": str(OUT),
        "final_video": str(FINAL_OUT),
        "qa_midframes": [str(path) for path in qa_frames],
        "qa": {
            **video_info,
            "voice_duration_seconds": round(sum(voice_durations), 3),
            "expected_final_duration_seconds": round(expected_audio_duration, 3),
            "audio_video_duration_difference_seconds": round(abs(video_info["duration_seconds"] - expected_audio_duration), 3),
            "frame_narration_mapping": "one telop frame per matching narration segment in cut order",
            "silent_gaps_between_cuts": "none",
            "final_tail": "1.0 second of BGM only after narration ends",
        },
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8-sig")
    print(json.dumps({"video": str(OUT), "final": str(FINAL_OUT), "qa": manifest["qa"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
