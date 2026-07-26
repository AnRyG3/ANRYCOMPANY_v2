from pathlib import Path
import json
import subprocess
import urllib.parse
import urllib.request
import wave


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "result_wait_series" / "additional_shot_question_04"
FRAME_DIR = ASSET_DIR / "02_telop"
WORK_DIR = ASSET_DIR / "_video_work"
AUDIO_DIR = ASSET_DIR / "audio"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
OUT = ASSET_DIR / "もう一枚撮ります_悪いものが写ったのかな.mp4"
FINAL_OUT = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形" / "もう一枚撮ります_悪いものが写ったのかな.mp4"

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20

FRAMES = [
    "frame_01_opening_telop.png",
    "frame_02_monitor_glance_telop.png",
    "frame_03_reassurance_telop.png",
    "frame_04_image_check_telop.png",
    "frame_05_exam_table_telop.png",
    "frame_06_role_explanation_telop.png",
    "frame_07_routine_operation_telop.png",
    "frame_08_after_exam_concern_telop.png",
    "frame_09_ask_staff_telop.png",
    "frame_10_save_cta_bg_telop.png",
    "frame_11_follow_cta_bg_telop.png",
]

NARRATION = [
    "「もう一枚撮ります」って言われると、悪いものが写ったのかなって、少し身構えてしまう。",
    "悪いものが写ってしまったんじゃないかと、不安になることがあります。",
    "その気持ち、おかしくありません。",
    "実は、写り方や体の向きを確認するために、追加で撮影することがあります。",
    "少しのズレや動きでも、確認のために撮り直すことがあります。",
    "画像の診断は医師が行います。診療放射線技師は、その場で診断結果としてお伝えすることはできません。",
    "だからこそ、追加の撮影は、珍しいことではありません。",
    "それでも、何か見つかったのでは、と気になってしまう。",
    "気になるときは、遠慮せずに聞いてください。検査の流れや撮り直しの理由など、分かる範囲でお伝えします。",
    "不安になったとき思い出せるように、保存しておいてください。",
    "検査のこと、これからも一緒に考えていきます。フォローして待っていてください。",
]


def run(cmd: list[object]) -> None:
    subprocess.run([str(part) for part in cmd], check=True)


def post_json(path: str, params=None, payload=None) -> bytes:
    query = urllib.parse.urlencode(params or {})
    url = f"{VOICEVOX}{path}"
    if query:
        url += f"?{query}"
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    if body is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=60) as res:
        return res.read()


def calm_sentence_ending(query: dict) -> dict:
    if not query.get("accent_phrases"):
        return query
    phrase = query["accent_phrases"][-1]
    voiced = [mora for mora in phrase["moras"] if mora.get("pitch", 0) > 0]
    for offset, mora in enumerate(voiced[-2:]):
        mora["pitch"] -= 0.12 + (0.08 * offset)
    return query


def synthesize_voice(text: str, out: Path) -> None:
    query = json.loads(post_json("/audio_query", {"text": text, "speaker": SPEAKER}))
    query["speedScale"] = 1.20
    query["pitchScale"] = 0.0
    query["intonationScale"] = 0.95
    query["volumeScale"] = 1.0
    query["prePhonemeLength"] = 0.08
    query["postPhonemeLength"] = 0.16
    calm_sentence_ending(query)
    out.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def main() -> None:
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_OUT.parent.mkdir(parents=True, exist_ok=True)

    frame_paths = [FRAME_DIR / name for name in FRAMES]
    missing = [str(path) for path in frame_paths if not path.exists()]
    if missing:
        raise FileNotFoundError("\n".join(missing))
    for required in [FFMPEG, BGM]:
        if not required.exists():
            raise FileNotFoundError(required)

    padded_wavs: list[Path] = []
    durations: list[float] = []
    for idx, text in enumerate(NARRATION, start=1):
        voice = AUDIO_DIR / f"voice_{idx:02d}.wav"
        padded = WORK_DIR / f"voice_{idx:02d}_padded.wav"
        synthesize_voice(text, voice)
        voice_duration = wav_duration(voice)
        min_duration = 2.7
        if idx in {6, 9, 11}:
            min_duration = 4.0
        elif idx in {1, 4, 5, 10}:
            min_duration = 3.2
        duration = max(min_duration, voice_duration + 0.45)
        durations.append(duration)
        run([
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
        ])
        padded_wavs.append(padded)

    frames_txt = WORK_DIR / "frames.txt"
    with frames_txt.open("w", encoding="utf-8") as f:
        for frame, duration in zip(frame_paths, durations):
            f.write(f"file '{frame.as_posix()}'\n")
            f.write(f"duration {duration:.3f}\n")
        f.write(f"file '{frame_paths[-1].as_posix()}'\n")

    voice_txt = WORK_DIR / "voice_segments.txt"
    with voice_txt.open("w", encoding="utf-8") as f:
        for wav in padded_wavs:
            f.write(f"file '{wav.as_posix()}'\n")

    silent = WORK_DIR / "silent.mp4"
    voice_all = AUDIO_DIR / "voice.wav"
    run([
        FFMPEG,
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        frames_txt,
        "-vf",
        "scale=1080:1920,format=yuv420p",
        "-r",
        "30",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        silent,
    ])
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", voice_txt, "-c", "copy", voice_all])
    run([
        FFMPEG,
        "-y",
        "-i",
        silent,
        "-i",
        voice_all,
        "-stream_loop",
        "-1",
        "-i",
        BGM,
        "-filter_complex",
        "[1:a]volume=1.35[voice];[2:a]volume=-22dB[bgm];"
        "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=1:normalize=0,"
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
        OUT,
    ])
    FINAL_OUT.write_bytes(OUT.read_bytes())

    manifest = {
        "title": "「もう一枚撮ります」って、悪いものが写ったってこと？",
        "speaker": "VOICEVOX style id 20",
        "voice_speed": 1.2,
        "bgm": str(BGM),
        "bgm_volume": "-22 dB",
        "frames": [str(path) for path in frame_paths],
        "narration": NARRATION,
        "durations_seconds": [round(value, 3) for value in durations],
        "total_seconds": round(sum(durations), 3),
        "asset_video": str(OUT),
        "final_video": str(FINAL_OUT),
    }
    (ASSET_DIR / "video_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8-sig",
    )
    print(FINAL_OUT)


if __name__ == "__main__":
    main()
