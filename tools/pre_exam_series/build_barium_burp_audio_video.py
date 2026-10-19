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

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
UNIT = ROOT / "reel_assets" / "pre_exam_series" / "25_barium_burp_during_exam_v1_samples"
MANIFEST = UNIT / "production_manifest.md"
TELOP_QA = UNIT / "telop_frames" / "telop_qa.json"
AUDIO = UNIT / "audio"
WORK = UNIT / "_video_work"
VIDEO = UNIT / "video"
FINAL_DIR = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
FONT = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"
OUT = VIDEO / "バリウム検査中にゲップが出たら_20261019.mp4"
FINAL = FINAL_DIR / OUT.name
VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
SPEED = 1.2
FPS = 30
FINAL_TAIL = 1.0

DISPLAY_NARRATION = [
    "バリウム検査中にゲップが出たら、その場で担当者に伝えてください。",
    "我慢していたのに出てしまうと、焦りますよね。",
    "検査の前に飲む発泡剤は、胃を膨らませて、画像を見やすくするためのものです。",
    "ゲップが出ると胃の膨らみが減って、画像に影響することがあります。",
    "だから我慢をお願いしていますが、出てしまうことはあります。",
    "撮影している診療放射線技師は、透視モニターで、胃の空気が減ったことが分かります。",
    "対応は、そのときの状況や施設によって違います。",
    "例えば、発泡剤を追加することがあります。",
    "検査中は声を出しにくいかもしれませんが、出たときは「ゲップが出ました」と伝えてみてください。",
    "この一文を保存しておくと、検査の前に思い出せます。",
]
VOICE_TEXT = DISPLAY_NARRATION.copy()
VOICE_TEXT[5] = VOICE_TEXT[5].replace("診療放射線技師", "しんりょうほうしゃせんぎし")


def run(*parts: object) -> None:
    result = subprocess.run([str(part) for part in parts], capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace")[-3000:])


def voicevox(path: str, params: dict | None = None, payload: dict | None = None) -> bytes:
    query = urllib.parse.urlencode(params or {})
    url = VOICEVOX + path + ("?" + query if query else "")
    request = urllib.request.Request(
        url,
        data=None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        method="POST",
    )
    if payload is not None:
        request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def synthesize(text: str, destination: Path) -> dict:
    query = json.loads(voicevox("/audio_query", {"text": text, "speaker": SPEAKER}))
    for phrase in query.get("accent_phrases", []):
        pause = phrase.get("pause_mora")
        if pause and float(pause.get("vowel_length", 0)) > 0.20:
            pause["vowel_length"] = 0.20
    query.update({
        "speedScale": SPEED,
        "pitchScale": 0.0,
        "intonationScale": 0.95,
        "volumeScale": 1.0,
        "prePhonemeLength": 0.0,
        "postPhonemeLength": 0.0,
    })
    destination.write_bytes(voicevox("/synthesis", {"speaker": SPEAKER}, query))
    return {"kana": query.get("kana"), "text": text}


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as audio:
        return audio.getnframes() / audio.getframerate()


def source_lock() -> tuple[list[Path], list[dict]]:
    approved = re.findall(
        r"\|\s*\d{2}\s*\|\s*`([A-Za-z]:\\[^`]+\.png)`",
        MANIFEST.read_text(encoding="utf-8-sig"),
    )
    frames = json.loads(TELOP_QA.read_text(encoding="utf-8-sig"))
    if len(approved) != 10 or len(frames) != 10 or len(DISPLAY_NARRATION) != 10:
        raise RuntimeError("Approved source, telop, and narration counts must all equal ten")
    if approved != [item["source"] for item in frames]:
        raise RuntimeError("Production manifest and telop source order differ")
    if [item["cut"] for item in frames] != [f"{i:02d}" for i in range(1, 11)]:
        raise RuntimeError("Telop cut order differs")
    paths = [Path(item["output"]) for item in frames]
    if any(not Path(path).is_file() for path in approved) or any(not path.is_file() for path in paths):
        raise FileNotFoundError("An approved source or telop frame is missing")
    prohibited = ("_archive_", "capcut_exports", "codex_generated_images", "reference_photos", "character_references")
    if any(any(token in path.lower() for token in prohibited) for path in approved):
        raise RuntimeError("A prohibited source area was detected")
    for path in paths:
        with Image.open(path) as frame:
            if frame.size != (1080, 1920):
                raise RuntimeError(f"Invalid telop dimensions: {path}")
    return paths, frames


def ffmpeg_info(path: Path) -> dict:
    result = subprocess.run([str(FFMPEG), "-hide_banner", "-i", str(path)], capture_output=True)
    output = result.stderr.decode("utf-8", errors="ignore")
    duration = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", output)
    dimensions = re.search(r"Video:.*?\b(\d{2,5})x(\d{2,5})\b", output)
    if not duration:
        raise RuntimeError(f"Could not determine media duration: {path}")
    hour, minute, second = duration.groups()
    return {
        "duration": round(int(hour) * 3600 + int(minute) * 60 + float(second), 3),
        "resolution": [int(dimensions.group(1)), int(dimensions.group(2))] if dimensions else None,
        "audio": "Audio:" in output,
    }


def silences(path: Path, minimum: float = 0.45) -> list[dict]:
    result = subprocess.run(
        [str(FFMPEG), "-hide_banner", "-i", str(path), "-af", f"silencedetect=noise=-42dB:d={minimum}", "-f", "null", "-"],
        capture_output=True,
    )
    details = result.stderr.decode("utf-8", errors="ignore")
    starts = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", details)]
    ends = [(float(end), float(length)) for end, length in re.findall(r"silence_end: ([0-9.]+) \| silence_duration: ([0-9.]+)", details)]
    return [{"start": round(start, 3), "end": round(end, 3), "duration": round(length, 3)}
            for start, (end, length) in zip(starts, ends)]


def contact_sheet(cut_durations: list[float]) -> Path:
    sheet = Image.new("RGB", (1080, 2 * 426), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(str(FONT), 20)
    elapsed = 0.0
    for index, duration in enumerate(cut_durations):
        mid = elapsed + duration / 2
        thumb = WORK / f"mid_{index + 1:02d}.jpg"
        run(FFMPEG, "-y", "-loglevel", "error", "-ss", f"{mid:.3f}", "-i", OUT, "-frames:v", "1", thumb)
        with Image.open(thumb) as frame:
            mini = frame.convert("RGB").resize((216, 384), Image.Resampling.LANCZOS)
        x, y = (index % 5) * 216, (index // 5) * 426
        sheet.paste(mini, (x, y))
        draw.text((x + 8, y + 390), f"{index + 1:02d} {mid:.1f}s", font=font, fill=(12, 34, 64))
        elapsed += duration
    path = VIDEO / "video_qa_midframes.png"
    sheet.save(path)
    return path


def main() -> None:
    for required in (MANIFEST, TELOP_QA, FFMPEG, BGM, FONT):
        if not required.is_file():
            raise FileNotFoundError(required)
    frame_paths, frame_qa = source_lock()
    urllib.request.urlopen(VOICEVOX + "/version", timeout=5).read()
    for folder in (AUDIO, WORK, VIDEO, FINAL_DIR):
        folder.mkdir(parents=True, exist_ok=True)

    raw_durations: list[float] = []
    cut_durations: list[float] = []
    audio_parts: list[Path] = []
    video_parts: list[Path] = []
    voice_queries: list[dict] = []
    for index, (frame, spoken) in enumerate(zip(frame_paths, VOICE_TEXT), 1):
        raw = AUDIO / f"voice_{index:02d}.wav"
        voice_queries.append(synthesize(spoken, raw))
        raw_duration = wav_duration(raw)
        # Frame time is quantized upward by less than 1/30 second, with no fixed gap.
        cut_duration = math.ceil(raw_duration * FPS) / FPS + (FINAL_TAIL if index == 10 else 0.0)
        padded = WORK / f"voice_{index:02d}_padded.wav"
        run(FFMPEG, "-y", "-loglevel", "error", "-i", raw,
            "-af", f"apad=pad_dur={cut_duration:.6f},atrim=duration={cut_duration:.6f}",
            "-ar", "44100", "-ac", "2", padded)
        segment = WORK / f"segment_{index:02d}.mp4"
        run(FFMPEG, "-y", "-loglevel", "error", "-loop", "1", "-t", f"{cut_duration:.6f}",
            "-i", frame, "-vf", "scale=1080:1920,format=yuv420p", "-r", str(FPS),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-tune", "stillimage",
            "-pix_fmt", "yuv420p", segment)
        raw_durations.append(raw_duration)
        cut_durations.append(cut_duration)
        audio_parts.append(padded)
        video_parts.append(segment)
        print(f"cut {index:02d}: voice={raw_duration:.3f}s frame={cut_duration:.3f}s", flush=True)

    audio_list = WORK / "audio_parts.txt"
    video_list = WORK / "video_parts.txt"
    audio_list.write_text("".join(f"file '{p.as_posix()}'\n" for p in audio_parts), encoding="utf-8")
    video_list.write_text("".join(f"file '{p.as_posix()}'\n" for p in video_parts), encoding="utf-8")
    voice_all = AUDIO / "voice_all.wav"
    silent = WORK / "silent_video.mp4"
    run(FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", audio_list, "-c", "copy", voice_all)
    run(FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", video_list, "-c", "copy", silent)
    run(FFMPEG, "-y", "-loglevel", "error", "-i", silent, "-i", voice_all, "-stream_loop", "-1", "-i", BGM,
        "-filter_complex", "[1:a]volume=1.45[voice];[2:a]volume=-27dB[bgm];"
        "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,alimiter=limit=0.95[a]",
        "-map", "0:v", "-map", "[a]", "-shortest", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", OUT)
    shutil.copy2(OUT, FINAL)
    midframes = contact_sheet(cut_durations)

    elapsed = 0.0
    mapping = []
    for index, (frame, item, voice, duration) in enumerate(zip(frame_paths, frame_qa, raw_durations, cut_durations), 1):
        mapping.append({"cut": index, "start": round(elapsed, 3), "voice_end": round(elapsed + voice, 3),
                        "end": round(elapsed + duration, 3), "image": item["source"],
                        "telop": item["text"], "telop_frame": str(frame), "narration": DISPLAY_NARRATION[index - 1]})
        elapsed += duration
    detected = silences(voice_all)
    report = {
        "source_lock_verified": True,
        "frame_voice_count": len(mapping),
        "speaker": f"VOICEVOX {SPEAKER}",
        "voice_speed": SPEED,
        "between_cut_added_gap_seconds": 0,
        "max_frame_quantization_gap_seconds": round(max(cut_durations[i] - raw_durations[i] for i in range(9)), 3),
        "final_bgm_only_tail_seconds": FINAL_TAIL,
        "voice_queries": voice_queries,
        "cut_map": mapping,
        "detected_voice_silences_over_0_45_seconds": detected,
        "video_info": ffmpeg_info(OUT),
        "voice_info": ffmpeg_info(voice_all),
        "video": str(OUT),
        "final_video": str(FINAL),
        "contact_sheet": str(midframes),
    }
    (VIDEO / "video_qa.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (AUDIO / "narration.json").write_text(json.dumps({"display": DISPLAY_NARRATION, "voice": VOICE_TEXT}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"video_seconds": report["video_info"]["duration"], "silences_over_0_45s": len(detected),
                      "cut_count": len(mapping), "video": str(FINAL)}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
