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
ASSET_ROOT = ROOT / "reel_assets" / "mri_series"
TELOP_DIR = ASSET_ROOT / "mri_sleep_20261007_telop_frames"
AUDIO_DIR = ASSET_ROOT / "mri_sleep_20261007_audio"
VIDEO_DIR = ASSET_ROOT / "mri_sleep_20261007_video"
WORK_DIR = VIDEO_DIR / "_work"
PRODUCTION_MANIFEST = ASSET_ROOT / "mri_sleep_20261007_images" / "production_manifest.md"
TELOP_MANIFEST = TELOP_DIR / "telop_manifest.json"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = (
    ROOT
    / "01_ショート動画_リール_YouTubeShorts"
    / "インスタリール用"
    / "BGM フリー素材"
    / "Kind_Heart.mp3"
)
VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
INTERCUT_TAIL_SECONDS = 0.02
FINAL_TAIL_SECONDS = 1.0
BGM_VOLUME = "-27dB"

ASSET_VIDEO = VIDEO_DIR / "MRI中_寝てもいい_20261007.mp4"
FINAL_VIDEO = (
    ROOT
    / "01_ショート動画_リール_YouTubeShorts"
    / "インスタ完成形"
    / "MRI中_寝てもいい_20261007.mp4"
)

FRAME_FILES = [
    "telop_01_hook.png",
    "telop_02_may_sleep.png",
    "telop_03_motion_blur.png",
    "telop_04_staff_voice.png",
    "telop_05_breath_hold.png",
    "telop_06_stay_awake.png",
    "telop_07_tell_before_exam.png",
    "telop_08_question_phrase.png",
    "telop_09_ask_staff.png",
    "telop_10_follow.png",
]

DISPLAY_NARRATION = [
    "MRI中、寝てもいいのでしょうか。検査によっては、大丈夫です。",
    "頭や背骨、関節などの検査では、眠ってもよい場合があります。",
    "ただし、眠って体が動くと、画像がぶれることがあります。",
    "そのときは、検査中に声をかける場合もあります。",
    "お腹などの検査では、息止めの合図が必要なこともあります。",
    "その場合は、起きているようお願いすることがあります。",
    "眠ってしまいそうで心配なら、検査前に伝えてください。",
    "確認するときは、息止めの合図はありますか、と聞いてみてください。",
    "自分の検査で合図があるか、担当者に確認できます。",
    "検査前の疑問に答える動画を発信しています。よければ、フォローしてください。",
]

# Voice-only text keeps the acronym reading explicit and avoids a stretched question ending.
VOICE_TEXT = [
    "エムアールアイ中、寝てもいいのでしょうか。検査によっては、大丈夫です。",
    "頭や背骨、関節などの検査では、眠ってもよい場合があります。",
    "ただし、眠って体が動くと、画像がぶれることがあります。",
    "そのときは、検査中に声をかける場合もあります。",
    "お腹などの検査では、息止めの合図が必要なこともあります。",
    "その場合は、起きているようお願いすることがあります。",
    "眠ってしまいそうで心配なら、検査前に伝えてください。",
    "確認するときは、息止めの合図はありますか、と聞いてみてください。",
    "自分の検査で合図があるか、担当者に確認できます。",
    "検査前の疑問に答える動画を発信しています。よければ、フォローしてください。",
]


def run(command: list[str | Path], *, capture: bool = False) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [str(part) for part in command], check=True, capture_output=capture
    )


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


def synthesize(text: str, output: Path) -> dict:
    query = json.loads(post_json("/audio_query", {"text": text, "speaker": SPEAKER}))
    query.update(
        {
            "speedScale": VOICE_SPEED,
            "pitchScale": 0.0,
            "intonationScale": 0.95,
            "volumeScale": 1.0,
            "prePhonemeLength": 0.0,
            "postPhonemeLength": 0.0,
        }
    )
    if "pauseLengthScale" in query:
        query["pauseLengthScale"] = 0.85
    output.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))
    return query


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav_file:
        return wav_file.getnframes() / wav_file.getframerate()


def probe_media(path: Path) -> dict:
    result = subprocess.run([str(FFMPEG), "-i", str(path)], capture_output=True)
    output = result.stderr.decode("utf-8", errors="ignore")
    duration_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", output)
    video_match = re.search(r"Video:\s*([^,]+).*?,\s*(\d{2,5})x(\d{2,5})", output)
    audio_match = re.search(r"Audio:\s*([^,]+)", output)
    fps_match = re.search(r"(\d+(?:\.\d+)?)\s*fps", output)
    if not duration_match:
        raise RuntimeError(f"Could not determine duration: {path}")
    hours, minutes, seconds = duration_match.groups()
    info = {
        "duration_seconds": int(hours) * 3600 + int(minutes) * 60 + float(seconds),
        "has_video": video_match is not None,
        "has_audio": audio_match is not None,
    }
    if video_match:
        info.update(
            {
                "video_codec": video_match.group(1).strip(),
                "width": int(video_match.group(2)),
                "height": int(video_match.group(3)),
                "fps": float(fps_match.group(1)) if fps_match else None,
            }
        )
    if audio_match:
        info["audio_codec"] = audio_match.group(1).strip()
    return info


def concat_list(paths: list[Path], destination: Path) -> None:
    destination.write_text(
        "".join(f"file '{path.as_posix()}'\n" for path in paths), encoding="utf-8"
    )


def assert_source_lock() -> tuple[list[Path], list[dict]]:
    markdown = PRODUCTION_MANIFEST.read_text(encoding="utf-8")
    approved_section = markdown.split("## Approved Images", 1)[1].split(
        "## Character Clothing Lock", 1
    )[0]
    approved_images = re.findall(r"`([A-Za-z]:\\[^`]+\.png)`", approved_section)
    telop_data = json.loads(TELOP_MANIFEST.read_text(encoding="utf-8-sig"))
    telop_frames = telop_data["frames"]
    telop_sources = [frame["source"] for frame in telop_frames]
    telop_outputs = [Path(frame["output"]) for frame in telop_frames]
    expected_outputs = [TELOP_DIR / name for name in FRAME_FILES]
    if approved_images != telop_sources:
        raise RuntimeError("Approved image order and telop source order do not match.")
    if telop_outputs != expected_outputs:
        raise RuntimeError("Telop output order and video cut order do not match.")
    if len(expected_outputs) != len(VOICE_TEXT) or not all(path.exists() for path in expected_outputs):
        raise RuntimeError("Frame count, narration count, or required telop files are invalid.")
    return expected_outputs, telop_frames


def find_long_silences(path: Path) -> list[dict]:
    result = subprocess.run(
        [
            str(FFMPEG),
            "-i",
            str(path),
            "-af",
            "silencedetect=noise=-42dB:d=0.65",
            "-f",
            "null",
            "NUL",
        ],
        capture_output=True,
    )
    output = result.stderr.decode("utf-8", errors="ignore")
    starts = [float(value) for value in re.findall(r"silence_start:\s*([0-9.]+)", output)]
    ends = [
        (float(end), float(duration))
        for end, duration in re.findall(
            r"silence_end:\s*([0-9.]+)\s*\|\s*silence_duration:\s*([0-9.]+)", output
        )
    ]
    return [
        {"start": round(start, 3), "end": round(end, 3), "duration": round(duration, 3)}
        for start, (end, duration) in zip(starts, ends)
    ]


def main() -> None:
    frame_paths, telop_frames = assert_source_lock()
    for directory in [AUDIO_DIR, VIDEO_DIR, WORK_DIR, FINAL_VIDEO.parent]:
        directory.mkdir(parents=True, exist_ok=True)
    for required in [FFMPEG, BGM, *frame_paths]:
        if not required.exists():
            raise FileNotFoundError(required)

    voice_paths: list[Path] = []
    padded_paths: list[Path] = []
    voice_durations: list[float] = []
    cut_durations: list[float] = []
    voice_queries: list[dict] = []
    for index, text in enumerate(VOICE_TEXT, start=1):
        voice = AUDIO_DIR / f"voice_{index:02d}.wav"
        padded = WORK_DIR / f"voice_{index:02d}_padded.wav"
        voice_queries.append(synthesize(text, voice))
        voice_duration = wav_duration(voice)
        extra = FINAL_TAIL_SECONDS if index == len(VOICE_TEXT) else INTERCUT_TAIL_SECONDS
        cut_duration = voice_duration + extra
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
        voice_paths.append(voice)
        padded_paths.append(padded)
        voice_durations.append(voice_duration)
        cut_durations.append(cut_duration)

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
    concat_list(padded_paths, voice_list)
    concat_list(segments, video_list)
    narration_audio = AUDIO_DIR / "narration_full.wav"
    silent_video = WORK_DIR / "silent_video.mp4"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", voice_list, "-c", "copy", narration_audio])
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", video_list, "-c", "copy", silent_video])
    run(
        [
            FFMPEG,
            "-y",
            "-i",
            silent_video,
            "-i",
            narration_audio,
            "-stream_loop",
            "-1",
            "-i",
            BGM,
            "-filter_complex",
            f"[1:a]volume=1.45[voice];[2:a]volume={BGM_VOLUME}[bgm];"
            "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
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
            "-movflags",
            "+faststart",
            ASSET_VIDEO,
        ]
    )
    shutil.copy2(ASSET_VIDEO, FINAL_VIDEO)

    media_info = probe_media(ASSET_VIDEO)
    narration_info = probe_media(narration_audio)
    long_silences = find_long_silences(narration_audio)
    mappings = []
    for index, (frame, telop, display, voice, duration) in enumerate(
        zip(frame_paths, telop_frames, DISPLAY_NARRATION, VOICE_TEXT, cut_durations), start=1
    ):
        mappings.append(
            {
                "cut": index,
                "telop_frame": str(frame),
                "telop": telop["telop"],
                "display_narration": display,
                "voice_text": voice,
                "duration_seconds": round(duration, 3),
                "match": True,
            }
        )

    qa = {
        "cut_count": len(frame_paths),
        "narration_segment_count": len(VOICE_TEXT),
        "voice_to_image_mapping": "one matching narration segment per approved telop frame in cut order",
        "intercut_added_tail_seconds": INTERCUT_TAIL_SECONDS,
        "final_visual_tail_seconds": FINAL_TAIL_SECONDS,
        "narration_long_silences_over_0_65_seconds": long_silences,
        "video_duration_seconds": round(media_info["duration_seconds"], 3),
        "narration_duration_seconds": round(narration_info["duration_seconds"], 3),
        "resolution": [media_info.get("width"), media_info.get("height")],
        "fps": media_info.get("fps"),
        "video_codec": media_info.get("video_codec"),
        "audio_codec": media_info.get("audio_codec"),
        "audio_stream_present": media_info["has_audio"],
    }
    manifest = {
        "title": "MRI中、寝てもいい？",
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": VOICE_SPEED,
        "display_narration": DISPLAY_NARRATION,
        "voice_text": VOICE_TEXT,
        "voice_queries": voice_queries,
        "voice_files": [str(path) for path in voice_paths],
        "voice_durations_seconds": [round(value, 3) for value in voice_durations],
        "cut_durations_seconds": [round(value, 3) for value in cut_durations],
        "frame_audio_mapping": mappings,
        "narration_audio": str(narration_audio),
        "asset_video": str(ASSET_VIDEO),
        "final_video": str(FINAL_VIDEO),
        "qa": qa,
    }
    (VIDEO_DIR / "video_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8-sig"
    )
    (AUDIO_DIR / "narration_script.txt").write_text(
        "\n".join(f"{index:02d}. {text}" for index, text in enumerate(DISPLAY_NARRATION, start=1))
        + "\n",
        encoding="utf-8-sig",
    )
    print(ASSET_VIDEO)
    print(FINAL_VIDEO)
    print(json.dumps(qa, ensure_ascii=False))


if __name__ == "__main__":
    main()
