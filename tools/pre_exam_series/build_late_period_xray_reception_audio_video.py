from __future__ import annotations

import json
import re
import struct
import subprocess
import urllib.parse
import urllib.request
import wave
from pathlib import Path


ROOT = Path(r"F:\ANRYCAMPANY")
UNIT = ROOT / "reel_assets" / "pre_exam_series" / "24_late_period_xray_reception_v1"
TELOP_DIR = UNIT / "telop"
AUDIO_DIR = UNIT / "audio"
WORK_DIR = UNIT / "_video_work"
VIDEO_DIR = UNIT / "video"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = (
    ROOT
    / "01_ショート動画_リール_YouTubeShorts"
    / "インスタリール用"
    / "BGM フリー素材"
    / "Kind_Heart.mp3"
)
VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
SPEED = 1.2
BETWEEN_CUT_TAIL = 0.03
FINAL_BGM_HOLD = 1.0
MAX_LONG_PUNCTUATION_PAUSE = 0.22
OUTPUT = VIDEO_DIR / "生理が遅れているとき_レントゲン受付で伝えて大丈夫_20261011.mp4"

VOICE_TEXT = [
    "生理が遅れていたら、レントゲン前に受付で伝えて大丈夫です。",
    "『妊娠の可能性があるかも』と、一言で十分です。",
    "まだ分からないと、言い出しにくいですよね。",
    "放射線を使う検査では、事前確認が一般的です。",
    "受付で言いそびれても、検査前に伝えられます。",
    "伝えたら、すぐ撮れないと決まるわけではありません。",
    "検査の進め方は、医師が状況を見て判断します。",
    "確認の流れは、施設によって異なります。",
    "恥ずかしいことでも、迷惑なことでもありません。",
    "生理が遅れていて、妊娠の可能性を否定できません。",
    "検査前に見返せるよう、保存しておいてください。",
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


def post(path: str, params: dict[str, object], payload: dict[str, object] | None = None) -> bytes:
    query = urllib.parse.urlencode(params)
    request = urllib.request.Request(
        f"{VOICEVOX}{path}?{query}",
        data=None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        method="POST",
    )
    if payload is not None:
        request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def synthesize(text: str, output: Path) -> None:
    query = json.loads(post("/audio_query", {"text": text, "speaker": SPEAKER}))
    for phrase in query.get("accent_phrases", []):
        pause_mora = phrase.get("pause_mora")
        if pause_mora and pause_mora.get("vowel_length", 0) > 0.35:
            pause_mora["vowel_length"] = MAX_LONG_PUNCTUATION_PAUSE
    query.update(
        {
            "speedScale": SPEED,
            "pitchScale": 0,
            "intonationScale": 0.95,
            "prePhonemeLength": 0,
            "postPhonemeLength": 0,
        }
    )
    output.write_bytes(post("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav_file:
        return wav_file.getnframes() / wav_file.getframerate()


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as image_file:
        header = image_file.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"PNGとして読めません: {path}")
    return struct.unpack(">II", header[16:24])


def write_concat_list(paths: list[Path], output: Path) -> None:
    output.write_text(
        "".join(f"file '{path.as_posix()}'\n" for path in paths),
        encoding="utf-8",
    )


def approved_source_images() -> list[Path]:
    text = (UNIT / "production_manifest.md").read_text(encoding="utf-8-sig")
    paths = [Path(item) for item in re.findall(r"`([A-Za-z]:\\[^`]+\.png)`", text)[:11]]
    if len(paths) != len(VOICE_TEXT):
        raise RuntimeError("production_manifest.md の承認画像が11枚ではありません。")
    return paths


def locked_telop_frames(source_images: list[Path]) -> list[Path]:
    entries = json.loads((TELOP_DIR / "telop_manifest.json").read_text(encoding="utf-8-sig"))
    if [entry["cut"] for entry in entries] != list(range(1, len(VOICE_TEXT) + 1)):
        raise RuntimeError("telop_manifest.json のカット順が1〜11ではありません。")
    if [Path(entry["source"]) for entry in entries] != source_images:
        raise RuntimeError("承認画像とテロップの対応がproduction_manifestと一致しません。")
    frames = [Path(entry["output"]) for entry in entries]
    listed_frames = sorted(TELOP_DIR.glob("telop_[0-9][0-9]_*.png"))
    if listed_frames != frames:
        raise RuntimeError("テロップフォルダの画像一覧とtelop_manifestが一致しません。")
    for frame in frames:
        if not frame.exists() or png_size(frame) != (1080, 1920):
            raise RuntimeError(f"テロップ画像が存在しないか1080x1920ではありません: {frame}")
    return frames


def main() -> None:
    for required in (FFMPEG, BGM):
        if not required.exists():
            raise FileNotFoundError(required)

    source_images = approved_source_images()
    frames = locked_telop_frames(source_images)
    for directory in (AUDIO_DIR, WORK_DIR, VIDEO_DIR):
        directory.mkdir(parents=True, exist_ok=True)

    raw_wavs: list[Path] = []
    padded_wavs: list[Path] = []
    video_segments: list[Path] = []
    voice_durations: list[float] = []
    cut_durations: list[float] = []
    timeline: list[dict[str, object]] = []
    cursor = 0.0

    for cut, (text, frame) in enumerate(zip(VOICE_TEXT, frames), start=1):
        raw_wav = AUDIO_DIR / f"voice_{cut:02d}.wav"
        synthesize(text, raw_wav)
        voice_duration = wav_duration(raw_wav)
        hold = FINAL_BGM_HOLD if cut == len(VOICE_TEXT) else BETWEEN_CUT_TAIL
        cut_duration = voice_duration + hold

        padded_wav = WORK_DIR / f"voice_{cut:02d}_timeline.wav"
        run(
            [
                FFMPEG,
                "-y",
                "-i",
                raw_wav,
                "-af",
                f"apad=pad_dur={cut_duration:.6f},atrim=duration={cut_duration:.6f}",
                "-ar",
                "44100",
                "-ac",
                "2",
                padded_wav,
            ]
        )

        segment = WORK_DIR / f"segment_{cut:02d}.mp4"
        run(
            [
                FFMPEG,
                "-y",
                "-loop",
                "1",
                "-t",
                f"{cut_duration:.6f}",
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

        raw_wavs.append(raw_wav)
        padded_wavs.append(padded_wav)
        video_segments.append(segment)
        voice_durations.append(voice_duration)
        cut_durations.append(cut_duration)
        timeline.append(
            {
                "cut": cut,
                "start": round(cursor, 3),
                "voice_end": round(cursor + voice_duration, 3),
                "cut_end": round(cursor + cut_duration, 3),
                "voice_text": text,
                "source_image": str(source_images[cut - 1]),
                "telop_frame": str(frame),
                "voice_file": str(raw_wav),
            }
        )
        cursor += cut_duration

    voice_list = WORK_DIR / "voice_concat.txt"
    video_list = WORK_DIR / "video_concat.txt"
    write_concat_list(padded_wavs, voice_list)
    write_concat_list(video_segments, video_list)
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
            "[1:a]volume=1.45[voice];[2:a]volume=-27dB[bgm];"
            "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
            "alimiter=limit=0.95[audio]",
            "-map",
            "0:v",
            "-map",
            "[audio]",
            "-shortest",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            OUTPUT,
        ]
    )

    silence_check = run(
        [FFMPEG, "-hide_banner", "-i", voice_all, "-af", "silencedetect=noise=-48dB:d=0.45", "-f", "null", "-"],
        capture=True,
    )
    detected_silence = [
        line.strip()
        for line in silence_check.stderr.splitlines()
        if "silence_start" in line or "silence_end" in line
    ]

    audio_manifest = {
        "voice_engine": "VOICEVOX",
        "speaker": SPEAKER,
        "voice_speed": SPEED,
        "pre_phoneme_length": 0,
        "post_phoneme_length": 0,
        "max_long_punctuation_pause": MAX_LONG_PUNCTUATION_PAUSE,
        "between_cut_tail_seconds": BETWEEN_CUT_TAIL,
        "final_bgm_hold_seconds": FINAL_BGM_HOLD,
        "voice_text": VOICE_TEXT,
        "voice_files": [str(path) for path in raw_wavs],
        "voice_durations": voice_durations,
        "detected_silence_over_0_45_seconds": detected_silence,
    }
    (AUDIO_DIR / "audio_manifest.json").write_text(
        json.dumps(audio_manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig"
    )

    video_manifest = {
        "video": str(OUTPUT),
        "resolution": "1080x1920",
        "fps": 30,
        "expected_duration_seconds": round(sum(cut_durations), 3),
        "pacing": "0.03秒のカット末尾余白。最終カットのみ音声後にBGMだけ1.0秒。",
        "source_images": [str(path) for path in source_images],
        "telop_frames": [str(path) for path in frames],
        "timeline": timeline,
    }
    (VIDEO_DIR / "video_manifest.json").write_text(
        json.dumps(video_manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig"
    )
    print(json.dumps(video_manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
