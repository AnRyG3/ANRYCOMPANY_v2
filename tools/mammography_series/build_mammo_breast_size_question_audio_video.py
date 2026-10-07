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
UNIT = ROOT / "reel_assets" / "mammography_series" / "mammo_breast_size_question_v1"
TELOP_DIR = UNIT / "telop_frames"
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
INTERCUT_TAIL_SECONDS = 0.03
FINAL_TAIL_SECONDS = 1.0
BGM_VOLUME = "-27dB"

ASSET_VIDEO = VIDEO_DIR / "胸が小さいと_マンモで挟めない.mp4"
FINAL_VIDEO = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形" / "胸が小さいと_マンモで挟めない.mp4"

FRAME_FILES = [
    "telop_01_hook_patient.png",
    "telop_02_answer_with_technologist.png",
    "telop_03_position_adjustment.png",
    "telop_04_individual_discomfort.png",
    "telop_05_tell_before_exam.png",
    "telop_06_speak_up_during_exam.png",
    "telop_07_history_preparation.png",
    "telop_08_facility_confirmation.png",
    "telop_09_seek_medical_care.png",
    "telop_10_cta_background.png",
]

DISPLAY_NARRATION = [
    "胸が小さいと、マンモで挟めないのかな、と心配になりますよね。",
    "胸の大きさだけで、受けられないとは決まりません。",
    "撮影では、診療放射線技師が乳房の位置を調整します。",
    "痛みの感じ方には、個人差があります。",
    "不安なことは、撮影前に伝えてください。",
    "撮影中につらくなったら、その場で声をかけてください。",
    "豊胸や乳房の手術歴がある方は、予約時に伝えてください。",
    "撮影できるかどうかは、予約時に検査施設へ確認してください。",
    "しこりなど気になる症状がある方は、検診を待たずに医療機関へ相談してください。",
    "検査前の不安に答える動画を発信しています。よければ、フォローしてください。",
]

# Voice-only substitutions follow voice-rules.md and avoid ambiguous readings.
VOICE_TEXT = [
    "胸が小さいと、マンモで挟めないのかな、と心配になりますよね。",
    "胸の大きさだけで、受けられないとは決まりません。",
    "撮影では、診療放射線技師が、にゅうぼうの位置を調整します。",
    "痛みの感じ方には、個人差があります。",
    "不安なことは、撮影前に伝えてください。",
    "撮影中につらくなったら、その場で声をかけてください。",
    "ほうきょうや、にゅうぼうの手術歴があるかたは、予約時に伝えてください。",
    "撮影できるかどうかは、予約時に検査施設へ確認してください。",
    "しこりなど気になる症状があるかたは、検診を待たずに医療機関へ相談してください。",
    "検査前の不安に答える動画を発信しています。よければ、フォローしてください。",
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


def synthesize(text: str, output: Path) -> None:
    query = json.loads(post_json("/audio_query", {"text": text, "speaker": SPEAKER}))
    query.update(
        {
            "speedScale": VOICE_SPEED,
            "pitchScale": 0.0,
            "intonationScale": 0.95,
            "volumeScale": 1.0,
            "prePhonemeLength": 0.0,
            "postPhonemeLength": INTERCUT_TAIL_SECONDS,
        }
    )
    output.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def probe_with_ffmpeg(path: Path) -> dict:
    result = subprocess.run([str(FFMPEG), "-i", str(path)], capture_output=True)
    output = result.stderr.decode("utf-8", errors="ignore")
    duration_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", output)
    video_match = re.search(r"Video:\s*([^,]+).*?,\s*(\d{2,5})x(\d{2,5})", output)
    audio_match = re.search(r"Audio:\s*([^,]+)", output)
    fps_match = re.search(r"(\d+(?:\.\d+)?)\s*fps", output)
    if not (duration_match and video_match and audio_match):
        raise RuntimeError(f"Could not verify output media streams: {path}")
    hours, minutes, seconds = duration_match.groups()
    return {
        "duration": int(hours) * 3600 + int(minutes) * 60 + float(seconds),
        "video_codec": video_match.group(1).strip(),
        "width": int(video_match.group(2)),
        "height": int(video_match.group(3)),
        "audio_codec": audio_match.group(1).strip(),
        "fps": float(fps_match.group(1)) if fps_match else None,
    }


def concat_list(paths: list[Path], destination: Path) -> None:
    destination.write_text(
        "".join(f"file '{path.as_posix()}'\n" for path in paths), encoding="utf-8"
    )


def assert_source_lock() -> list[Path]:
    markdown = PRODUCTION_MANIFEST.read_text(encoding="utf-8")
    approved_section = markdown.split("## Approved Images", 1)[1].split(
        "## Character Clothing Lock", 1
    )[0]
    approved_images = re.findall(r"`([A-Za-z]:\\[^`]+\.png)`", approved_section)
    telop_data = json.loads(TELOP_MANIFEST.read_text(encoding="utf-8-sig"))
    telop_sources = [frame["source"] for frame in telop_data["frames"]]
    telop_outputs = [Path(frame["output"]) for frame in telop_data["frames"]]
    expected_outputs = [TELOP_DIR / name for name in FRAME_FILES]
    if approved_images != telop_sources:
        raise RuntimeError("Approved image order and telop source order do not match.")
    if telop_outputs != expected_outputs:
        raise RuntimeError("Telop manifest output order does not match the video cut order.")
    if len(expected_outputs) != len(VOICE_TEXT) or not all(path.exists() for path in expected_outputs):
        raise RuntimeError("Frame count, narration count, or required telop files are invalid.")
    return expected_outputs


def main() -> None:
    frame_paths = assert_source_lock()
    for directory in [AUDIO_DIR, WORK_DIR, VIDEO_DIR, FINAL_VIDEO.parent]:
        directory.mkdir(parents=True, exist_ok=True)
    for required in [FFMPEG, BGM, *frame_paths]:
        if not required.exists():
            raise FileNotFoundError(required)

    voices: list[Path] = []
    padded_voices: list[Path] = []
    voice_durations: list[float] = []
    cut_durations: list[float] = []
    for index, text in enumerate(VOICE_TEXT, start=1):
        voice = AUDIO_DIR / f"voice_{index:02d}.wav"
        padded = WORK_DIR / f"voice_{index:02d}_padded.wav"
        synthesize(text, voice)
        duration = wav_duration(voice)
        tail = FINAL_TAIL_SECONDS if index == len(VOICE_TEXT) else INTERCUT_TAIL_SECONDS
        cut_duration = duration + tail
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
        voices.append(voice)
        padded_voices.append(padded)
        voice_durations.append(duration)
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
    concat_list(padded_voices, voice_list)
    concat_list(segments, video_list)
    voice_all = AUDIO_DIR / "voice_all.wav"
    silent_video = WORK_DIR / "silent_video.mp4"
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

    media_info = probe_with_ffmpeg(ASSET_VIDEO)
    qa = {
        "cut_count": len(frame_paths),
        "narration_segment_count": len(VOICE_TEXT),
        "voice_to_image_mapping": "one narration segment per matching approved telop frame in cut order",
        "intercut_fixed_tail_seconds": INTERCUT_TAIL_SECONDS,
        "final_visual_tail_seconds": FINAL_TAIL_SECONDS,
        "video_duration_seconds": round(media_info["duration"], 3),
        "resolution": [media_info["width"], media_info["height"]],
        "frame_rate": media_info["fps"],
        "video_codec": media_info["video_codec"],
        "audio_codec": media_info["audio_codec"],
    }
    manifest = {
        "title": "胸が小さいと、マンモで挟めない？",
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": VOICE_SPEED,
        "display_narration": DISPLAY_NARRATION,
        "voice_text": VOICE_TEXT,
        "telop_frames": [str(path) for path in frame_paths],
        "voice_files": [str(path) for path in voices],
        "voice_durations_seconds": [round(value, 3) for value in voice_durations],
        "cut_durations_seconds": [round(value, 3) for value in cut_durations],
        "narration_audio": str(voice_all),
        "asset_video": str(ASSET_VIDEO),
        "final_video": str(FINAL_VIDEO),
        "qa": qa,
    }
    (VIDEO_DIR / "video_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8-sig"
    )
    print(ASSET_VIDEO)
    print(FINAL_VIDEO)
    print(json.dumps(qa, ensure_ascii=False))


if __name__ == "__main__":
    main()
