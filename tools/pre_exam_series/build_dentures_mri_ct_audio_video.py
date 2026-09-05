from __future__ import annotations

import json
import re
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave
from pathlib import Path


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "pre_exam_series" / "dentures_mri_ct_samples"
FRAME_DIR = ASSET_DIR / "telop_frames"
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_video_work"
VIDEO_DIR = ASSET_DIR / "video"
FINAL_DIR = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形"
MANIFEST = ASSET_DIR / "video_manifest.json"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = (
    ROOT
    / "01_ショート動画_リール_YouTubeShorts"
    / "インスタリール用"
    / "BGM フリー素材"
    / "Kind_Heart.mp3"
)

OUT = VIDEO_DIR / "入れ歯_MRI_CT検査前に外す理由_20260904.mp4"
FINAL_OUT = FINAL_DIR / OUT.name

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
BGM_VOLUME = "-27dB"

FRAMES = [
    "telop_01_home_denture_case.png",
    "telop_02_reception_explanation.png",
    "telop_03_mri_entrance_case_tray.png",
    "telop_04_ct_flat_table_case.png",
    "telop_05_tech_monitor_artifact.png",
    "telop_06_image_comparison.png",
    "telop_07_pack_case_bag.png",
    "telop_08_case_handoff.png",
    "telop_09_after_exam_case.png",
    "telop_10_cta_save_review.png",
]

DISPLAY_NARRATION = [
    "MRIや頭のCTの予約。入れ歯は外すのかな、と思うことがありますよね。",
    "外せる入れ歯は、検査前に外していただくことがあります。",
    "MRIでは、金属が画像に影響することがあります。",
    "頭やお顔のCTでも、外していただく場合があります。",
    "口元や顎の周りが、見えにくくなることがあるためです。",
    "外しておくと、必要な部分を確認しやすい画像になります。",
    "理由は、画像を見やすくするための案内です。",
    "入れ歯ケースがあると、検査中の置き場所も安心です。",
    "検査が終わったら、すぐにつけ直していただけます。",
    "検査前日に見返せるよう、保存しておいてください。家族にも共有できます。",
]

VOICE_TEXT = [
    "エムアールアイや、頭のシーティーの予約。入れ歯は外すのかな、と思うことがありますよね。",
    "外せる入れ歯は、検査前に外していただくことがあります。",
    "エムアールアイでは、金属が画像に影響することがあります。",
    "頭やお顔のシーティーでも、外していただく場合があります。",
    "口元や、あごの周りが、見えにくくなることがあるためです。",
    "外しておくと、必要な部分を確認しやすい画像になります。",
    "理由は、画像を見やすくするための案内です。",
    "入れ歯ケースがあると、検査中の置き場所も安心です。",
    "検査が終わったら、すぐにつけ直していただけます。",
    "検査前日に見返せるよう、保存しておいてください。家族にも共有できます。",
]

# Only readability floors. Final cut length is voice duration plus a short tail.
MIN_DURATIONS = [3.8, 3.3, 3.0, 3.2, 3.6, 3.4, 3.0, 3.5, 3.2, 4.5]
TAIL_SECONDS = 0.18


def run(cmd: list[Path | str]) -> None:
    subprocess.run([str(part) for part in cmd], check=True)


def post_json(path: str, params: dict | None = None, payload: dict | None = None) -> bytes:
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
            "prePhonemeLength": 0.05,
            "postPhonemeLength": 0.10,
        }
    )
    output.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def media_duration(path: Path) -> float:
    result = subprocess.run(
        [str(FFMPEG), "-i", str(path)],
        capture_output=True,
    )
    stderr = result.stderr.decode("utf-8", errors="ignore")
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", stderr)
    if not match:
        raise RuntimeError(f"Could not read duration for {path}")
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def main() -> None:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)

    frame_paths = [FRAME_DIR / frame for frame in FRAMES]
    for required in [FFMPEG, BGM, *frame_paths]:
        if not required.exists():
            raise FileNotFoundError(required)

    padded_wavs: list[Path] = []
    durations: list[float] = []
    voice_durations: list[float] = []

    for index, text in enumerate(VOICE_TEXT, start=1):
        voice = AUDIO_DIR / f"voice_{index:02d}.wav"
        padded = WORK_DIR / f"voice_{index:02d}_padded.wav"
        synthesize_voice(text, voice)
        voice_len = wav_duration(voice)
        duration = max(MIN_DURATIONS[index - 1], voice_len + TAIL_SECONDS)
        voice_durations.append(voice_len)
        durations.append(duration)
        run(
            [
                FFMPEG,
                "-y",
                "-i",
                voice,
                "-af",
                f"apad=pad_dur={duration:.3f},atrim=duration={duration:.3f}",
                "-ar",
                "44100",
                "-ac",
                "2",
                padded,
            ]
        )
        padded_wavs.append(padded)

    voice_txt = WORK_DIR / "voice_segments.txt"
    voice_txt.write_text("".join(f"file '{wav.as_posix()}'\n" for wav in padded_wavs), encoding="utf-8")

    segment_paths: list[Path] = []
    for index, (frame, duration) in enumerate(zip(frame_paths, durations), start=1):
        segment = WORK_DIR / f"segment_{index:02d}.mp4"
        run(
            [
                FFMPEG,
                "-y",
                "-loop",
                "1",
                "-t",
                f"{duration:.3f}",
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

    segments_txt = WORK_DIR / "video_segments.txt"
    segments_txt.write_text("".join(f"file '{path.as_posix()}'\n" for path in segment_paths), encoding="utf-8")

    silent_video = WORK_DIR / "silent.mp4"
    voice_all = AUDIO_DIR / "voice.wav"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", segments_txt, "-c", "copy", silent_video])
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", voice_txt, "-c", "copy", voice_all])
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

    expected_total = sum(durations)
    manifest = {
        "title": "入れ歯 MRI CT 検査前に外す理由",
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": VOICE_SPEED,
        "bgm": str(BGM),
        "bgm_volume": BGM_VOLUME,
        "tail_seconds_per_cut": TAIL_SECONDS,
        "frames": [str(path) for path in frame_paths],
        "display_narration": DISPLAY_NARRATION,
        "voice_text": VOICE_TEXT,
        "voice_durations_seconds": [round(value, 3) for value in voice_durations],
        "cut_durations_seconds": [round(value, 3) for value in durations],
        "expected_total_seconds": round(expected_total, 3),
        "voice_audio": str(voice_all),
        "asset_video": str(OUT),
        "final_video": str(FINAL_OUT),
        "qa": {
            "video_duration_seconds": round(media_duration(OUT), 3),
            "audio_duration_seconds": round(media_duration(voice_all), 3),
            "duration_strategy": "each still frame duration equals matching voice segment plus a short tail; no long silent gap inserted",
        },
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(OUT)
    print(FINAL_OUT)
    print(json.dumps(manifest["qa"], ensure_ascii=False))


if __name__ == "__main__":
    main()
