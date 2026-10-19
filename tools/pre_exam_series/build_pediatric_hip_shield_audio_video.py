from __future__ import annotations

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
UNIT = ROOT / "reel_assets" / "pre_exam_series"
IMAGES = UNIT / "pediatric_hip_shield_v1_images"
TELOP = UNIT / "pediatric_hip_shield_v1_telop"
OUTPUT = UNIT / "pediatric_hip_shield_v1_video"
AUDIO = OUTPUT / "audio"
WORK = OUTPUT / "_work"
MANIFEST = IMAGES / "production_manifest.md"
TELOP_QA = TELOP / "telop_qa.json"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
FONT = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"
FINAL = OUTPUT / "子どもの股関節撮影_前掛けの見直し_20261019.mp4"
VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
SPEED = 1.2
FPS = 30
FINAL_TAIL = 1.0

NARRATION = [
    "子どもの股関節撮影。前掛けがなくても、慌てず撮影前に聞いてください。",
    "前はつけたのに、今日はない。気になりますよね。",
    "学会など4団体が、股関節撮影で鉛の防護をやめていく方針を示しています。資料のURLは投稿文にあります。",
    "前掛けで減らせる被ばくは、考えられていたより小さいとされています。",
    "前掛けが画像に重なると、見たい部分が隠れ、撮り直しにつながることもあります。",
    "施設で対応は異なります。当院では前掛けを使っていません。",
    "撮影前に『前掛けを使わない理由を教えてください』と聞いて大丈夫です。",
    "この一文を保存しておくと、撮影前に見返せます。",
]

# VOICEVOX向けの読み指定。画面の表記は変えない。
VOICE_TEXT = NARRATION.copy()
VOICE_TEXT[2] = VOICE_TEXT[2].replace("4団体", "よん団体").replace("URL", "ユーアールエル")


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
    return {"text": text, "kana": query.get("kana")}


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as audio:
        return audio.getnframes() / audio.getframerate()


def source_lock() -> tuple[list[Path], list[dict]]:
    approved = re.findall(
        r"\|\s*\d{2}\s*\|\s*`([A-Za-z]:\\[^`]+\.png)`",
        MANIFEST.read_text(encoding="utf-8-sig"),
    )
    items = json.loads(TELOP_QA.read_text(encoding="utf-8-sig"))
    if len(approved) != 8 or len(items) != 8 or len(NARRATION) != 8:
        raise RuntimeError("Approved source, telop, and narration counts must equal eight")
    if approved != [item["source"] for item in items]:
        raise RuntimeError("Manifest and telop source order differ")
    if [item["cut"] for item in items] != [f"{i:02d}" for i in range(1, 9)]:
        raise RuntimeError("Telop cut order differs")
    if items[2]["text"] != "前掛け見直しの根拠は\n投稿文のURLへ":
        raise RuntimeError("The newly approved cut 03 telop is missing")
    paths = [Path(item["output"]) for item in items]
    if any(not Path(path).is_file() for path in approved) or any(not path.is_file() for path in paths):
        raise FileNotFoundError("An approved source or telop frame is missing")
    prohibited = ("_archive_", "capcut_exports", "codex_generated_images", "reference_photos", "character_references")
    if any(any(token in path.lower() for token in prohibited) for path in approved):
        raise RuntimeError("A prohibited source area was detected")
    for path in paths:
        with Image.open(path) as frame:
            if frame.size != (941, 1672):
                raise RuntimeError(f"Invalid telop dimensions: {path}")
    return paths, items


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


def contact_sheet(durations: list[float]) -> Path:
    sheet = Image.new("RGB", (864, 2 * 414), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(str(FONT), 19)
    elapsed = 0.0
    for index, duration in enumerate(durations):
        middle = elapsed + duration / 2
        thumb = WORK / f"mid_{index + 1:02d}.jpg"
        run(FFMPEG, "-y", "-loglevel", "error", "-ss", f"{middle:.3f}", "-i", FINAL, "-frames:v", "1", thumb)
        with Image.open(thumb) as frame:
            mini = frame.convert("RGB").resize((216, 384), Image.Resampling.LANCZOS)
        x, y = (index % 4) * 216, (index // 4) * 414
        sheet.paste(mini, (x, y))
        draw.text((x + 8, y + 390), f"{index + 1:02d} {middle:.1f}s", font=font, fill=(12, 34, 64))
        elapsed += duration
    path = OUTPUT / "video_qa_midframes.png"
    sheet.save(path)
    return path


def main() -> None:
    for required in (MANIFEST, TELOP_QA, FFMPEG, BGM, FONT):
        if not required.is_file():
            raise FileNotFoundError(required)
    frames, frame_qa = source_lock()
    urllib.request.urlopen(VOICEVOX + "/version", timeout=5).read()
    for folder in (OUTPUT, AUDIO, WORK):
        folder.mkdir(parents=True, exist_ok=True)
    raw_durations = []
    cut_durations = []
    audio_parts = []
    video_parts = []
    voice_queries = []
    for index, (frame, spoken) in enumerate(zip(frames, VOICE_TEXT), 1):
        raw = AUDIO / f"voice_{index:02d}.wav"
        voice_queries.append(synthesize(spoken, raw))
        raw_duration = wav_duration(raw)
        cut_duration = math.ceil(raw_duration * FPS) / FPS + (FINAL_TAIL if index == 8 else 0.0)
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
        "-movflags", "+faststart", FINAL)
    midframes = contact_sheet(cut_durations)
    elapsed = 0.0
    mapping = []
    for index, (frame, item, voice, duration) in enumerate(zip(frames, frame_qa, raw_durations, cut_durations), 1):
        mapping.append({"cut": index, "start": round(elapsed, 3), "voice_end": round(elapsed + voice, 3),
                        "end": round(elapsed + duration, 3), "image": item["source"],
                        "telop": item["text"], "telop_frame": str(frame), "narration": NARRATION[index - 1]})
        elapsed += duration
    report = {
        "source_lock_verified": True,
        "frame_voice_count": len(mapping),
        "speaker": f"VOICEVOX {SPEAKER}",
        "voice_speed": SPEED,
        "between_cut_added_gap_seconds": 0,
        "max_frame_quantization_gap_seconds": round(max(cut_durations[i] - raw_durations[i] for i in range(7)), 3),
        "final_bgm_only_tail_seconds": FINAL_TAIL,
        "voice_queries": voice_queries,
        "cut_map": mapping,
        "detected_voice_silences_over_0_45_seconds": silences(voice_all),
        "video_info": ffmpeg_info(FINAL),
        "voice_info": ffmpeg_info(voice_all),
        "video": str(FINAL),
        "contact_sheet": str(midframes),
    }
    (OUTPUT / "video_qa.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (AUDIO / "narration.json").write_text(json.dumps({"display": NARRATION, "voice": VOICE_TEXT}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"video_seconds": report["video_info"]["duration"],
                      "silences_over_0_45s": len(report["detected_voice_silences_over_0_45_seconds"]),
                      "cut_count": len(mapping), "video": str(FINAL)}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
