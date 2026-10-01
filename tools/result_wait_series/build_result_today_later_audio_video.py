from pathlib import Path
import json
import subprocess
import urllib.parse
import urllib.request
import wave


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "result_wait_series" / "06_result_today_later"
FRAME_DIR = ASSET_DIR / "03_telop"
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_video_work"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
ASSET_VIDEO = ASSET_DIR / "CTやMRIを撮ったのに_結果は後日_なぜ.mp4"
FINAL_VIDEO = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形" / "CTやMRIを撮ったのに_結果は後日_なぜ.mp4"

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20

FRAMES = [
    "cut_01_after_scan_question_telop.png",
    "cut_02_reassurance_telop.png",
    "cut_03_confirm_time_telop.png",
    "cut_04_reading_room_telop.png",
    "cut_05_doctor_explanation_telop.png",
    "cut_06_large_hospital_telop.png",
    "cut_07_referral_return_telop.png",
    "cut_08_check_guidance_telop.png",
    "cut_09_save_follow_telop.png",
]

NARRATION = [
    "結果は後日。悪かったのかな。",
    "不安になりますよね。でも、後日だからといって、悪い結果とは限りません。",
    "会計の前に、結果をいつ、どこで聞くか、確認してください。",
    "撮影後は、放射線科医が画像を読み、報告書を作ることがあります。",
    "主治医は、診察内容と合わせて、結果を説明します。",
    "大学病院でも、結果の説明が別日になる施設があります。",
    "紹介検査では、結果が依頼元の病院へ返ることもあります。",
    "流れは、施設ごとに異なります。受診先の案内を確認してください。",
    "会計前に見返せるように、保存してください。検査の不安を減らす情報も、フォローでお届けします。",
]


def run(command: list[object]) -> None:
    subprocess.run([str(item) for item in command], check=True)


def post_json(path: str, params: dict | None = None, payload: dict | None = None) -> bytes:
    query = urllib.parse.urlencode(params or {})
    url = f"{VOICEVOX}{path}"
    if query:
        url += f"?{query}"
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=data, method="POST")
    if data is not None:
        request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def calm_sentence_ending(query: dict) -> dict:
    if not query.get("accent_phrases"):
        return query
    phrase = query["accent_phrases"][-1]
    voiced = [mora for mora in phrase["moras"] if mora.get("pitch", 0) > 0]
    for offset, mora in enumerate(voiced[-2:]):
        mora["pitch"] -= 0.12 + 0.08 * offset
    return query


def synthesize(text: str, output: Path) -> None:
    query = json.loads(post_json("/audio_query", {"text": text, "speaker": SPEAKER}))
    query["speedScale"] = 1.20
    query["pitchScale"] = 0.0
    query["intonationScale"] = 0.95
    query["volumeScale"] = 1.0
    query["prePhonemeLength"] = 0.05
    query["postPhonemeLength"] = 0.10
    output.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, calm_sentence_ending(query)))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as audio:
        return audio.getnframes() / audio.getframerate()


def main() -> None:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_VIDEO.parent.mkdir(parents=True, exist_ok=True)

    frame_paths = [FRAME_DIR / name for name in FRAMES]
    missing = [str(path) for path in [*frame_paths, FFMPEG, BGM] if not path.exists()]
    if missing:
        raise FileNotFoundError("\n".join(missing))

    audio_paths: list[Path] = []
    durations: list[float] = []
    for index, text in enumerate(NARRATION, start=1):
        output = AUDIO_DIR / f"voice_{index:02d}.wav"
        synthesize(text, output)
        audio_paths.append(output)
        durations.append(wav_duration(output))

    audio_list = WORK_DIR / "audio_segments.txt"
    with audio_list.open("w", encoding="utf-8") as file:
        for audio in audio_paths:
            file.write(f"file '{audio.as_posix()}'\n")

    video_list = WORK_DIR / "video_segments.txt"
    video_segments: list[Path] = []
    for index, (frame, duration) in enumerate(zip(frame_paths, durations), start=1):
        segment = WORK_DIR / f"video_{index:02d}.mp4"
        run([
            FFMPEG,
            "-y",
            "-loop", "1",
            "-i", frame,
            "-t", f"{duration:.3f}",
            "-vf", "scale=1080:1920,format=yuv420p",
            "-r", "30",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            segment,
        ])
        video_segments.append(segment)
    with video_list.open("w", encoding="utf-8") as file:
        for segment in video_segments:
            file.write(f"file '{segment.as_posix()}'\n")

    silent_video = WORK_DIR / "video_without_audio.mp4"
    narration_audio = AUDIO_DIR / "narration.wav"
    run([
        FFMPEG,
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", video_list,
        "-c", "copy",
        silent_video,
    ])
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", audio_list, "-c", "copy", narration_audio])
    run([
        FFMPEG,
        "-y",
        "-i", silent_video,
        "-i", narration_audio,
        "-stream_loop", "-1",
        "-i", BGM,
        "-filter_complex",
        "[1:a]volume=1.35[voice];[2:a]volume=-22dB[bgm];"
        "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
        "alimiter=limit=0.95[a]",
        "-map", "0:v",
        "-map", "[a]",
        "-shortest",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        ASSET_VIDEO,
    ])
    FINAL_VIDEO.write_bytes(ASSET_VIDEO.read_bytes())

    manifest = {
        "title": "CTやMRIを撮ったのに、結果は後日。なぜ？",
        "speaker": "VOICEVOX もち子さん normal style id 20",
        "voice_speed": 1.2,
        "bgm": str(BGM),
        "bgm_volume": "-22 dB",
        "narration": NARRATION,
        "frame_count": len(frame_paths),
        "durations_seconds": [round(duration, 3) for duration in durations],
        "total_seconds": round(sum(durations), 3),
        "extra_silence_between_segments_seconds": 0,
        "asset_video": str(ASSET_VIDEO),
        "final_video": str(FINAL_VIDEO),
    }
    (ASSET_DIR / "video_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig"
    )
    print(FINAL_VIDEO)


if __name__ == "__main__":
    main()
