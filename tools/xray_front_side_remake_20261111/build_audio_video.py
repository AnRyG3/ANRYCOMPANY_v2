"""Build the approved 9-cut reel with VOICEVOX at speedScale=1.15."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import urllib.parse
import urllib.request
import wave
from pathlib import Path

from PIL import Image


ROOT = Path(r"F:\ANRYCAMPANY")
UNIT = ROOT / "reel_assets" / "xray_front_side_remake_20261111"
SOURCE_MANIFEST = UNIT / "production_manifest.md"
TELOP_QA = UNIT / "telop_frames_v2" / "qa_report.json"
FRAMES = UNIT / "telop_frames_v2"
AUDIO = UNIT / "audio"
WORK = UNIT / "_video_work"
VIDEO = UNIT / "video" / "前回は正面だけ_今日は横向きも_20261111.mp4"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
VOICEVOX = "http://127.0.0.1:50021"
SPEAKER_ID = 20
SPEED_SCALE = 1.15
INTONATION_SCALE = 1.06
FPS = 30
BETWEEN_CUT_SECONDS = 0.06
FINAL_BGM_TAIL_SECONDS = 1.0

# Each spoken paragraph corresponds to one approved text frame. No next-episode line.
NARRATION = [
    "見る方向を増やすことがあります。",
    "前回は正面だけだったのに、今日は横向きも。前と違うと、気になりますよね。",
    "レントゲンは、ひとつの向きだけでは、見えにくいところが出ることがあります。",
    "そのため、横向きなど、別の向きからも撮ることがあります。",
    "撮る向きや枚数は、部位や検査の目的によって変わります。",
    "向きを変えるときは、姿勢を変えてもらうことがあります。",
    "別の向きからも見ることで、見えにくいところを減らせることがあります。",
    "気になるときは、その場で、前回と向きが違うのはなぜですか、と聞いて大丈夫です。",
    "検査の疑問を、これからも分かりやすくお届けします。フォローをお願いします。",
]


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_source_lock() -> list[Path]:
    source_rows = []
    for line in SOURCE_MANIFEST.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\|\s*(\d{2})\s*\|\s*`([^`]+)`\s*\|", line)
        if match:
            source_rows.append((int(match.group(1)), str(Path(match.group(2)))))
    qa = json.loads(TELOP_QA.read_text(encoding="utf-8"))
    if len(source_rows) != 9 or len(qa) != 9 or len(NARRATION) != 9:
        raise RuntimeError("Source, telop, or narration count is not 9")
    frame_paths = []
    for i, ((cut, source), record) in enumerate(zip(source_rows, qa), 1):
        frame = FRAMES / f"telop_{i:02d}.png"
        if cut != i or source != record["source"] or str(frame) != record["output"]:
            raise RuntimeError(f"Manifest/telop order mismatch at cut {i}")
        if not frame.is_file() or hash_file(Path(source)) != record["source_sha256"]:
            raise RuntimeError(f"Approved source or telop missing/changed at cut {i}")
        with Image.open(frame) as image:
            if image.size != (1080, 1920):
                raise RuntimeError(f"Wrong frame size: {frame}")
        frame_paths.append(frame)
    return frame_paths


def request_json(path: str, params: dict | None = None, payload: dict | None = None) -> bytes:
    query = urllib.parse.urlencode(params or {})
    url = f"{VOICEVOX}{path}" + (f"?{query}" if query else "")
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST")
    if body is not None:
        request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def verify_speaker() -> None:
    with urllib.request.urlopen(f"{VOICEVOX}/speakers", timeout=10) as response:
        speakers = json.load(response)
    matches = [speaker for speaker in speakers if speaker.get("name") == "もち子さん"]
    if len(matches) != 1 or not any(
        style.get("id") == SPEAKER_ID and style.get("name") == "ノーマル"
        for style in matches[0].get("styles", [])
    ):
        raise RuntimeError("VOICEVOX speaker 20 is not もち子さん・ノーマル")


def wav_info(path: Path) -> dict:
    with wave.open(str(path), "rb") as wav:
        return {
            "channels": wav.getnchannels(),
            "sample_width": wav.getsampwidth(),
            "sample_rate": wav.getframerate(),
            "samples": wav.getnframes(),
            "duration": wav.getnframes() / wav.getframerate(),
        }


def synthesize_audio() -> None:
    check_source_lock()
    verify_speaker()
    AUDIO.mkdir(parents=True, exist_ok=True)
    records = []
    for i, text in enumerate(NARRATION, 1):
        query = json.loads(request_json("/audio_query", {"text": text, "speaker": SPEAKER_ID}))
        query.update(
            {
                "speedScale": SPEED_SCALE,
                "pitchScale": 0.0,
                "intonationScale": INTONATION_SCALE,
                "volumeScale": 1.0,
                "prePhonemeLength": 0.07,
                "postPhonemeLength": 0.18,
                "pauseLengthScale": 1.0,
            }
        )
        target = AUDIO / f"voice_{i:02d}.wav"
        target.write_bytes(request_json("/synthesis", {"speaker": SPEAKER_ID}, query))
        info = wav_info(target)
        if info["duration"] <= 0.4:
            raise RuntimeError(f"Voice clip too short: {target}")
        tail = FINAL_BGM_TAIL_SECONDS if i == 9 else BETWEEN_CUT_SECONDS
        video_frames = math.ceil((info["duration"] + tail) * FPS)
        records.append(
            {
                "cut": i,
                "text": text,
                "voice_file": str(target),
                "voice_seconds": round(info["duration"], 4),
                "video_frames": video_frames,
                "cut_seconds": round(video_frames / FPS, 4),
                "audio_query": {
                    "speaker_name": "もち子さん",
                    "style": "ノーマル",
                    "speaker_id": SPEAKER_ID,
                    "speedScale": SPEED_SCALE,
                    "intonationScale": INTONATION_SCALE,
                },
            }
        )
        (AUDIO / f"query_{i:02d}.json").write_text(
            json.dumps(query, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"voice_{i:02d}: {info['duration']:.2f}s, cut {video_frames / FPS:.2f}s", flush=True)

    (AUDIO / "voice_plan.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    lines = [
        "# ナレーション（VOICEVOX）",
        "",
        "話者: もち子さん・ノーマル（ID 20）。音声生成時の speedScale=1.15。動画編集で倍速処理なし。次回予告なし。",
        "",
    ]
    lines.extend(f"{i:02d}. {text}" for i, text in enumerate(NARRATION, 1))
    (UNIT / "narration.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(command: list[str | Path], capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(part) for part in command],
        check=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )


def concat_file(paths: list[Path], destination: Path) -> None:
    destination.write_text(
        "".join(f"file '{path.as_posix()}'\n" for path in paths), encoding="utf-8"
    )


def joined_voice(records: list[dict]) -> Path:
    result = AUDIO / "voice.wav"
    specs = [wav_info(Path(record["voice_file"])) for record in records]
    first = specs[0]
    if any(
        (spec["channels"], spec["sample_width"], spec["sample_rate"])
        != (first["channels"], first["sample_width"], first["sample_rate"])
        for spec in specs
    ):
        raise RuntimeError("VOICEVOX clip audio formats differ")
    with wave.open(str(result), "wb") as output:
        output.setnchannels(first["channels"])
        output.setsampwidth(first["sample_width"])
        output.setframerate(first["sample_rate"])
        for record, spec in zip(records, specs):
            with wave.open(record["voice_file"], "rb") as clip:
                output.writeframes(clip.readframes(clip.getnframes()))
            target_samples = round(record["cut_seconds"] * first["sample_rate"])
            pad_samples = target_samples - spec["samples"]
            if pad_samples < 0:
                raise RuntimeError("Frame-rounded cut is shorter than voice")
            output.writeframes(b"\x00" * pad_samples * first["channels"] * first["sample_width"])
    return result


def make_video() -> None:
    frames = check_source_lock()
    records = json.loads((AUDIO / "voice_plan.json").read_text(encoding="utf-8"))
    if len(records) != 9 or any(record["text"] != NARRATION[i] for i, record in enumerate(records)):
        raise RuntimeError("Audio plan differs from current narration")
    for record in records:
        if not Path(record["voice_file"]).is_file():
            raise FileNotFoundError(record["voice_file"])
    if not FFMPEG.is_file() or not BGM.is_file():
        raise FileNotFoundError("ffmpeg or BGM missing")
    WORK.mkdir(parents=True, exist_ok=True)
    VIDEO.parent.mkdir(parents=True, exist_ok=True)
    voice = joined_voice(records)
    total_seconds = sum(record["video_frames"] for record in records) / FPS
    if abs(wav_info(voice)["duration"] - total_seconds) > 0.002:
        raise RuntimeError("Joined voice duration does not match cut durations")

    segments = []
    for i, (frame, record) in enumerate(zip(frames, records), 1):
        segment = WORK / f"scene_{i:02d}.mp4"
        run(
            [
                FFMPEG, "-y", "-loglevel", "error", "-framerate", str(FPS),
                "-loop", "1", "-i", frame, "-frames:v", str(record["video_frames"]),
                "-c:v", "libx264", "-preset", "fast", "-crf", "19",
                "-tune", "stillimage", "-pix_fmt", "yuv420p", "-r", str(FPS), segment,
            ]
        )
        segments.append(segment)
        print(f"scene_{i:02d}: {record['cut_seconds']:.2f}s", flush=True)

    video_list = WORK / "scenes.txt"
    silent_video = WORK / "silent_video.mp4"
    concat_file(segments, video_list)
    run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", video_list,
         "-c", "copy", silent_video])
    fade_start = max(0.0, total_seconds - 0.9)
    filter_graph = (
        "[1:a]volume=1.0[voice];"
        f"[2:a]volume=-30dB,afade=t=out:st={fade_start:.3f}:d=0.9[bgm];"
        "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
        "alimiter=limit=0.95[a]"
    )
    run(
        [
            FFMPEG, "-y", "-loglevel", "error", "-i", silent_video,
            "-i", voice, "-stream_loop", "-1", "-i", BGM,
            "-filter_complex", filter_graph, "-map", "0:v", "-map", "[a]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
            "-t", f"{total_seconds:.3f}", VIDEO,
        ]
    )
    run([FFMPEG, "-v", "error", "-i", VIDEO, "-f", "null", "-"], capture=True)
    report = {
        "video": str(VIDEO),
        "resolution": "1080x1920",
        "fps": FPS,
        "duration_seconds": round(total_seconds, 3),
        "speaker": "もち子さん・ノーマル",
        "speaker_id": SPEAKER_ID,
        "speedScale": SPEED_SCALE,
        "editing_speed_change": False,
        "bgm": str(BGM),
        "bgm_gain": "-30dB",
        "final_bgm_only_tail_seconds": FINAL_BGM_TAIL_SECONDS,
        "narration": NARRATION,
        "cuts": records,
        "telop_frames": [str(path) for path in frames],
        "telop_frame_sha256": [hash_file(path) for path in frames],
    }
    (UNIT / "audio_video_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"VIDEO {VIDEO} {total_seconds:.2f}s", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True, choices=("audio", "video"))
    args = parser.parse_args()
    if args.stage == "audio":
        synthesize_audio()
    else:
        make_video()


if __name__ == "__main__":
    main()
