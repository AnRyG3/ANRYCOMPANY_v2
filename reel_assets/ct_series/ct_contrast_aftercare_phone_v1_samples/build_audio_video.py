from pathlib import Path
import json
import math
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave


ASSET_DIR = Path(r"F:\ANRYCAMPANY\reel_assets\ct_series\ct_contrast_aftercare_phone_v1_samples")
FRAME_DIR = ASSET_DIR / "telop_frames"
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_video_work"
VIDEO_DIR = ASSET_DIR / "video"
FINAL_DIR = Path(r"F:\ANRYCAMPANY\01_ショート動画_リール_YouTubeShorts\インスタ完成形")
MANIFEST = ASSET_DIR / "video_manifest.json"
FFMPEG = Path(r"F:\ANRYCAMPANY\tools\ffmpeg\bin\ffmpeg.exe")
BGM = Path(r"F:\ANRYCAMPANY\01_ショート動画_リール_YouTubeShorts\インスタリール用\BGM フリー素材\Kind_Heart.mp3")
VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
BGM_VOLUME = "-25dB"

FRAMES = [
    "s01_home_question_telop.png",
    "s02_mild_fatigue_telop.png",
    "s03_call_facility_telop.png",
    "s04_time_passes_telop.png",
    "s05_emergency_119_telop.png",
    "s06_consultation_telop.png",
    "s07_contact_info_telop.png",
    "s08_save_share_telop.png",
]

# 読み上げ専用。画面の要点を保ちつつ、疑問符による不自然な引き延ばしを避ける。
VOICE_TEXT = [
    "造影検査のあと、家で気分が悪い。電話していいのかな、と迷いますよね。",
    "帰宅後、なんとなくだるく感じることもあります。",
    "気になる変化は、検査を受けた施設へ連絡して大丈夫です。",
    "時間が経ってから、症状が出ることもあります。",
    "呼吸が苦しい。意識がもうろうとする。急で強い症状は、ためらわず百十九番へ。",
    "迷う内容でも、遠慮せず相談してください。",
    "説明書と連絡先を、帰宅後もすぐ見られる場所に置いておくと安心です。",
    "帰宅後に見返せるよう保存。ご家族にも共有してください。",
]


def run(command: list[Path | str]) -> None:
    subprocess.run([str(value) for value in command], check=True)


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
            "pauseLengthScale": 0.75,
            "prePhonemeLength": 0.05,
            "postPhonemeLength": 0.08,
        }
    )
    output.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def main() -> None:
    for directory in [AUDIO_DIR, WORK_DIR, VIDEO_DIR, FINAL_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

    frame_paths = [FRAME_DIR / name for name in FRAMES]
    for required in [FFMPEG, BGM, *frame_paths]:
        if not required.exists():
            raise FileNotFoundError(required)

    voice_paths: list[Path] = []
    durations: list[float] = []
    for index, text in enumerate(VOICE_TEXT, start=1):
        voice_path = AUDIO_DIR / f"voice_{index:02d}.wav"
        synthesize_voice(text, voice_path)
        voice_paths.append(voice_path)
        durations.append(wav_duration(voice_path))

    voice_list = WORK_DIR / "voice_segments.txt"
    voice_list.write_text(
        "".join(f"file '{path.as_posix()}'\n" for path in voice_paths), encoding="utf-8"
    )
    voice_all = AUDIO_DIR / "voice.wav"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", voice_list, "-c", "copy", voice_all])

    video_segments: list[Path] = []
    for index, (frame, duration) in enumerate(zip(frame_paths, durations), start=1):
        segment = WORK_DIR / f"segment_{index:02d}.mp4"
        # H.264 は30fps単位になるため、音声より短く丸めない。
        video_duration = (math.ceil(duration * 30) + 1) / 30
        run(
            [
                FFMPEG, "-y", "-loop", "1", "-t", f"{video_duration:.3f}", "-i", frame,
                "-vf", "scale=1080:1920,format=yuv420p", "-r", "30", "-c:v", "libx264",
                "-tune", "stillimage", "-pix_fmt", "yuv420p", segment,
            ]
        )
        video_segments.append(segment)

    video_list = WORK_DIR / "video_segments.txt"
    video_list.write_text(
        "".join(f"file '{path.as_posix()}'\n" for path in video_segments), encoding="utf-8"
    )
    silent_video = WORK_DIR / "silent.mp4"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", video_list, "-c", "copy", silent_video])

    output = VIDEO_DIR / "造影検査後に帰宅してから気分が悪いとき.mp4"
    final_output = FINAL_DIR / output.name
    run(
        [
            FFMPEG, "-y", "-i", silent_video, "-i", voice_all, "-stream_loop", "-1", "-i", BGM,
            "-filter_complex",
            f"[1:a]volume=1.35[voice];[2:a]volume={BGM_VOLUME}[bgm];"
            "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
            "alimiter=limit=0.95[a]",
            "-map", "0:v", "-map", "[a]", "-shortest", "-c:v", "copy", "-c:a", "aac",
            "-b:a", "192k", "-movflags", "+faststart", output,
        ]
    )
    shutil.copy2(output, final_output)

    manifest = {
        "title": "造影検査後に帰宅してから気分が悪いとき",
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": VOICE_SPEED,
        "frames": [str(path) for path in frame_paths],
        "voice_text": VOICE_TEXT,
        "durations_seconds": [round(value, 3) for value in durations],
        "total_seconds": round(sum(durations), 3),
        "voice_audio": str(voice_all),
        "asset_video": str(output),
        "final_video": str(final_output),
        "notes": "各フレームは対応する音声の実測時間のみ表示。追加の無音パディングなし。",
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(output)
    print(round(sum(durations), 3))


if __name__ == "__main__":
    main()
