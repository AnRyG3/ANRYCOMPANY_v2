from __future__ import annotations

import json
import subprocess
import urllib.parse
import urllib.request
import wave
from pathlib import Path


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "mammography_series" / "mammo_deodorant_v1"
FRAME_DIR = ASSET_DIR / "telop_frames"
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_video_work"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
ASSET_VIDEO = ASSET_DIR / "マンモ_制汗剤を使ってしまったら.mp4"
FINAL_VIDEO = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形" / "マンモ_制汗剤を使ってしまったら.mp4"

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
SPEED = 1.20

NARRATION = [
    "脇に制汗剤をつけちゃった。今日のマンモ、受けられるかなと不安になりますよね。",
    "まずは、受付やスタッフに伝えてください。",
    "必要に応じて、拭き取りをご案内します。",
    "制汗剤やパウダーは、画像に白い点として写ることがあります。",
    "乳がんのサインのひとつである石灰化に、似て写ることがあるためです。",
    "うっかり使ってしまっても、言い出しにくく感じなくて大丈夫です。",
    "気づいた時点で伝えれば、その場で一緒に確認できます。",
    "次回の検査当日は、脇に何もつけずに行くと安心です。",
    "検査前日に見返せるように、保存しておいてください。",
]

FRAME_FILES = [f"telop_{index:02d}_{name}.png" for index, name in [
    (1, "hook_antiperspirant"),
    (2, "tell_staff"),
    (3, "towel_guidance"),
    (4, "product_reason"),
    (5, "mammography_room"),
    (6, "reassurance"),
    (7, "tell_technologist"),
    (8, "next_time_prepare"),
    (9, "save_background"),
]]


def run(command: list[Path | str]) -> None:
    subprocess.run([str(part) for part in command], check=True)


def post_json(path: str, params: dict | None = None, payload: dict | None = None) -> bytes:
    query = urllib.parse.urlencode(params or {})
    url = f"{VOICEVOX}{path}" + (f"?{query}" if query else "")
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=data, method="POST")
    if data is not None:
        request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def synthesize(text: str, output: Path) -> None:
    query = json.loads(post_json("/audio_query", {"text": text, "speaker": SPEAKER}))
    query["speedScale"] = SPEED
    query["pitchScale"] = 0.0
    query["intonationScale"] = 0.95
    query["volumeScale"] = 1.0
    query["prePhonemeLength"] = 0.04
    query["postPhonemeLength"] = 0.08
    output.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def main() -> None:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_VIDEO.parent.mkdir(parents=True, exist_ok=True)
    frames = [FRAME_DIR / name for name in FRAME_FILES]
    for required in [*frames, FFMPEG, BGM]:
        if not required.exists():
            raise FileNotFoundError(required)

    voices: list[Path] = []
    durations: list[float] = []
    for index, text in enumerate(NARRATION, start=1):
        voice = AUDIO_DIR / f"voice_{index:02d}.wav"
        synthesize(text, voice)
        voices.append(voice)
        durations.append(wav_duration(voice))

    frame_list = WORK_DIR / "frames.txt"
    with frame_list.open("w", encoding="utf-8") as handle:
        for frame, duration in zip(frames, durations):
            handle.write(f"file '{frame.as_posix()}'\n")
            handle.write(f"duration {duration:.3f}\n")
        handle.write(f"file '{frames[-1].as_posix()}'\n")

    audio_list = WORK_DIR / "audio_segments.txt"
    with audio_list.open("w", encoding="utf-8") as handle:
        for voice in voices:
            handle.write(f"file '{voice.as_posix()}'\n")

    narration_audio = AUDIO_DIR / "mammo_deodorant_narration.wav"
    silent_video = WORK_DIR / "mammo_deodorant_silent.mp4"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", audio_list, "-c", "copy", narration_audio])
    run([
        FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", frame_list,
        "-vf", "scale=1080:1920,format=yuv420p", "-r", "30",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", silent_video,
    ])
    run([
        FFMPEG, "-y", "-i", silent_video, "-i", narration_audio,
        "-stream_loop", "-1", "-i", BGM,
        "-filter_complex",
        "[1:a]volume=1.35[voice];[2:a]volume=-26dB[bgm];"
        "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
        "alimiter=limit=0.95[a]",
        "-map", "0:v", "-map", "[a]", "-shortest",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", ASSET_VIDEO,
    ])
    FINAL_VIDEO.write_bytes(ASSET_VIDEO.read_bytes())

    manifest = {
        "title": "うっかり制汗剤、マンモは受けられない？",
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": "1.20x",
        "fixed_interframe_silence_seconds": 0,
        "narration_voice_only": NARRATION,
        "frame_files": [str(frame.relative_to(ROOT)) for frame in frames],
        "durations_seconds": [round(duration, 3) for duration in durations],
        "total_seconds": round(sum(durations), 3),
        "narration_audio": str(narration_audio.relative_to(ROOT)),
        "asset_video": str(ASSET_VIDEO.relative_to(ROOT)),
        "final_video": str(FINAL_VIDEO.relative_to(ROOT)),
    }
    (ASSET_DIR / "video_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8-sig"
    )
    print(FINAL_VIDEO)


if __name__ == "__main__":
    main()
