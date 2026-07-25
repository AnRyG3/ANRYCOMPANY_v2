from pathlib import Path
import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "sample_frames" / "movement_retake_f70_20260725"
FRAME_DIR = ASSET_DIR / "telop_frames"
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_video_work"
MANIFEST = ASSET_DIR / "video_manifest.json"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = (
    ROOT
    / "01_ショート動画_リール_YouTubeShorts"
    / "インスタリール用"
    / "BGM フリー素材"
    / "Kind_Heart.mp3"
)
OUT = ASSET_DIR / "検査中に動いてしまったら_撮り直しは想定内.mp4"
FINAL_OUT = (
    ROOT
    / "01_ショート動画_リール_YouTubeShorts"
    / "インスタ完成形"
    / "検査中に動いてしまったら_撮り直しは想定内.mp4"
)

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
BGM_VOLUME = "-25dB"

FRAMES = [
    "frame_01_telop.png",
    "frame_02_telop.png",
    "frame_03_telop.png",
    "frame_04_telop.png",
    "frame_05_telop.png",
    "frame_06_telop.png",
    "frame_07_telop.png",
    "frame_08_telop.png",
    "frame_09_telop.png",
    "frame_10_telop.png",
    "frame_11_telop.png",
]

DISPLAY_NARRATION = [
    "検査中に少し動いてしまったら、もう一度撮り直しになるのかな。そう感じて、不安になることがありますよね。",
    "迷惑をかけてしまったのでは、と気にされる方もいます。その気持ちは、決しておかしくありません。",
    "その気持ちは自然です。検査の場面では、そう感じる患者さんも少なくありません。",
    "検査中に同じ姿勢でいることは、思っている以上に難しいものです。",
    "動いてしまうことや、指示のタイミングが合わないことも、現場では想定しながら検査を進めています。",
    "うまくできない場面があっても、こちらで確認しながら対応します。",
    "必要な時は医師にも確認し、より良い画像を届けられるように調整します。",
    "それでも、また動いたらどうしよう、と不安になることはあります。",
    "難しい時は、遠慮せずに伝えてください。一緒に、できる方法を考えていきます。",
    "不安な時に思い出せるように、スマートフォンに保存しておいてください。",
    "検査のこと、これからも一緒に考えていきます。フォローして待っていてください。",
]

VOICEVOX_TEXT = [
    "検査中に少し動いてしまったら、もう一度撮り直しになるのかな。そう感じて、不安になることがありますよね。",
    "迷惑をかけてしまったのでは、と気にされるかたもいます。その気持ちは、決しておかしくありません。",
    "その気持ちは自然です。検査の場面では、そう感じる患者さんも少なくありません。",
    "検査中に同じ姿勢でいることは、思っている以上に難しいものです。",
    "動いてしまうことや、指示のタイミングが合わないことも、現場では想定しながら検査を進めています。",
    "うまくできない場面があっても、こちらで確認しながら対応します。",
    "必要な時は医師にも確認し、より良い画像を届けられるように調整します。",
    "それでも、また動いたらどうしよう、と不安になることはあります。",
    "難しい時は、遠慮せずに伝えてください。一緒に、できる方法を考えていきます。",
    "不安な時に思い出せるように、スマートフォンに保存しておいてください。",
    "検査のこと、これからも一緒に考えていきます。フォローして待っていてください。",
]

MIN_DURATIONS = [5.0, 5.0, 4.8, 3.7, 5.4, 3.8, 5.2, 4.2, 5.2, 4.6, 4.8]


def run(cmd: list[Path | str]) -> None:
    subprocess.run([str(part) for part in cmd], check=True)


def post_json(path: str, params=None, payload=None) -> bytes:
    query = urllib.parse.urlencode(params or {})
    url = f"{VOICEVOX}{path}" + (f"?{query}" if query else "")
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    if body is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=90) as res:
        return res.read()


def check_voicevox() -> None:
    urllib.request.urlopen(f"{VOICEVOX}/version", timeout=5).read()


def synthesize_voice(text: str, out: Path) -> None:
    query = json.loads(post_json("/audio_query", {"text": text, "speaker": SPEAKER}))
    query["speedScale"] = VOICE_SPEED
    query["pitchScale"] = 0.0
    query["intonationScale"] = 0.95
    query["volumeScale"] = 1.0
    query["prePhonemeLength"] = 0.08
    query["postPhonemeLength"] = 0.16
    out.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def main() -> None:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_OUT.parent.mkdir(parents=True, exist_ok=True)

    frame_paths = [FRAME_DIR / name for name in FRAMES]
    for required in [FFMPEG, BGM, *frame_paths]:
        if not required.exists():
            raise FileNotFoundError(required)
    check_voicevox()

    padded_wavs = []
    durations = []
    for idx, text in enumerate(VOICEVOX_TEXT, start=1):
        voice = AUDIO_DIR / f"voice_{idx:02d}.wav"
        padded = WORK_DIR / f"voice_{idx:02d}_padded.wav"
        synthesize_voice(text, voice)
        duration = max(MIN_DURATIONS[idx - 1], wav_duration(voice) + 0.35)
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

    run(
        [
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
        ]
    )
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", voice_txt, "-c", "copy", voice_all])
    run(
        [
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
            f"[1:a]volume=1.45[voice];[2:a]volume={BGM_VOLUME}[bgm];"
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
            "-movflags",
            "+faststart",
            OUT,
        ]
    )
    shutil.copy2(OUT, FINAL_OUT)

    script_path = ASSET_DIR / "voicevox_script.md"
    script_path.write_text(
        "# VOICEVOX読み上げ用\n\n"
        "## 表示用ナレーション\n\n"
        + "\n\n".join(f"{idx}. {text}" for idx, text in enumerate(DISPLAY_NARRATION, start=1))
        + "\n\n## VOICEVOX入力文\n\n"
        + "\n\n".join(f"{idx}. {text}" for idx, text in enumerate(VOICEVOX_TEXT, start=1))
        + "\n",
        encoding="utf-8",
    )

    manifest = {
        "title": "検査中に動いてしまったら",
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": VOICE_SPEED,
        "bgm": str(BGM),
        "bgm_volume": BGM_VOLUME,
        "frames": [str(path) for path in frame_paths],
        "display_narration": DISPLAY_NARRATION,
        "voicevox_text": VOICEVOX_TEXT,
        "durations_seconds": [round(value, 3) for value in durations],
        "total_seconds": round(sum(durations), 3),
        "voice_audio": str(voice_all),
        "asset_video": str(OUT),
        "final_video": str(FINAL_OUT),
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(FINAL_OUT)


if __name__ == "__main__":
    main()
