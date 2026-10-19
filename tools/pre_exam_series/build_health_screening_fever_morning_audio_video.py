from __future__ import annotations

import json
import math
import re
import shutil
import struct
import subprocess
import urllib.parse
import urllib.request
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
UNIT = ROOT / "reel_assets" / "pre_exam_series" / "health_screening_fever_morning_20261019_samples"
TELOP_DIR = UNIT / "telop"
AUDIO_DIR = UNIT / "audio"
WORK_DIR = UNIT / "_video_work"
VIDEO_DIR = UNIT / "video"
FINAL_DIR = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形"
PRODUCTION_MANIFEST = UNIT / "production_manifest.md"
TELOP_MANIFEST = TELOP_DIR / "telop_manifest.json"
VIDEO_MANIFEST = VIDEO_DIR / "video_manifest.json"
QA_REPORT = VIDEO_DIR / "video_qa.json"
MIDFRAME_SHEET = VIDEO_DIR / "video_qa_midframes.png"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = (
    ROOT
    / "01_ショート動画_リール_YouTubeShorts"
    / "インスタリール用"
    / "BGM フリー素材"
    / "Kind_Heart.mp3"
)
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
BGM_VOLUME = "-27dB"
BETWEEN_CUT_TAIL = 0.0
FINAL_TAIL = 1.0
MAX_PUNCTUATION_PAUSE = 0.20

TITLE = "健診の朝_熱っぽい_そのまま行っていい_20261019"
OUT = VIDEO_DIR / f"{TITLE}.mp4"
FINAL_OUT = FINAL_DIR / OUT.name

FRAMES = [
    "telop_01_call_before_visit.png",
    "telop_02_hesitate_before_call.png",
    "telop_03_screening_not_diagnosis.png",
    "telop_04_schedule_change.png",
    "telop_05_facility_rules.png",
    "telop_06_call_to_confirm.png",
    "telop_07_describe_symptoms.png",
    "telop_08_speak_without_hesitation.png",
    "telop_09_phone_phrase.png",
    "telop_10_save_phone_note.png",
]

DISPLAY_NARRATION = [
    "健診の朝に熱っぽい時は、行く前に予約先へ連絡してください。",
    "行っていいのか迷うし、連絡するのも気が引けるかもしれません。",
    "健診は、今ある発熱や風邪症状を診断するための検査ではありません。",
    "そのため、発熱や風邪の症状があるときは、日程の変更を案内する施設があります。",
    "受けられるかどうかの基準は、施設によって違います。",
    "来院の前に連絡すると、受診できるか、日程の変更を確認できます。",
    "熱があるか、どんな症状があるかを、そのまま伝えてください。",
    "言い出しにくくても、体調のことは遠慮なく伝えてください。",
    "予約先には、こう伝えてみてください。朝から熱っぽいです。今日は受けられるか、日程の変更はできるか、教えてください。",
    "この一文を保存しておくと、当日の朝も慌てず電話できます。",
]

# This script has no special reading substitutions because the approved narration
# contains no terms listed in voice-rules.md that require kana conversion.
VOICE_TEXT = DISPLAY_NARRATION.copy()


def run(cmd: list[Path | str], *, capture: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(part) for part in cmd],
        check=True,
        capture_output=capture,
        text=capture,
        encoding="utf-8" if capture else None,
        errors="ignore" if capture else None,
    )


def post_json(path: str, params=None, payload=None) -> bytes:
    query = urllib.parse.urlencode(params or {})
    url = f"{VOICEVOX}{path}" + (f"?{query}" if query else "")
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST")
    if body is not None:
        request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def synthesize_voice(text: str, output: Path) -> dict[str, object]:
    query = json.loads(post_json("/audio_query", {"text": text, "speaker": SPEAKER}))
    original_pauses = []
    adjusted_pauses = []
    for phrase in query.get("accent_phrases", []):
        pause_mora = phrase.get("pause_mora")
        if pause_mora is None:
            continue
        original = float(pause_mora.get("vowel_length", 0.0))
        original_pauses.append(original)
        if original > MAX_PUNCTUATION_PAUSE:
            pause_mora["vowel_length"] = MAX_PUNCTUATION_PAUSE
        adjusted_pauses.append(float(pause_mora.get("vowel_length", 0.0)))
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
    output.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))
    return {
        "kana": query.get("kana"),
        "original_pause_mora_seconds": original_pauses,
        "adjusted_pause_mora_seconds": adjusted_pauses,
    }


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as image_file:
        header = image_file.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"PNGとして読めません: {path}")
    return struct.unpack(">II", header[16:24])


def media_info(path: Path) -> dict:
    completed = subprocess.run([str(FFMPEG), "-hide_banner", "-i", str(path)], capture_output=True)
    details = completed.stderr.decode("utf-8", errors="ignore")
    duration = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", details)
    resolution = re.search(r"Video:.*?\b(\d{2,5})x(\d{2,5})\b", details)
    if duration is None:
        raise RuntimeError(f"Could not read duration: {path}")
    hours, minutes, seconds = duration.groups()
    return {
        "duration_seconds": round(int(hours) * 3600 + int(minutes) * 60 + float(seconds), 3),
        "resolution": [int(resolution.group(1)), int(resolution.group(2))] if resolution else None,
        "has_audio": "Audio:" in details,
    }


def cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    scale = max(size[0] / image.width, size[1] / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = (resized.width - size[0]) // 2
    top = (resized.height - size[1]) // 2
    return resized.crop((left, top, left + size[0], top + size[1]))


def verify_source_lock(frame_paths: list[Path]) -> tuple[list[str], list[dict]]:
    manifest_text = PRODUCTION_MANIFEST.read_text(encoding="utf-8-sig")
    approved = re.findall(r"\|\s*\d{2}\s*\|\s*`([A-Za-z]:\\[^`]+\.png)`", manifest_text)
    telop_items = json.loads(TELOP_MANIFEST.read_text(encoding="utf-8-sig"))
    telop_sources = [item["source"] for item in telop_items]
    telop_outputs = [str(Path(item["output"])) for item in telop_items]
    expected_outputs = [str(path) for path in frame_paths]
    if len(approved) != 10 or len(telop_items) != 10:
        raise RuntimeError("Expected exactly ten approved sources and ten telop items.")
    if approved != telop_sources:
        raise RuntimeError("Production manifest and telop source order differ.")
    if telop_outputs != expected_outputs:
        raise RuntimeError("Telop manifest and requested frame order differ.")
    if not all(Path(path).exists() for path in approved) or not all(path.exists() for path in frame_paths):
        raise FileNotFoundError("An approved source or telop frame is missing.")
    if any(png_size(path) != (1080, 1920) for path in frame_paths):
        raise RuntimeError("A telop frame is not 1080x1920.")
    prohibited = ("_archive_", "capcut_exports", "codex_generated_images", "reference_photos", "character_references")
    if any(any(part in path.lower() for part in prohibited) for path in approved):
        raise RuntimeError("A prohibited source area was detected.")
    return approved, telop_items


def detect_silences(audio: Path, duration_threshold: float = 0.45) -> list[dict]:
    completed = subprocess.run(
        [
            str(FFMPEG),
            "-hide_banner",
            "-i",
            str(audio),
            "-af",
            f"silencedetect=noise=-42dB:d={duration_threshold}",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
    )
    details = completed.stderr.decode("utf-8", errors="ignore")
    starts = [float(value) for value in re.findall(r"silence_start: ([0-9.]+)", details)]
    ends = [
        (float(end), float(duration))
        for end, duration in re.findall(r"silence_end: ([0-9.]+) \| silence_duration: ([0-9.]+)", details)
    ]
    return [
        {"start": round(start, 3), "end": round(end, 3), "duration": round(duration, 3)}
        for start, (end, duration) in zip(starts, ends)
    ]


def make_midframe_sheet(video: Path, durations: list[float]) -> None:
    thumbs = []
    elapsed = 0.0
    for index, duration in enumerate(durations, start=1):
        timestamp = elapsed + duration / 2
        thumb = WORK_DIR / f"midframe_{index:02d}.jpg"
        run(
            [
                FFMPEG,
                "-y",
                "-loglevel",
                "error",
                "-ss",
                f"{timestamp:.3f}",
                "-i",
                video,
                "-frames:v",
                "1",
                "-q:v",
                "2",
                thumb,
            ]
        )
        thumbs.append((thumb, timestamp))
        elapsed += duration

    columns = 5
    thumb_w, thumb_h, label_h = 216, 384, 40
    rows = math.ceil(len(thumbs) / columns)
    sheet = Image.new("RGB", (columns * thumb_w, rows * (thumb_h + label_h)), (244, 246, 248))
    font = ImageFont.truetype(str(FONT_PATH), 20)
    draw = ImageDraw.Draw(sheet)
    for index, (path, timestamp) in enumerate(thumbs):
        image = cover(Image.open(path).convert("RGB"), (thumb_w, thumb_h))
        x = (index % columns) * thumb_w
        y = (index // columns) * (thumb_h + label_h)
        sheet.paste(image, (x, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill="white")
        draw.text((x + 8, y + thumb_h + 8), f"{index + 1:02d} {timestamp:.1f}s", font=font, fill=(12, 34, 64))
    sheet.save(MIDFRAME_SHEET, quality=94)


def main() -> None:
    for directory in (AUDIO_DIR, WORK_DIR, VIDEO_DIR, FINAL_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    frame_paths = [TELOP_DIR / name for name in FRAMES]
    for required in (FFMPEG, BGM, FONT_PATH, PRODUCTION_MANIFEST, TELOP_MANIFEST):
        if not required.exists():
            raise FileNotFoundError(required)
    approved_sources, telop_items = verify_source_lock(frame_paths)
    if not (len(FRAMES) == len(DISPLAY_NARRATION) == len(VOICE_TEXT) == 10):
        raise RuntimeError("Frame and narration counts must match.")
    urllib.request.urlopen(f"{VOICEVOX}/version", timeout=5).read()

    padded_wavs: list[Path] = []
    segment_paths: list[Path] = []
    raw_durations: list[float] = []
    cut_durations: list[float] = []
    voice_queries: list[dict[str, object]] = []

    for index, (frame, text) in enumerate(zip(frame_paths, VOICE_TEXT), start=1):
        voice = AUDIO_DIR / f"voice_{index:02d}.wav"
        padded = WORK_DIR / f"voice_{index:02d}_padded.wav"
        voice_query = synthesize_voice(text, voice)
        voice_query["cut"] = index
        voice_query["text"] = text
        voice_queries.append(voice_query)
        raw_duration = wav_duration(voice)
        tail = FINAL_TAIL if index == len(FRAMES) else BETWEEN_CUT_TAIL
        cut_duration = raw_duration + tail
        raw_durations.append(raw_duration)
        cut_durations.append(cut_duration)
        run(
            [
                FFMPEG,
                "-y",
                "-loglevel",
                "error",
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
        padded_wavs.append(padded)

        segment = WORK_DIR / f"segment_{index:02d}.mp4"
        run(
            [
                FFMPEG,
                "-y",
                "-loglevel",
                "error",
                "-loop",
                "1",
                "-t",
                f"{cut_duration:.3f}",
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
        segment_paths.append(segment)

    voice_list = WORK_DIR / "voice_segments.txt"
    video_list = WORK_DIR / "video_segments.txt"
    voice_list.write_text("".join(f"file '{path.as_posix()}'\n" for path in padded_wavs), encoding="utf-8")
    video_list.write_text("".join(f"file '{path.as_posix()}'\n" for path in segment_paths), encoding="utf-8")
    voice_all = AUDIO_DIR / "voice_all.wav"
    silent_video = WORK_DIR / "silent.mp4"
    run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", voice_list, "-c", "copy", voice_all])
    run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", video_list, "-c", "copy", silent_video])
    run(
        [
            FFMPEG,
            "-y",
            "-loglevel",
            "error",
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
            OUT,
        ]
    )
    shutil.copy2(OUT, FINAL_OUT)
    make_midframe_sheet(OUT, cut_durations)

    video_info = media_info(OUT)
    voice_info = media_info(voice_all)
    composite_silences = detect_silences(voice_all)
    per_cut_silences = [
        {"cut": index, "silences_over_0_45_seconds": detect_silences(AUDIO_DIR / f"voice_{index:02d}.wav")}
        for index in range(1, 11)
    ]
    total = sum(cut_durations)
    cut_map = []
    elapsed = 0.0
    for index, duration in enumerate(cut_durations, start=1):
        cut_map.append(
            {
                "cut": index,
                "start": round(elapsed, 3),
                "voice_end": round(elapsed + raw_durations[index - 1], 3),
                "end": round(elapsed + duration, 3),
                "duration": round(duration, 3),
                "approved_source": approved_sources[index - 1],
                "telop": telop_items[index - 1]["telop"],
                "telop_frame": str(frame_paths[index - 1]),
                "narration": DISPLAY_NARRATION[index - 1],
            }
        )
        elapsed += duration

    audio_manifest = {
        "voice_engine": "VOICEVOX",
        "speaker_id": SPEAKER,
        "voice_speed": VOICE_SPEED,
        "pre_phoneme_length": 0.0,
        "post_phoneme_length": 0.0,
        "max_punctuation_pause_seconds": MAX_PUNCTUATION_PAUSE,
        "between_cut_tail_seconds": BETWEEN_CUT_TAIL,
        "final_bgm_only_tail_seconds": FINAL_TAIL,
        "voice_text": VOICE_TEXT,
        "voice_queries": voice_queries,
        "raw_voice_seconds": [round(value, 3) for value in raw_durations],
        "voice_files": [str(AUDIO_DIR / f"voice_{index:02d}.wav") for index in range(1, 11)],
        "combined_voice": str(voice_all),
    }
    (AUDIO_DIR / "audio_manifest.json").write_text(
        json.dumps(audio_manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig"
    )

    manifest = {
        "title": TITLE,
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": VOICE_SPEED,
        "bgm": str(BGM),
        "bgm_volume": BGM_VOLUME,
        "approved_sources": approved_sources,
        "telop_frames": [str(path) for path in frame_paths],
        "display_narration": DISPLAY_NARRATION,
        "voice_text": VOICE_TEXT,
        "raw_voice_seconds": [round(value, 3) for value in raw_durations],
        "cut_durations_seconds": [round(value, 3) for value in cut_durations],
        "between_cut_tail_seconds": BETWEEN_CUT_TAIL,
        "final_bgm_only_tail_seconds": FINAL_TAIL,
        "total_planned_seconds": round(total, 3),
        "voice_audio": str(voice_all),
        "asset_video": str(OUT),
        "final_video": str(FINAL_OUT),
        "midframe_qa_sheet": str(MIDFRAME_SHEET),
        "cut_map": cut_map,
    }
    VIDEO_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig")

    qa = {
        "source_lock_verified": True,
        "frame_narration_count": 10,
        "one_to_one_mapping_verified": True,
        "video": video_info,
        "voice_audio": voice_info,
        "duration_difference_seconds": round(abs(video_info["duration_seconds"] - voice_info["duration_seconds"]), 3),
        "added_gap_between_cuts_seconds": BETWEEN_CUT_TAIL,
        "final_bgm_only_tail_seconds": FINAL_TAIL,
        "detected_combined_voice_silences_over_0_45_seconds": composite_silences,
        "detected_per_cut_silences_over_0_45_seconds": per_cut_silences,
        "note": "Each approved telop frame is held for its matching narration. No fixed silent gap is inserted between cuts. The final frame remains for 1.0 second with BGM.",
    }
    QA_REPORT.write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(f"source lock verified: {len(approved_sources)} images")
    print(f"voice/frame mapping verified: {len(frame_paths)} cuts")
    print(f"planned={total:.3f}s voice={voice_info['duration_seconds']:.3f}s video={video_info['duration_seconds']:.3f}s")
    print(f"combined silences over 0.45s: {len(composite_silences)}")
    print(OUT)
    print(FINAL_OUT)
    print(MIDFRAME_SHEET)
    print(QA_REPORT)


if __name__ == "__main__":
    main()
