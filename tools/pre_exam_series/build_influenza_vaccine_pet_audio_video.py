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
UNIT = ROOT / "reel_assets" / "pre_exam_series" / "16_influenza_vaccine_pet_v1_samples"
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
BETWEEN_CUT_TAIL = 0.03
FINAL_TAIL = 1.0

TITLE = "インフル予防接種後のPET検査_20261018"
OUT = VIDEO_DIR / f"{TITLE}.mp4"
FINAL_OUT = FINAL_DIR / OUT.name

FRAMES = [
    "telop_01_hook_vaccine_pet.png",
    "telop_02_patient_checks_schedule.png",
    "telop_03_fdg_pet_explanation.png",
    "telop_04_vaccinated_side_axilla.png",
    "telop_05_date_and_arm_info.png",
    "telop_06_facility_scheduling_differs.png",
    "telop_07_call_pet_booking.png",
    "telop_08_after_call_calm.png",
    "telop_09_phone_example_sentence.png",
    "telop_10_save_before_call.png",
]

DISPLAY_NARRATION = [
    "インフルエンザの予防接種のあとにPET検査があるときは、接種した日と打った腕を予約先に伝えてください。",
    "予防接種のすぐあとに検査が控えていると、心配になりますよね。",
    "FDGを使うPET検査では、薬が集まる場所を画像にします。",
    "接種した側のわきのリンパ節に、その薬が集まって映ることがあります。",
    "接種した日と打った腕は、画像を見るときの参考情報です。",
    "検査の日を変えるかどうかは、検査の目的や施設によって考え方が異なります。",
    "検査日を変更する前に、PET検査の予約先へ確認してください。",
    "事前にひとこと伝えておくと、当日を落ち着いて迎えられます。",
    "予約のときは、こう伝えてみてください。○月○日にインフルエンザの予防接種を受けました。打ったのは右腕です。検査の進め方を教えてください。",
    "この一文を保存しておくと、予約の電話の前に見返せます。",
]

# Voice-only kana substitutions keep PET and FDG readings stable.
VOICE_TEXT = [
    "インフルエンザの予防接種のあとに、ペット検査があるときは、接種した日と打ったうでを予約先に伝えてください。",
    "予防接種のすぐあとに検査が控えていると、心配になりますよね。",
    "エフディージーを使うペット検査では、薬が集まる場所を画像にします。",
    "接種した側のわきのリンパ節に、その薬が集まって映ることがあります。",
    "接種した日と打ったうでは、画像を見るときの参考情報です。",
    "検査の日を変えるかどうかは、検査の目的や施設によって、考え方が異なります。",
    "検査日を変更する前に、ペット検査の予約先へ確認してください。",
    "事前にひとこと伝えておくと、当日を落ち着いて迎えられます。",
    "予約のときは、こう伝えてみてください。まる月まる日に、インフルエンザの予防接種を受けました。打ったのは右うでです。検査の進め方を教えてください。",
    "この一文を保存しておくと、予約の電話の前に見返せます。",
]


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


def synthesize_voice(text: str, output: Path) -> None:
    query = json.loads(post_json("/audio_query", {"text": text, "speaker": SPEAKER}))
    query.update(
        {
            "speedScale": VOICE_SPEED,
            "pitchScale": 0.0,
            "intonationScale": 0.95,
            "volumeScale": 1.0,
            "prePhonemeLength": 0.03,
            "postPhonemeLength": 0.05,
        }
    )
    output.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def media_info(path: Path) -> dict:
    completed = subprocess.run(
        [str(FFMPEG), "-hide_banner", "-i", str(path)], capture_output=True
    )
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


def cover(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    scale = max(size[0] / img.width, size[1] / img.height)
    resized = img.resize((int(img.width * scale), int(img.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - size[0]) // 2
    top = (resized.height - size[1]) // 2
    return resized.crop((left, top, left + size[0], top + size[1]))


def verify_source_lock(frame_paths: list[Path]) -> list[str]:
    manifest_text = PRODUCTION_MANIFEST.read_text(encoding="utf-8")
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
    prohibited = ("_archive_", "capcut_exports", "codex_generated_images", "reference_photos", "character_references")
    if any(any(part in path.lower() for part in prohibited) for path in approved):
        raise RuntimeError("A prohibited source area was detected.")
    return approved


def detect_silences(audio: Path) -> list[dict]:
    completed = subprocess.run(
        [
            str(FFMPEG), "-hide_banner", "-i", str(audio),
            "-af", "silencedetect=noise=-42dB:d=0.55", "-f", "null", "-",
        ],
        capture_output=True,
    )
    details = completed.stderr.decode("utf-8", errors="ignore")
    starts = [float(value) for value in re.findall(r"silence_start: ([0-9.]+)", details)]
    ends = [(float(end), float(duration)) for end, duration in re.findall(r"silence_end: ([0-9.]+) \| silence_duration: ([0-9.]+)", details)]
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
        run([FFMPEG, "-y", "-loglevel", "error", "-ss", f"{timestamp:.3f}", "-i", video, "-frames:v", "1", "-q:v", "2", thumb])
        thumbs.append((thumb, timestamp))
        elapsed += duration

    cols = 5
    thumb_w, thumb_h, label_h = 216, 384, 40
    rows = math.ceil(len(thumbs) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (244, 246, 248))
    font = ImageFont.truetype(str(FONT_PATH), 20)
    draw = ImageDraw.Draw(sheet)
    for idx, (path, timestamp) in enumerate(thumbs):
        img = cover(Image.open(path).convert("RGB"), (thumb_w, thumb_h))
        x = (idx % cols) * thumb_w
        y = (idx // cols) * (thumb_h + label_h)
        sheet.paste(img, (x, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill="white")
        draw.text((x + 8, y + thumb_h + 8), f"{idx + 1:02d} {timestamp:.1f}s", font=font, fill=(12, 34, 64))
    sheet.save(MIDFRAME_SHEET, quality=94)


def main() -> None:
    for directory in (AUDIO_DIR, WORK_DIR, VIDEO_DIR, FINAL_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    frame_paths = [TELOP_DIR / name for name in FRAMES]
    for required in (FFMPEG, BGM, FONT_PATH, PRODUCTION_MANIFEST, TELOP_MANIFEST):
        if not required.exists():
            raise FileNotFoundError(required)
    approved_sources = verify_source_lock(frame_paths)
    if not (len(FRAMES) == len(DISPLAY_NARRATION) == len(VOICE_TEXT) == 10):
        raise RuntimeError("Frame and narration counts must match.")
    urllib.request.urlopen(f"{VOICEVOX}/version", timeout=5).read()

    padded_wavs: list[Path] = []
    segment_paths: list[Path] = []
    raw_durations: list[float] = []
    cut_durations: list[float] = []

    for index, (frame, text) in enumerate(zip(frame_paths, VOICE_TEXT), start=1):
        voice = AUDIO_DIR / f"voice_{index:02d}.wav"
        padded = WORK_DIR / f"voice_{index:02d}_padded.wav"
        synthesize_voice(text, voice)
        raw_duration = wav_duration(voice)
        tail = FINAL_TAIL if index == len(FRAMES) else BETWEEN_CUT_TAIL
        cut_duration = raw_duration + tail
        raw_durations.append(raw_duration)
        cut_durations.append(cut_duration)
        run([FFMPEG, "-y", "-loglevel", "error", "-i", voice, "-af", f"apad=pad_dur={cut_duration:.3f},atrim=duration={cut_duration:.3f}", "-ar", "44100", "-ac", "2", padded])
        padded_wavs.append(padded)

        segment = WORK_DIR / f"segment_{index:02d}.mp4"
        run([FFMPEG, "-y", "-loglevel", "error", "-loop", "1", "-t", f"{cut_duration:.3f}", "-i", frame, "-vf", "scale=1080:1920,format=yuv420p", "-r", "30", "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p", segment])
        segment_paths.append(segment)

    voice_list = WORK_DIR / "voice_segments.txt"
    video_list = WORK_DIR / "video_segments.txt"
    voice_list.write_text("".join(f"file '{path.as_posix()}'\n" for path in padded_wavs), encoding="utf-8")
    video_list.write_text("".join(f"file '{path.as_posix()}'\n" for path in segment_paths), encoding="utf-8")
    voice_all = AUDIO_DIR / "voice_all.wav"
    silent_video = WORK_DIR / "silent.mp4"
    run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", voice_list, "-c", "copy", voice_all])
    run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", video_list, "-c", "copy", silent_video])
    run([
        FFMPEG, "-y", "-loglevel", "error", "-i", silent_video, "-i", voice_all,
        "-stream_loop", "-1", "-i", BGM,
        "-filter_complex",
        f"[1:a]volume=1.45[voice];[2:a]volume={BGM_VOLUME}[bgm];[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,alimiter=limit=0.95[a]",
        "-map", "0:v", "-map", "[a]", "-shortest", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT,
    ])
    shutil.copy2(OUT, FINAL_OUT)
    make_midframe_sheet(OUT, cut_durations)

    video_info = media_info(OUT)
    voice_info = media_info(voice_all)
    silences = detect_silences(voice_all)
    total = sum(cut_durations)
    cut_map = []
    elapsed = 0.0
    for index, duration in enumerate(cut_durations, start=1):
        cut_map.append({"cut": index, "start": round(elapsed, 3), "end": round(elapsed + duration, 3), "duration": round(duration, 3), "frame": str(frame_paths[index - 1]), "narration": DISPLAY_NARRATION[index - 1]})
        elapsed += duration

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
        "detected_voice_silences_over_0_55_seconds": silences,
        "note": "Each approved telop frame is held for its matching narration. No fixed pause is inserted between cuts beyond 0.03 seconds; the final frame remains for 1.0 second with BGM.",
    }
    QA_REPORT.write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(f"source lock verified: {len(approved_sources)} images")
    print(f"voice/frame mapping verified: {len(frame_paths)} cuts")
    print(f"planned={total:.3f}s voice={voice_info['duration_seconds']:.3f}s video={video_info['duration_seconds']:.3f}s")
    print(OUT)
    print(FINAL_OUT)
    print(MIDFRAME_SHEET)
    print(QA_REPORT)


if __name__ == "__main__":
    main()
