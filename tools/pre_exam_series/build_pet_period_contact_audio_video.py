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

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
UNIT = ROOT / "reel_assets" / "pre_exam_series" / "26_pet_period_contact_v1"
MANIFEST = UNIT / "production_manifest.md"
TELOP_MANIFEST = UNIT / "telop" / "telop_manifest.json"
AUDIO = UNIT / "audio"
WORK = UNIT / "_video_work"
VIDEO = UNIT / "video"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
FONT = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"
OUTPUT = VIDEO / "FDG-PET検査日と生理_予約先へ相談_20261019.mp4"

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
SPEED = 1.2
FPS = 30
FINAL_BGM_HOLD = 1.0
MAX_PUNCTUATION_PAUSE = 0.20

DISPLAY_NARRATION = [
    "FDG-PET検査の日に生理が重なりそうなら、予約を変える前に、案内された連絡先へ相談してください。",
    "予約を変えたほうがいいのか、迷いますよね。",
    "FDG-PET検査では、検査薬が集まる場所を画像で確認します。",
    "子宮や卵巣では、病気がなくても、周期によって検査薬の集まり方が変わることがあります。",
    "そのため、周期の情報は、画像を見るときの参考になります。",
    "検査をどう進めるかは、目的や施設によって異なります。",
    "重なりそうなときは、検査前にひとこと伝えてください。",
    "連絡するときは、こう伝えてみてください。生理の予定日が検査日と重なりそうです。どうすればいいですか。",
    "この一文を保存しておくと、検査先に連絡する前に見返せます。",
]
VOICE_NARRATION = [text.replace("FDG-PET", "エフディージーペット") for text in DISPLAY_NARRATION]


def run(*parts: object, capture: bool = False) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run([str(part) for part in parts], capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace")[-3000:])
    if capture:
        return result
    return result


def voicevox(path: str, params: dict | None = None, payload: dict | None = None) -> bytes:
    query = urllib.parse.urlencode(params or {})
    request = urllib.request.Request(
        VOICEVOX + path + ("?" + query if query else ""),
        data=None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        method="POST",
    )
    if payload is not None:
        request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def synthesize(text: str, output: Path) -> dict:
    query = json.loads(voicevox("/audio_query", {"text": text, "speaker": SPEAKER}))
    for phrase in query.get("accent_phrases", []):
        pause = phrase.get("pause_mora")
        if pause and float(pause.get("vowel_length", 0)) > MAX_PUNCTUATION_PAUSE:
            pause["vowel_length"] = MAX_PUNCTUATION_PAUSE
    query.update({
        "speedScale": SPEED,
        "pitchScale": 0.0,
        "intonationScale": 0.95,
        "volumeScale": 1.0,
        "prePhonemeLength": 0.0,
        "postPhonemeLength": 0.0,
    })
    output.write_bytes(voicevox("/synthesis", {"speaker": SPEAKER}, query))
    return {"text": text, "kana": query.get("kana")}


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as audio:
        return audio.getnframes() / audio.getframerate()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_lock() -> tuple[list[Path], list[Path]]:
    pattern = re.compile(r"^\|\s*(\d{2})\s*\|\s*`([^`]+\.png)`\s*\|")
    rows = []
    for line in MANIFEST.read_text(encoding="utf-8-sig").splitlines():
        match = pattern.match(line)
        if match:
            rows.append((int(match.group(1)), Path(match.group(2)).resolve()))
    telops = json.loads(TELOP_MANIFEST.read_text(encoding="utf-8-sig"))
    expected_cuts = list(range(1, len(DISPLAY_NARRATION) + 1))
    if [index for index, _ in rows] != expected_cuts:
        raise RuntimeError("Approved image cut count/order differs from narration")
    if [item["cut"] for item in telops] != expected_cuts:
        raise RuntimeError("Telop cut count/order differs from narration")
    images = [path for _, path in rows]
    if [Path(item["source"]).resolve() for item in telops] != images:
        raise RuntimeError("Telop source images differ from approved image order")
    frames = [Path(item["output"]).resolve() for item in telops]
    actual_images = {path.resolve() for path in (UNIT / "images").glob("*.png")}
    actual_frames = {path.resolve() for path in (UNIT / "telop").glob("telop_[0-9][0-9].png")}
    if actual_images != set(images) or actual_frames != set(frames):
        raise RuntimeError("Actual image or telop files differ from their locked lists")
    prohibited = ("_archive_", "capcut_exports", "codex_generated_images", "reference_photos", "character_references", "_不採用_")
    if any(any(token.lower() in str(path).lower() for token in prohibited) for path in images):
        raise RuntimeError("Prohibited image source detected")
    for path in images + frames:
        if not path.is_file():
            raise FileNotFoundError(path)
    for path in frames:
        with Image.open(path) as image:
            if image.size != (1080, 1920):
                raise RuntimeError(f"Telop resolution is not 1080x1920: {path}")
    return images, frames


def write_concat_list(paths: list[Path], output: Path) -> None:
    output.write_text("".join(f"file '{path.as_posix()}'\n" for path in paths), encoding="utf-8")


def media_info(path: Path) -> dict:
    result = subprocess.run([str(FFMPEG), "-hide_banner", "-i", str(path)], capture_output=True)
    detail = result.stderr.decode("utf-8", errors="replace")
    duration = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", detail)
    dimensions = re.search(r"Video:.*?\b(\d{2,5})x(\d{2,5})\b", detail)
    if not duration:
        raise RuntimeError(f"No duration found: {path}")
    hour, minute, second = duration.groups()
    return {
        "duration_seconds": round(int(hour) * 3600 + int(minute) * 60 + float(second), 3),
        "resolution": [int(dimensions.group(1)), int(dimensions.group(2))] if dimensions else None,
        "has_audio": "Audio:" in detail,
    }


def detect_silence(path: Path, minimum: float = 0.45) -> list[dict]:
    result = run(FFMPEG, "-hide_banner", "-i", path, "-af", f"silencedetect=noise=-42dB:d={minimum}", "-f", "null", "-", capture=True)
    detail = result.stderr.decode("utf-8", errors="replace")
    starts = [float(value) for value in re.findall(r"silence_start: ([0-9.]+)", detail)]
    ends = [tuple(map(float, pair)) for pair in re.findall(r"silence_end: ([0-9.]+) \| silence_duration: ([0-9.]+)", detail)]
    return [
        {"start": round(start, 3), "end": round(end, 3), "duration": round(length, 3)}
        for start, (end, length) in zip(starts, ends)
    ]


def make_midframe_sheet(cut_durations: list[float]) -> Path:
    columns, thumb_w, thumb_h, label_h = 3, 180, 320, 30
    sheet = Image.new("RGB", (columns * thumb_w, math.ceil(len(cut_durations) / columns) * (thumb_h + label_h)), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(str(FONT), 19)
    elapsed = 0.0
    for index, duration in enumerate(cut_durations):
        middle = elapsed + duration / 2
        still = WORK / f"mid_{index + 1:02d}.jpg"
        run(FFMPEG, "-y", "-loglevel", "error", "-ss", f"{middle:.3f}", "-i", OUTPUT, "-frames:v", "1", still)
        with Image.open(still) as image:
            thumb = image.convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (index % columns) * thumb_w
        y = (index // columns) * (thumb_h + label_h)
        sheet.paste(thumb, (x, y))
        draw.text((x + 6, y + thumb_h + 2), f"{index + 1:02d} {middle:.1f}s", font=font, fill=(16, 36, 55))
        elapsed += duration
    output = VIDEO / "video_qa_midframes.png"
    sheet.save(output)
    return output


def main() -> None:
    for required in (MANIFEST, TELOP_MANIFEST, FFMPEG, BGM, FONT):
        if not required.is_file():
            raise FileNotFoundError(required)
    images, frames = source_lock()
    source_hashes = {str(path): sha256(path) for path in images + frames}
    urllib.request.urlopen(VOICEVOX + "/version", timeout=5).read()
    for folder in (AUDIO, WORK, VIDEO):
        folder.mkdir(parents=True, exist_ok=True)

    audio_parts: list[Path] = []
    video_parts: list[Path] = []
    durations: list[float] = []
    cut_durations: list[float] = []
    voice_queries: list[dict] = []
    timeline: list[dict] = []
    cursor = 0.0
    for index, (frame, spoken) in enumerate(zip(frames, VOICE_NARRATION), 1):
        raw = AUDIO / f"voice_{index:02d}.wav"
        voice_queries.append(synthesize(spoken, raw))
        duration = wav_duration(raw)
        cut_duration = math.ceil(duration * FPS) / FPS + (FINAL_BGM_HOLD if index == len(frames) else 0)
        padded = WORK / f"voice_{index:02d}_timeline.wav"
        run(FFMPEG, "-y", "-loglevel", "error", "-i", raw,
            "-af", f"apad=pad_dur={cut_duration:.6f},atrim=duration={cut_duration:.6f}",
            "-ar", "44100", "-ac", "2", padded)
        segment = WORK / f"segment_{index:02d}.mp4"
        run(FFMPEG, "-y", "-loglevel", "error", "-loop", "1", "-t", f"{cut_duration:.6f}",
            "-i", frame, "-vf", "scale=1080:1920,format=yuv420p", "-r", str(FPS),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-tune", "stillimage",
            "-pix_fmt", "yuv420p", segment)
        audio_parts.append(padded)
        video_parts.append(segment)
        durations.append(duration)
        cut_durations.append(cut_duration)
        timeline.append({
            "cut": index,
            "start": round(cursor, 3),
            "voice_end": round(cursor + duration, 3),
            "cut_end": round(cursor + cut_duration, 3),
            "source_image": str(images[index - 1]),
            "telop_frame": str(frame),
            "display_narration": DISPLAY_NARRATION[index - 1],
            "voice_text": spoken,
        })
        cursor += cut_duration
        print(f"cut {index:02d}: voice={duration:.3f}s frame={cut_duration:.3f}s", flush=True)

    audio_list = WORK / "audio_parts.txt"
    video_list = WORK / "video_parts.txt"
    write_concat_list(audio_parts, audio_list)
    write_concat_list(video_parts, video_list)
    voice_all = AUDIO / "voice_all.wav"
    silent_video = WORK / "silent_video.mp4"
    run(FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", audio_list, "-c", "copy", voice_all)
    run(FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", video_list, "-c", "copy", silent_video)
    bgm_fade_start = max(0, cursor - FINAL_BGM_HOLD)
    run(FFMPEG, "-y", "-loglevel", "error", "-i", silent_video, "-i", voice_all,
        "-stream_loop", "-1", "-i", BGM,
        "-filter_complex", "[1:a]volume=1.45[voice];"
        f"[2:a]volume=-27dB,afade=t=out:st={bgm_fade_start:.3f}:d={FINAL_BGM_HOLD:.3f}[bgm];"
        "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,alimiter=limit=0.95[a]",
        "-map", "0:v", "-map", "[a]", "-shortest", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", OUTPUT)

    if any(sha256(path) != digest for path, digest in ((Path(name), value) for name, value in source_hashes.items())):
        raise RuntimeError("An approved image or telop frame changed during video generation")
    midframes = make_midframe_sheet(cut_durations)
    silences = detect_silence(voice_all)
    report = {
        "source_lock_verified": True,
        "image_telop_voice_cut_count": len(timeline),
        "voice_engine": "VOICEVOX",
        "speaker": SPEAKER,
        "speed": SPEED,
        "max_punctuation_pause_seconds": MAX_PUNCTUATION_PAUSE,
        "added_gap_between_cuts_seconds": 0,
        "max_frame_quantization_gap_seconds": round(max(cut_durations[i] - durations[i] for i in range(len(durations) - 1)), 3),
        "final_bgm_only_hold_seconds": FINAL_BGM_HOLD,
        "voice_queries": voice_queries,
        "timeline": timeline,
        "detected_voice_silences_over_0_45_seconds": silences,
        "video_info": media_info(OUTPUT),
        "voice_info": media_info(voice_all),
        "video": str(OUTPUT),
        "midframes": str(midframes),
    }
    (AUDIO / "narration.json").write_text(json.dumps({"display": DISPLAY_NARRATION, "voice": VOICE_NARRATION}, ensure_ascii=False, indent=2), encoding="utf-8")
    (VIDEO / "video_qa.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "video": str(OUTPUT),
        "duration_seconds": report["video_info"]["duration_seconds"],
        "resolution": report["video_info"]["resolution"],
        "has_audio": report["video_info"]["has_audio"],
        "silences_over_0_45_seconds": silences,
    }, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
