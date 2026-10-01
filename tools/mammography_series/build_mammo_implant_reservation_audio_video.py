from __future__ import annotations

import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave
from pathlib import Path


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "mammography_series" / "mammo_implant_reservation_v1"
FRAME_DIR = ASSET_DIR / "telop_frames"
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_video_work"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
ASSET_VIDEO = ASSET_DIR / "豊胸インプラント_マンモグラフィ予約していい？.mp4"
FINAL_VIDEO = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形" / "豊胸インプラント_マンモグラフィ予約していい？.mp4"

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
SPEED = 1.20

# Kana is used only where it prevents ambiguous speech-engine readings.
NARRATION = [
    "ほうきょうインプラントがあるけど、マンモグラフィを予約していいのか、迷いますよね。",
    "予約のときに、インプラントがあると、先に伝えてください。",
    "施設によっては、マンモグラフィを実施していないことがあります。",
    "言いにくいことではありません。安全に確認するための大切な情報です。",
    "マンモグラフィは、にゅうぼうを圧迫して撮影する検査です。",
    "安全面や画像の見え方を、確認する必要があります。",
    "特に検診では、施設ごとに対応が異なります。",
    "実施できない場合は、次の相談先を確認してください。",
    "そこで終わりではありません。相談先が分かれば大丈夫です。",
    "予約前に見返せるよう、保存しておいてください。検査の不安をへらしたいかたは、フォローを。",
]

FRAME_FILES = [
    "telop_01_hook_reservation_hesitation.png",
    "telop_02_booking_call.png",
    "telop_03_facility_room.png",
    "telop_04_declaration_note.png",
    "telop_05_mammography_compression_unit.png",
    "telop_06_individual_review.png",
    "telop_07_reception_confirmation.png",
    "telop_08_consultation_destination.png",
    "telop_09_reassurance.png",
    "telop_10_cta_background.png",
]


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
    query["postPhonemeLength"] = 0.06
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

    narration = AUDIO_DIR / "mammo_implant_reservation_narration.wav"
    silent_video = WORK_DIR / "mammo_implant_reservation_silent.mp4"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", audio_list, "-c", "copy", narration])
    run([
        FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", frame_list,
        "-vf", "scale=1080:1920,format=yuv420p", "-r", "30",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", silent_video,
    ])
    run([
        FFMPEG, "-y", "-i", silent_video, "-i", narration,
        "-stream_loop", "-1", "-i", BGM,
        "-filter_complex",
        "[1:a]volume=1.35[voice];[2:a]volume=-26dB[bgm];"
        "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
        "alimiter=limit=0.95[a]",
        "-map", "0:v", "-map", "[a]", "-shortest",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", ASSET_VIDEO,
    ])
    shutil.copy2(ASSET_VIDEO, FINAL_VIDEO)

    manifest = {
        "title": "豊胸インプラントがある、マンモグラフィは予約していい？",
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": "1.20x",
        "fixed_interframe_silence_seconds": 0,
        "narration_voice_only": NARRATION,
        "frame_files": [str(frame.relative_to(ROOT)) for frame in frames],
        "durations_seconds": [round(duration, 3) for duration in durations],
        "total_seconds": round(sum(durations), 3),
        "narration_audio": str(narration.relative_to(ROOT)),
        "asset_video": str(ASSET_VIDEO.relative_to(ROOT)),
        "final_video": str(FINAL_VIDEO.relative_to(ROOT)),
    }
    (ASSET_DIR / "video_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8-sig"
    )
    print(FINAL_VIDEO)


if __name__ == "__main__":
    main()
