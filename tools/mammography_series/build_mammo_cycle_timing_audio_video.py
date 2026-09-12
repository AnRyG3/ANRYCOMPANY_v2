from pathlib import Path
import json
import subprocess
import urllib.parse
import urllib.request
import wave


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "mammography_series" / "mammo_cycle_timing_v1"
FRAME_DIR = ASSET_DIR / "telop_frames"
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_video_work"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
SPEED = 1.20
POST_FRAME_GAP = 0.12

VOICE_NARRATION = [
    "生理前で胸が張るとき。マンモの予約を変えた方がいいのかな、と迷いますよね。",
    "張りや痛みがつらければ、予約先に相談して大丈夫です。",
    "せっかく取った予約。変更の電話は、気が引けますよね。",
    "マンモグラフィは、にゅうぼうを圧迫して撮影します。",
    "生理前は胸が張り、痛みを強く感じることがあります。",
    "ただ、生理前や生理中でも、検査自体は受けられます。",
    "痛みが心配なときは、生理後など、胸の張りが少ない時期がひとつの目安です。",
    "自己判断で延期せず、予約先に日程を相談してみてください。",
    "次の予約日を決める前に、保存しておいてください。",
    "検査前の小さな迷いに答えています。次も見逃さないよう、フォローを。",
]

FRAME_FILES = [
    "telop_01_hook_calendar.png",
    "telop_02_consult_by_phone.png",
    "telop_03_appointment_hesitation.png",
    "telop_04_mammography_equipment.png",
    "telop_05_compression_detail.png",
    "telop_06_reassured_waiting.png",
    "telop_07_timing_calendar.png",
    "telop_08_reschedule_note.png",
    "telop_09_save_cta_background.png",
    "telop_10_follow_cta_background.png",
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
    query["prePhonemeLength"] = 0.05
    query["postPhonemeLength"] = 0.10
    output.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def main() -> None:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    frames = [FRAME_DIR / name for name in FRAME_FILES]
    for required in [*frames, FFMPEG, BGM]:
        if not required.exists():
            raise FileNotFoundError(required)

    padded_segments: list[Path] = []
    durations: list[float] = []
    for index, text in enumerate(VOICE_NARRATION, start=1):
        raw = AUDIO_DIR / f"voice_{index:02d}.wav"
        padded = WORK_DIR / f"voice_{index:02d}_timed.wav"
        synthesize(text, raw)
        duration = wav_duration(raw) + POST_FRAME_GAP
        run([
            FFMPEG, "-y", "-i", raw,
            "-af", f"apad=pad_dur={POST_FRAME_GAP:.3f},atrim=duration={duration:.3f}",
            "-ar", "44100", "-ac", "2", padded,
        ])
        padded_segments.append(padded)
        durations.append(duration)

    frame_list = WORK_DIR / "frames.txt"
    with frame_list.open("w", encoding="utf-8") as handle:
        for frame, duration in zip(frames, durations):
            handle.write(f"file '{frame.as_posix()}'\n")
            handle.write(f"duration {duration:.3f}\n")
        handle.write(f"file '{frames[-1].as_posix()}'\n")

    audio_list = WORK_DIR / "audio_segments.txt"
    with audio_list.open("w", encoding="utf-8") as handle:
        for segment in padded_segments:
            handle.write(f"file '{segment.as_posix()}'\n")

    narration = AUDIO_DIR / "mammo_cycle_timing_narration.wav"
    silent_video = WORK_DIR / "mammo_cycle_timing_silent.mp4"
    preview = ASSET_DIR / "マンモ予約_生理前の胸の張り_確認用.mp4"

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
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", preview,
    ])

    manifest = {
        "title": "生理前で胸が張る時、マンモの予約は変えた方がいい？",
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": "1.20x",
        "post_frame_gap_seconds": POST_FRAME_GAP,
        "narration_voice_only": [text for text in VOICE_NARRATION],
        "durations_seconds": [round(value, 3) for value in durations],
        "total_seconds": round(sum(durations), 3),
        "frames": [str(frame) for frame in frames],
        "narration_audio": str(narration),
        "preview_video": str(preview),
    }
    (ASSET_DIR / "video_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(preview)


if __name__ == "__main__":
    main()
