from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
UNIT = ROOT / "reel_assets" / "ct_series" / "ct_contrast_kidney_consult_v1_images"
PRODUCTION_MANIFEST = UNIT / "production_manifest.md"
TELOP_MANIFEST = UNIT / "telop_frames" / "telop_manifest.json"
AUDIO_DIR = UNIT / "audio"
WORK_DIR = UNIT / "video_work"
QA_DIR = UNIT / "video_qa"
ASSET_OUT = UNIT / "造影CTの話が出たら_腎臓について何を伝える.mp4"
FINAL_OUT = (
    ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形" / ASSET_OUT.name
)
VIDEO_MANIFEST = UNIT / "video_manifest.json"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = (
    ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用"
    / "BGM フリー素材" / "Kind_Heart.mp3"
)
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"
VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20  # もち子さん・ノーマル
VOICE_SPEED = 1.15
VOICE_INTONATION = 1.07
VOICE_PAUSE_SCALE = 0.9
BGM_VOLUME = "-25dB"
FINAL_BGM_TAIL = 1.0

# The approved narration is kept in cut order. Pronunciation-only substitutions
# are used in the text sent to VOICEVOX.
NARRATION = [
    "造影CTの話なら、腎臓のことを医師に伝えて。",
    "造影剤を使えるのか、気になりますよね。",
    "伝えるのは、腎臓の病気や腎機能の低下を指摘されたことです。",
    "造影CTでは、施設が定める期間内の採血結果で腎機能を確認します。",
    "その期間や、結果がないときの対応は施設によって違います。",
    "最近の採血結果が手元にあれば、診察で医師に見せてください。",
    "造影剤を使うかどうかは、医師が判断します。",
    "数値を覚えていなくても、腎臓について言われたことを伝えて大丈夫です。",
    "採血結果が手元になくても、診察で医師に相談してください。",
    "診察では「腎臓が悪いと言われたことがありますが、造影CTの前に確認することはありますか？」と聞いてみてください。",
    "この聞き方を保存して診察前に見返し、よければフォローしてください。",
]

VOICE_TEXT = [
    "ぞうえいシーティーの話なら、腎臓のことを医師に伝えて。",
    "造影剤を使えるのか、気になりますよね。",
    "伝えるのは、腎臓の病気や腎機能の低下を指摘されたことです。",
    "ぞうえいシーティーでは、施設が定める期間内の採血結果で腎機能を確認します。",
    "その期間や、結果がないときの対応は施設によって違います。",
    "最近の採血結果が手元にあれば、診察で医師に見せてください。",
    "造影剤を使うかどうかは、医師が判断します。",
    "数値を覚えていなくても、腎臓について言われたことを伝えて大丈夫です。",
    "採血結果が手元になくても、診察で医師に相談してください。",
    "診察では、こう聞いてみてください。腎臓が悪いと言われたことがありますが、ぞうえいシーティーの前に、確認することはありますか。",
    "この聞き方を保存して診察前に見返し、よければフォローしてください。",
]


def run(command: list[Path | str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(part) for part in command],
        check=True,
        capture_output=capture,
        text=capture,
        encoding="utf-8",
        errors="replace",
    )


def post_json(path: str, params: dict | None = None, payload: dict | None = None) -> bytes:
    query = urllib.parse.urlencode(params or {})
    url = f"{VOICEVOX}{path}" + (f"?{query}" if query else "")
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST")
    if body is not None:
        request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def locked_frames() -> tuple[list[Path], list[dict], list[Path]]:
    if len(NARRATION) != 11 or len(VOICE_TEXT) != 11:
        raise ValueError("Narration must have exactly 11 segments")
    if not PRODUCTION_MANIFEST.is_file() or not TELOP_MANIFEST.is_file():
        raise FileNotFoundError("A production or telop manifest is missing")
    section = PRODUCTION_MANIFEST.read_text(encoding="utf-8-sig").split("## Approved Images", 1)[1]
    section = section.split("## Character Clothing Lock", 1)[0]
    entries = re.findall(r"^\|\s*(\d{2})\s*\|\s*`([^`]+)`\s*\|", section, re.M)
    if len(entries) != 11 or [cut for cut, _ in entries] != [f"{n:02d}" for n in range(1, 12)]:
        raise ValueError("Approved image count or order is not 01-11")
    sources = [Path(path) for _, path in entries]
    telops = json.loads(TELOP_MANIFEST.read_text(encoding="utf-8-sig"))
    if len(telops) != 11 or [item["cut"] for item in telops] != [f"{n:02d}" for n in range(1, 12)]:
        raise ValueError("Telop count or order is not 01-11")
    frames = []
    for source, telop in zip(sources, telops, strict=True):
        frame = Path(telop["output"])
        if source.resolve() != Path(telop["source"]).resolve():
            raise ValueError(f"Telop source differs from approved source: {source}")
        if not source.is_file() or not frame.is_file():
            raise FileNotFoundError(source if not source.is_file() else frame)
        frames.append(frame)
    if len(set(frames)) != 11:
        raise ValueError("A telop frame is repeated")
    return frames, telops, sources


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as audio:
        return audio.getnframes() / audio.getframerate()


def concat_list(paths: list[Path], output: Path) -> None:
    output.write_text("".join(f"file '{path.as_posix()}'\n" for path in paths), encoding="utf-8")


def synthesize_voice(text: str, output: Path, query_output: Path) -> None:
    query = json.loads(post_json("/audio_query", {"text": text, "speaker": SPEAKER}))
    query.update({
        "speedScale": VOICE_SPEED,
        "pitchScale": 0.0,
        "intonationScale": VOICE_INTONATION,
        "pauseLengthScale": VOICE_PAUSE_SCALE,
        "prePhonemeLength": 0.03,
        "postPhonemeLength": 0.08,
        "volumeScale": 1.0,
    })
    query_output.write_text(json.dumps(query, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    output.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def generate_audio() -> tuple[list[Path], list[float], Path]:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    voices = []
    durations = []
    for index, text in enumerate(VOICE_TEXT, start=1):
        voice = AUDIO_DIR / f"voice_{index:02d}.wav"
        query = AUDIO_DIR / f"query_{index:02d}.json"
        synthesize_voice(text, voice, query)
        voices.append(voice)
        durations.append(wav_duration(voice))
    voice_list = WORK_DIR / "voice_segments.txt"
    concat_list(voices, voice_list)
    narration = AUDIO_DIR / "narration.wav"
    run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", voice_list, "-c", "copy", narration])
    return voices, durations, narration


def load_audio() -> tuple[list[Path], list[float], Path]:
    voices = [AUDIO_DIR / f"voice_{i:02d}.wav" for i in range(1, 12)]
    narration = AUDIO_DIR / "narration.wav"
    if any(not path.is_file() for path in voices) or not narration.is_file():
        raise FileNotFoundError("VOICEVOX audio has not been generated")
    queries = [json.loads((AUDIO_DIR / f"query_{i:02d}.json").read_text(encoding="utf-8-sig")) for i in range(1, 12)]
    if any(query.get("speedScale") != VOICE_SPEED for query in queries):
        raise ValueError(f"VOICEVOX speedScale differs from {VOICE_SPEED}")
    return voices, [wav_duration(path) for path in voices], narration


def detect_long_silences(audio: Path) -> list[dict]:
    completed = run([
        FFMPEG, "-hide_banner", "-i", audio, "-af", "silencedetect=noise=-42dB:d=0.8",
        "-f", "null", "-",
    ], capture=True)
    starts = [float(value) for value in re.findall(r"silence_start: ([0-9.]+)", completed.stderr)]
    endings = [
        (float(end), float(duration))
        for end, duration in re.findall(r"silence_end: ([0-9.]+) \| silence_duration: ([0-9.]+)", completed.stderr)
    ]
    return [
        {"start": round(start, 3), "end": round(end, 3), "duration": round(duration, 3)}
        for start, (end, duration) in zip(starts, endings)
    ]


def probe_duration(media: Path) -> float:
    completed = subprocess.run(
        [str(FFMPEG), "-hide_banner", "-i", str(media)],
        check=False, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    match = re.search(r"Duration: (\d+):(\d+):([0-9.]+)", completed.stderr)
    if not match:
        raise ValueError(f"Cannot probe duration: {media}")
    hour, minute, second = match.groups()
    return int(hour) * 3600 + int(minute) * 60 + float(second)


def make_video_sample_sheet(video: Path, durations: list[float]) -> Path:
    QA_DIR.mkdir(parents=True, exist_ok=True)
    elapsed = 0.0
    samples = []
    for index, duration in enumerate(durations, start=1):
        sample = QA_DIR / f"sample_{index:02d}.png"
        run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{elapsed + duration / 2:.3f}", "-i", video, "-frames:v", "1", sample])
        samples.append(sample)
        elapsed += duration
    thumb_w, thumb_h, label_h, columns = 270, 480, 38, 3
    rows = math.ceil(len(samples) / columns)
    sheet = Image.new("RGB", (thumb_w * columns, (thumb_h + label_h) * rows), (247, 249, 250))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(str(FONT_PATH), 22)
    for i, sample in enumerate(samples):
        x = (i % columns) * thumb_w
        y = (i // columns) * (thumb_h + label_h)
        image = Image.open(sample).resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        sheet.paste(image, (x, y))
        draw.text((x + 10, y + thumb_h + 4), f"CUT {i + 1:02d}", font=font, fill=(16, 36, 55))
    output = QA_DIR / "contact_sheet_video_samples.png"
    sheet.save(output)
    return output


def build_video(frames: list[Path], telops: list[dict], sources: list[Path]) -> None:
    voices, durations, narration = load_audio()
    if not BGM.is_file():
        raise FileNotFoundError(BGM)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    video_durations = durations.copy()
    video_durations[-1] += FINAL_BGM_TAIL
    segments = []
    for index, (frame, duration) in enumerate(zip(frames, video_durations, strict=True), start=1):
        segment = WORK_DIR / f"segment_{index:02d}.mp4"
        run([
            FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-loop", "1", "-t", f"{duration:.3f}",
            "-i", frame, "-vf", "scale=1080:1920,format=yuv420p", "-r", "30",
            "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p", segment,
        ])
        segments.append(segment)
    video_list = WORK_DIR / "video_segments.txt"
    concat_list(segments, video_list)
    silent_video = WORK_DIR / "silent.mp4"
    run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", video_list, "-c", "copy", silent_video])

    total_duration = sum(video_durations)
    fade_start = max(0.0, total_duration - 0.8)
    audio_filter = (
        f"[1:a]apad=pad_dur={FINAL_BGM_TAIL:.3f},atrim=duration={total_duration:.3f},volume=1.4[voice];"
        f"[2:a]volume={BGM_VOLUME},afade=t=out:st={fade_start:.3f}:d=0.8[bgm];"
        "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
        "alimiter=limit=0.95[a]"
    )
    run([
        FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", silent_video,
        "-i", narration, "-stream_loop", "-1", "-i", BGM,
        "-filter_complex", audio_filter, "-map", "0:v", "-map", "[a]",
        "-t", f"{total_duration:.3f}", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", ASSET_OUT,
    ])
    silence = detect_long_silences(narration)
    measured = probe_duration(ASSET_OUT)
    if abs(measured - total_duration) > 0.12:
        raise ValueError(f"Video duration mismatch: expected {total_duration:.3f}, got {measured:.3f}")
    sheet = make_video_sample_sheet(ASSET_OUT, video_durations)
    FINAL_OUT.parent.mkdir(parents=True, exist_ok=True)
    staged_final = FINAL_OUT.with_name(f"{FINAL_OUT.stem}__new{FINAL_OUT.suffix}")
    shutil.copy2(ASSET_OUT, staged_final)
    staged_final.replace(FINAL_OUT)
    VIDEO_MANIFEST.write_text(json.dumps({
        "title": "造影CTの話が出たら、腎臓について何を伝える？",
        "speaker": "VOICEVOX もち子さん・ノーマル (style id 20)",
        "speedScale": VOICE_SPEED,
        "video_speed_change": False,
        "intonationScale": VOICE_INTONATION,
        "pauseLengthScale": VOICE_PAUSE_SCALE,
        "final_bgm_only_tail_seconds": FINAL_BGM_TAIL,
        "bgm": str(BGM),
        "bgm_volume": BGM_VOLUME,
        "cut_mapping": [
            {
                "cut": f"{i:02d}",
                "source_image": str(source),
                "telop_frame": str(frame),
                "telop_text": telop["telop"],
                "narration_text": narration_text,
                "voice_input_text": voice_text,
                "voice_file": str(voice),
                "voice_duration_seconds": round(duration, 3),
                "video_duration_seconds": round(video_duration, 3),
            }
            for i, (source, frame, telop, narration_text, voice_text, voice, duration, video_duration)
            in enumerate(zip(sources, frames, telops, NARRATION, VOICE_TEXT, voices, durations, video_durations, strict=True), start=1)
        ],
        "narration_duration_seconds": round(sum(durations), 3),
        "target_video_duration_seconds": round(total_duration, 3),
        "measured_video_duration_seconds": round(measured, 3),
        "detected_long_silences": silence,
        "narration_audio": str(narration),
        "asset_video": str(ASSET_OUT),
        "final_video": str(FINAL_OUT),
        "video_sample_sheet": str(sheet),
    }, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(f"narration_seconds={sum(durations):.3f}")
    print(f"video_seconds={measured:.3f}")
    print(f"long_silences={len(silence)}")
    print(FINAL_OUT)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("audio", "video"))
    args = parser.parse_args()
    if not FFMPEG.is_file():
        raise FileNotFoundError(FFMPEG)
    frames, telops, sources = locked_frames()
    if args.phase == "audio":
        _, durations, narration = generate_audio()
        print(f"created 11 voice segments; narration_seconds={sum(durations):.3f}")
        print(narration)
    else:
        build_video(frames, telops, sources)


if __name__ == "__main__":
    main()
