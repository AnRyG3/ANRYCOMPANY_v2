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
UNIT = ROOT / "reel_assets" / "echo_series" / "10_heart_echo_onepiece_v1_samples"
MANIFEST = UNIT / "production_manifest.md"
TELOP_DIR = UNIT / "telop_frames"
AUDIO_DIR = UNIT / "audio"
WORK_DIR = UNIT / "_video_work"
VIDEO_DIR = UNIT / "video"
QA_DIR = UNIT / "qa_midframes"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
FONT = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"
VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
SPEED = 1.2
FPS = 30
BETWEEN_CUT_TAIL = 0.03
FINAL_BGM_HOLD = 1.0
MAX_PUNCTUATION_PAUSE = 0.22
OUTPUT = VIDEO_DIR / "心臓エコーの日_ワンピースで来たら_20261019_確認用.mp4"

DISPLAY_NARRATION = [
    "心臓エコーの日、ワンピースで来てしまった。服装への対応は施設によって違います。",
    "上下が分かれた服にすればよかったのかな、と気になるかもしれません。",
    "心臓エコーは、胸に機器を当てて行う検査です。",
    "そのため、胸部が出せるように衣服を調整します。",
    "ワンピースを控えるよう案内する施設もあります。",
    "検査着を用意している施設もありますが、対応は一律ではありません。",
    "服装や肌の露出が気になれば、検査の担当者に相談できます。",
    "次回は予約案内の服装欄を確認してください。施設の案内を優先しましょう。",
]

# VOICEVOXに渡す文は、読みに迷う語だけかなへ置き換える。
VOICE_TEXT = [
    "しんぞうエコーの日、ワンピースで来てしまった。服装への対応は、施設によって違います。",
    "上下が分かれた服にすればよかったのかな、と、気になるかもしれません。",
    "しんぞうエコーは、胸に機器を当てて行う検査です。",
    "そのため、胸が出せるように、服を調整します。",
    "ワンピースを控えるよう、案内する施設もあります。",
    "検査着を用意している施設もありますが、対応は一律ではありません。",
    "服装や肌の露出が気になれば、検査の担当者に相談できます。",
    "次回は、予約のあんないひょうで服装を確認してください。施設の案内を優先しましょう。",
]


def run(command: list[object], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(part) for part in command],
        check=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=capture,
    )


def voicevox_post(endpoint: str, params: dict, payload: dict | None = None) -> bytes:
    query = urllib.parse.urlencode(params)
    request = urllib.request.Request(
        f"{VOICEVOX}{endpoint}?{query}",
        data=None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        method="POST",
    )
    if payload is not None:
        request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def synthesize(voice_text: str, output: Path) -> None:
    query = json.loads(voicevox_post("/audio_query", {"text": voice_text, "speaker": SPEAKER}))
    for phrase in query.get("accent_phrases", []):
        pause = phrase.get("pause_mora")
        if pause and pause.get("vowel_length", 0) > MAX_PUNCTUATION_PAUSE:
            pause["vowel_length"] = MAX_PUNCTUATION_PAUSE
    query.update(
        speedScale=SPEED,
        pitchScale=0,
        intonationScale=0.95,
        prePhonemeLength=0,
        postPhonemeLength=0,
    )
    output.write_bytes(voicevox_post("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as opened:
        return opened.getnframes() / opened.getframerate()


def approved_sources() -> list[Path]:
    rows = re.findall(r"^\| (\d{2}) \| ([A-Z]:\\[^|]+?) \|", MANIFEST.read_text(encoding="utf-8"), re.M)
    if [int(number) for number, _ in rows] != list(range(1, 9)):
        raise RuntimeError("Approved image count or order mismatch")
    paths = [Path(path.strip()) for _, path in rows]
    if len({str(path).lower() for path in paths}) != 8 or any(not path.is_file() for path in paths):
        raise RuntimeError("Approved image is duplicated or missing")
    return paths


def locked_telops(sources: list[Path]) -> list[Path]:
    records = json.loads((TELOP_DIR / "telop_manifest.json").read_text(encoding="utf-8"))
    if [record["cut"] for record in records] != list(range(1, 9)):
        raise RuntimeError("Telop cut order mismatch")
    if len(DISPLAY_NARRATION) != 8 or len(VOICE_TEXT) != 8:
        raise RuntimeError("Narration count mismatch")
    frames = []
    for source, record in zip(sources, records, strict=True):
        if Path(record["source"]).resolve() != source.resolve():
            raise RuntimeError(f"Telop source mismatch: {source}")
        if hashlib.sha256(source.read_bytes()).hexdigest() != record["source_sha256"]:
            raise RuntimeError(f"Approved source changed: {source}")
        frame = Path(record["output"])
        if not frame.is_file():
            raise FileNotFoundError(frame)
        with Image.open(frame) as opened:
            if opened.size != (1080, 1920):
                raise RuntimeError(f"Telop size mismatch: {frame}")
        frames.append(frame)
    listed = sorted(TELOP_DIR.glob("telop_[0-9][0-9].png"))
    if [path.resolve() for path in listed] != [path.resolve() for path in frames]:
        raise RuntimeError("Telop frame folder differs from locked list")
    return frames


def concat_list(paths: list[Path], output: Path) -> None:
    output.write_text(
        "".join(f"file '{path.as_posix()}'\n" for path in paths), encoding="utf-8"
    )


def contact_sheet(paths: list[Path], output: Path) -> None:
    thumb_w, thumb_h, label_h = 270, 480, 34
    sheet = Image.new("RGB", (thumb_w * 4, (thumb_h + label_h) * 2), (245, 247, 249))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(str(FONT), 20)
    for index, path in enumerate(paths):
        with Image.open(path) as opened:
            thumb = opened.convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = index % 4 * thumb_w
        y = index // 4 * (thumb_h + label_h)
        sheet.paste(thumb, (x, y))
        draw.text((x + 8, y + thumb_h + 5), f"{index + 1:02d}", font=font, fill=(12, 34, 58))
    sheet.save(output, quality=92)


def main() -> None:
    for required in (FFMPEG, BGM, FONT):
        if not required.is_file():
            raise FileNotFoundError(required)
    sources = approved_sources()
    frames = locked_telops(sources)
    for directory in (AUDIO_DIR, WORK_DIR, VIDEO_DIR, QA_DIR):
        directory.mkdir(parents=True, exist_ok=True)

    padded_wavs: list[Path] = []
    segments: list[Path] = []
    timeline: list[dict] = []
    cursor = 0.0
    for cut, (display, voice, source, frame) in enumerate(
        zip(DISPLAY_NARRATION, VOICE_TEXT, sources, frames, strict=True), start=1
    ):
        raw_wav = AUDIO_DIR / f"voice_{cut:02d}.wav"
        synthesize(voice, raw_wav)
        duration = wav_duration(raw_wav)
        tail = FINAL_BGM_HOLD if cut == 8 else BETWEEN_CUT_TAIL
        frame_count = math.ceil((duration + tail) * FPS)
        cut_duration = frame_count / FPS
        padded = WORK_DIR / f"voice_{cut:02d}_timeline.wav"
        run([
            FFMPEG, "-y", "-loglevel", "error", "-i", raw_wav,
            "-af", f"apad=pad_dur={cut_duration:.6f},atrim=duration={cut_duration:.6f}",
            "-ar", "44100", "-ac", "2", padded,
        ])
        segment = WORK_DIR / f"segment_{cut:02d}.mp4"
        run([
            FFMPEG, "-y", "-loglevel", "error", "-loop", "1",
            "-framerate", str(FPS), "-t", f"{cut_duration:.6f}",
            "-i", frame, "-vf", "scale=1080:1920,format=yuv420p",
            "-r", str(FPS), "-frames:v", str(frame_count),
            "-c:v", "libx264", "-preset", "medium", "-tune", "stillimage",
            "-pix_fmt", "yuv420p", segment,
        ])
        padded_wavs.append(padded)
        segments.append(segment)
        timeline.append({
            "cut": cut,
            "start": round(cursor, 3),
            "voice_end": round(cursor + duration, 3),
            "cut_end": round(cursor + cut_duration, 3),
            "voice_duration": round(duration, 3),
            "tail_duration": round(cut_duration - duration, 3),
            "display_narration": display,
            "voice_text": voice,
            "source_image": str(source),
            "telop_frame": str(frame),
            "voice_file": str(raw_wav),
        })
        cursor += cut_duration
        print(f"cut {cut:02d}: voice {duration:.3f}s, video {cut_duration:.3f}s", flush=True)

    voice_list = WORK_DIR / "voice_concat.txt"
    video_list = WORK_DIR / "video_concat.txt"
    concat_list(padded_wavs, voice_list)
    concat_list(segments, video_list)
    voice_all = AUDIO_DIR / "voice_all.wav"
    silent_video = WORK_DIR / "silent_video.mp4"
    run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", voice_list, "-c", "copy", voice_all])
    run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", video_list, "-c", "copy", silent_video])
    run([
        FFMPEG, "-y", "-loglevel", "error", "-i", silent_video, "-i", voice_all,
        "-stream_loop", "-1", "-i", BGM,
        "-filter_complex",
        "[1:a]volume=1.45[voice];[2:a]volume=-27dB[bgm];"
        "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
        "alimiter=limit=0.95[audio]",
        "-map", "0:v", "-map", "[audio]", "-shortest",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", OUTPUT,
    ])

    qa_paths = []
    for item in timeline:
        midpoint = (item["start"] + item["voice_end"]) / 2
        qa = QA_DIR / f"qa_mid_{item['cut']:02d}.jpg"
        run([FFMPEG, "-y", "-loglevel", "error", "-ss", f"{midpoint:.3f}", "-i", OUTPUT, "-frames:v", "1", qa])
        qa_paths.append(qa)
    qa_contact = QA_DIR / "qa_midframes_contact_sheet.jpg"
    contact_sheet(qa_paths, qa_contact)

    silence = run([
        FFMPEG, "-hide_banner", "-i", voice_all,
        "-af", "silencedetect=noise=-45dB:d=0.45", "-f", "null", "-",
    ], capture=True)
    silence_events = [
        line.strip() for line in silence.stderr.splitlines()
        if "silence_start" in line or "silence_end" in line
    ]
    probe = run([FFMPEG, "-hide_banner", "-i", OUTPUT, "-f", "null", "-"], capture=True)
    media_info = {"ffmpeg_stream_report": [
        line.strip() for line in probe.stderr.splitlines()
        if "Duration:" in line or "Stream #" in line
    ]}
    (AUDIO_DIR / "audio_manifest.json").write_text(
        json.dumps({
            "voice_engine": "VOICEVOX",
            "speaker": "もち子さん(cv 明日葉よもぎ)",
            "speaker_id": SPEAKER,
            "speed": SPEED,
            "between_cut_tail_seconds": BETWEEN_CUT_TAIL,
            "final_bgm_hold_seconds": FINAL_BGM_HOLD,
            "display_narration": DISPLAY_NARRATION,
            "voice_text": VOICE_TEXT,
            "voice_files": [str(AUDIO_DIR / f"voice_{cut:02d}.wav") for cut in range(1, 9)],
            "silence_over_0_45_seconds": silence_events,
        }, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (VIDEO_DIR / "video_manifest.json").write_text(
        json.dumps({
            "video": str(OUTPUT),
            "timeline": timeline,
            "expected_duration_seconds": round(cursor, 3),
            "qa_contact_sheet": str(qa_contact),
            "media_info": media_info,
        }, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"video: {OUTPUT}", flush=True)
    print(f"silence events: {len(silence_events)}", flush=True)


if __name__ == "__main__":
    main()
