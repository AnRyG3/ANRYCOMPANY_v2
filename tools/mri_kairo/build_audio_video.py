from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
import urllib.parse
import urllib.request
import wave
from pathlib import Path


ROOT = Path(r"F:\ANRYCAMPANY")
UNIT = ROOT / "reel_assets" / "mri_series" / "mri_kairo_20261109"
MANIFEST = UNIT / "production_manifest.md"
TELOP_DETAILS = UNIT / "telop_frames" / "telop_details.json"
TELOP_DIR = UNIT / "telop_frames"
AUDIO_DIR = UNIT / "audio"
VIDEO_DIR = UNIT / "video"
WORK_DIR = VIDEO_DIR / "_work"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
VOICEVOX = "http://127.0.0.1:50021"
SPEAKER_NAME = "もち子さん"
SPEAKER_STYLE = "ノーマル"
SPEAKER_ID = 20
SPEED_SCALE = 1.15  # User instruction; never change playback speed in ffmpeg.
INTONATION_SCALE = 1.03
FPS = 30
BETWEEN_CUT_TAIL = 0.03
FINAL_BGM_TAIL = 1.0
BGM_VOLUME = "-30dB"
VIDEO = VIDEO_DIR / "MRI_貼るカイロ_20261109_review.mp4"

# Display narration keeps approved wording. Voice-only text fixes MRI reading.
DISPLAY_TEXT = [
    "MRI前、貼るカイロは検査担当者に伝えてください。",
    "寒い日に貼ったまま来てしまうのは、おかしくありません。",
    "MRIでは、検査室に持ち込めない物があります。",
    "カイロも、検査前に外すよう案内されています。",
    "背中や腰など、服の下に貼っていると、自分でも忘れていることがあります。",
    "検査の前には、身につけている物を確認する流れがあります。",
    "外す場所や手順は病院ごとに違うので、スタッフの案内に沿えば大丈夫です。",
    "迷ったときは、検査担当者に聞いて大丈夫です。",
    "検査担当者には、こう伝えてみてください。カイロを貼っているのですが、どうすればいいか教えてください。",
    "検査前に見返せるよう、保存しておいてください。",
]
VOICE_TEXT = [text.replace("MRI", "エムアールアイ") for text in DISPLAY_TEXT]


def run(parts: list[str | Path], *, capture: bool = False) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run([str(part) for part in parts], check=True, capture_output=capture)


def voicevox_json(path: str, params: dict | None = None, payload: dict | None = None) -> bytes:
    query = urllib.parse.urlencode(params or {})
    url = f"{VOICEVOX}{path}" + (f"?{query}" if query else "")
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST" if body is not None or path == "/audio_query" else "GET")
    if body is not None:
        request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def verify_speaker() -> None:
    speakers = json.loads(voicevox_json("/speakers"))
    for speaker in speakers:
        if speaker["name"] == SPEAKER_NAME:
            if any(style["name"] == SPEAKER_STYLE and style["id"] == SPEAKER_ID for style in speaker["styles"]):
                return
    raise RuntimeError("VOICEVOX もち子さん／ノーマル speaker id 20 was not found")


def approved_frames() -> list[Path]:
    content = MANIFEST.read_text(encoding="utf-8-sig")
    approved = re.findall(r"^\|\s*(\d{2})\s*\|\s*`([A-Z]:\\[^`]+\.png)`\s*\|", content, re.M)
    if [number for number, _ in approved] != [f"{n:02d}" for n in range(1, 11)]:
        raise RuntimeError("production_manifest.md must lock exactly 10 images in cut order")
    details = json.loads(TELOP_DETAILS.read_text(encoding="utf-8"))["frames"]
    if len(details) != len(approved) or len(details) != len(DISPLAY_TEXT):
        raise RuntimeError("Source, telop, and narration counts differ")
    outputs = []
    for index, ((_, source), detail) in enumerate(zip(approved, details), 1):
        image = Path(source)
        telop = TELOP_DIR / f"telop_{index:02d}.png"
        if detail["cut"] != index or Path(detail["source"]) != image or Path(detail["output"]) != telop:
            raise RuntimeError(f"Cut {index:02d} source/telop order differs from source lock")
        if not image.is_file() or not telop.is_file():
            raise FileNotFoundError(f"Missing source or telop for cut {index:02d}")
        if hashlib.sha256(image.read_bytes()).hexdigest() != detail["source_sha256"]:
            raise RuntimeError(f"Approved source image changed for cut {index:02d}")
        if detail["font_size_px"] != 64 or detail["x_center"] != 540:
            raise RuntimeError(f"Telop style mismatch in cut {index:02d}")
        outputs.append(telop)
    return outputs


def synthesize(text: str, destination: Path) -> dict:
    query = json.loads(voicevox_json("/audio_query", {"text": text, "speaker": SPEAKER_ID}))
    query["speedScale"] = SPEED_SCALE
    query["intonationScale"] = INTONATION_SCALE
    query["volumeScale"] = 1.0
    destination.write_bytes(voicevox_json("/synthesis", {"speaker": SPEAKER_ID}, query))
    return query


def wav_data(path: Path) -> tuple[int, int, int, int, bytes]:
    with wave.open(str(path), "rb") as wav:
        channels, sample_width, rate, count = (
            wav.getnchannels(), wav.getsampwidth(), wav.getframerate(), wav.getnframes()
        )
        return channels, sample_width, rate, count, wav.readframes(count)


def save_concat_list(paths: list[Path], destination: Path) -> None:
    destination.write_text("".join(f"file '{path.as_posix()}'\n" for path in paths), encoding="utf-8")


def detect_long_silences(path: Path, before_seconds: float) -> list[dict]:
    result = subprocess.run(
        [str(FFMPEG), "-hide_banner", "-i", str(path), "-af", "silencedetect=noise=-42dB:d=0.85", "-f", "null", "NUL"],
        capture_output=True,
    )
    output = result.stderr.decode("utf-8", errors="ignore")
    starts = [float(value) for value in re.findall(r"silence_start:\s*([0-9.]+)", output)]
    ends = [(float(a), float(b)) for a, b in re.findall(r"silence_end:\s*([0-9.]+)\s*\|\s*silence_duration:\s*([0-9.]+)", output)]
    return [
        {"start": round(start, 3), "end": round(end, 3), "duration": round(duration, 3)}
        for start, (end, duration) in zip(starts, ends)
        if end <= before_seconds
    ]


def main() -> None:
    frames = approved_frames()
    for required in (FFMPEG, BGM):
        if not required.is_file():
            raise FileNotFoundError(required)
    verify_speaker()
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)

    queries: list[dict] = []
    voices: list[Path] = []
    voice_seconds: list[float] = []
    cut_frame_counts: list[int] = []
    audio_parts: list[bytes] = []
    wav_format: tuple[int, int, int] | None = None
    for index, text in enumerate(VOICE_TEXT, 1):
        path = AUDIO_DIR / f"voice_{index:02d}.wav"
        queries.append(synthesize(text, path))
        voices.append(path)
        channels, sample_width, rate, count, data = wav_data(path)
        current_format = (channels, sample_width, rate)
        if wav_format is None:
            wav_format = current_format
        elif current_format != wav_format:
            raise RuntimeError("VOICEVOX returned inconsistent WAV formats")
        duration = count / rate
        voice_seconds.append(duration)
        extra = FINAL_BGM_TAIL if index == len(VOICE_TEXT) else BETWEEN_CUT_TAIL
        frame_count = math.ceil((duration + extra) * FPS)
        cut_frame_counts.append(frame_count)
        target_audio_frames = round(frame_count * rate / FPS)
        if target_audio_frames < count:
            raise RuntimeError("Audio cut is shorter than narration")
        audio_parts.append(data + b"\0" * ((target_audio_frames - count) * channels * sample_width))

    assert wav_format is not None
    channels, sample_width, rate = wav_format
    full_audio = AUDIO_DIR / "narration_full.wav"
    with wave.open(str(full_audio), "wb") as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(sample_width)
        wav.setframerate(rate)
        wav.writeframes(b"".join(audio_parts))

    segments = []
    for index, (frame, frame_count) in enumerate(zip(frames, cut_frame_counts), 1):
        segment = WORK_DIR / f"segment_{index:02d}.mp4"
        run([
            FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
            "-loop", "1", "-framerate", str(FPS), "-i", frame,
            "-frames:v", str(frame_count), "-c:v", "libx264", "-preset", "veryfast",
            "-tune", "stillimage", "-crf", "20", "-pix_fmt", "yuv420p", "-an", segment,
        ])
        segments.append(segment)

    video_list = WORK_DIR / "video_segments.txt"
    silent_video = WORK_DIR / "silent_video.mp4"
    save_concat_list(segments, video_list)
    run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", video_list, "-c", "copy", silent_video])

    total_seconds = sum(cut_frame_counts) / FPS
    bgm_fade_start = max(0.0, total_seconds - 0.7)
    filter_graph = (
        f"[1:a]volume=1.0[voice];"
        f"[2:a]volume={BGM_VOLUME},afade=t=out:st={bgm_fade_start:.3f}:d=0.7[bgm];"
        "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
        "alimiter=limit=0.95[a]"
    )
    run([
        FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
        "-i", silent_video, "-i", full_audio, "-stream_loop", "-1", "-i", BGM,
        "-filter_complex", filter_graph, "-map", "0:v", "-map", "[a]",
        "-t", f"{total_seconds:.3f}", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", VIDEO,
    ])

    timing = []
    start = 0.0
    for index, (voice, frame_count) in enumerate(zip(voice_seconds, cut_frame_counts), 1):
        end = start + frame_count / FPS
        timing.append({
            "cut": index, "start_seconds": round(start, 3), "end_seconds": round(end, 3),
            "voice_duration_seconds": round(voice, 3), "display_duration_seconds": round(frame_count / FPS, 3),
            "telop": str(frames[index - 1]), "voice": str(voices[index - 1]),
        })
        start = end

    long_silences = detect_long_silences(full_audio, total_seconds - FINAL_BGM_TAIL)
    report = {
        "speaker": SPEAKER_NAME,
        "style": SPEAKER_STYLE,
        "speaker_id": SPEAKER_ID,
        "voicevox_speedScale": SPEED_SCALE,
        "video_playback_speed": 1.0,
        "intonationScale": INTONATION_SCALE,
        "display_text": DISPLAY_TEXT,
        "voice_text": VOICE_TEXT,
        "voice_queries": queries,
        "cut_timing": timing,
        "video_duration_seconds": round(total_seconds, 3),
        "long_silences_before_final_tail": long_silences,
        "bgm": str(BGM),
        "bgm_volume": BGM_VOLUME,
        "voice_only_audio": str(full_audio),
        "review_video": str(VIDEO),
    }
    (AUDIO_DIR / "narration_script.txt").write_text(
        "\n".join(f"{i:02d}. {line}" for i, line in enumerate(DISPLAY_TEXT, 1)) + "\n",
        encoding="utf-8-sig",
    )
    (VIDEO_DIR / "video_manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "video": str(VIDEO), "duration_seconds": round(total_seconds, 3),
        "voice_durations_seconds": [round(value, 3) for value in voice_seconds],
        "long_silences_before_final_tail": long_silences,
        "speedScale": SPEED_SCALE,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
