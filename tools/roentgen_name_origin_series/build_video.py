from pathlib import Path
import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "roentgen_name_origin_video"
FRAME_DIR = ROOT / "reel_assets" / "roentgen_name_origin_telop_frames"
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_work"
FINAL_DIR = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = (
    ROOT
    / "01_ショート動画_リール_YouTubeShorts"
    / "インスタリール用"
    / "BGM フリー素材"
    / "Kind_Heart.mp3"
)

TITLE = "レントゲンって実は人の名前だった"
OUT = ASSET_DIR / f"{TITLE}.mp4"
FINAL_OUT = FINAL_DIR / f"{TITLE}.mp4"
MANIFEST = ASSET_DIR / "video_manifest.json"

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
BGM_VOLUME = "-27dB"

FRAMES = [FRAME_DIR / f"frame_{idx:02d}_telop.png" for idx in range(1, 14)]

NARRATION = [
    "「レントゲンを撮りましょう」。病院でよく聞くこの言葉。実は、もともと人の名前だって知っていましたか。",
    "え、検査の名前じゃないの？と思った方も多いかもしれません。",
    "「レントゲン」は、ドイツの物理学者、ヴィルヘルム・コンラート・レントゲンさんの名前に由来しています。",
    "彼が発見したのが、目に見えない不思議な光。これが、X線です。",
    "ここで大事なのは、「レントゲン」は本来、検査そのものの正式名称ではないということです。",
    "正確には、「X線写真」や「X線検査」と呼ぶのが本来の言い方です。",
    "ただ、日本では発見者の名前である「レントゲン」という呼び方が、長く一般的に使われてきました。",
    "医療従事者も、患者さんに伝わりやすいように「レントゲン」と言うことがあります。",
    "でも、言葉として正確に言うなら「X線写真」。ここは知っておくと、ちょっと面白い豆知識です。",
    "つまり、「レントゲン」は検査名として広まった言葉ですが、もともとはX線を発見した人物の名前なんです。",
    "次に病院で「レントゲン」と聞いたとき、少しだけ見え方が変わるかもしれません。",
    "今日の豆知識、あとで見返したい方は保存してくださいね。",
    "診療放射線技師の目線で、検査のことをわかりやすく発信しています。フォローで応援お願いします。",
]

VOICE_TEXT = [
    "レントゲンを撮りましょう。病院でよく聞くこの言葉。実は、もともと人の名前だって知っていましたか。",
    "え、検査の名前じゃないの、と思ったかたも多いかもしれません。",
    "レントゲンは、ドイツの物理学者、ヴィルヘルム、コンラート、レントゲンさんの名前に由来しています。",
    "彼が発見したのが、目に見えない不思議な光。これが、エックス線です。",
    "ここで大事なのは、レントゲンは本来、検査そのものの正式名称ではないということです。",
    "正確には、エックス線写真や、エックス線検査、と呼ぶのが本来の言い方です。",
    "ただ、日本では発見者の名前である、レントゲン、という呼び方が、長く一般的に使われてきました。",
    "医療従事者も、患者さんに伝わりやすいように、レントゲン、と言うことがあります。",
    "でも、言葉として正確に言うなら、エックス線写真。ここは知っておくと、ちょっと面白い豆知識です。",
    "つまり、レントゲンは検査名として広まった言葉ですが、もともとはエックス線を発見した人物の名前なんです。",
    "次に病院で、レントゲン、と聞いたとき、少しだけ見え方が変わるかもしれません。",
    "今日の豆知識、あとで見返したいかたは、保存してくださいね。",
    "診療放射線技師の目線で、検査のことをわかりやすく発信しています。フォローで応援お願いします。",
]

MIN_DURATIONS = [5.8, 4.0, 5.8, 4.2, 5.2, 4.6, 5.4, 4.6, 5.8, 6.0, 4.8, 3.8, 5.4]


def run(cmd: list[Path | str]) -> None:
    subprocess.run([str(part) for part in cmd], check=True)


def post_json(path: str, params=None, payload=None) -> bytes:
    query = urllib.parse.urlencode(params or {})
    url = f"{VOICEVOX}{path}"
    if query:
        url += f"?{query}"
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST")
    if body is not None:
        request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def synthesize_voice(text: str, out: Path) -> None:
    query = json.loads(post_json("/audio_query", {"text": text, "speaker": SPEAKER}))
    query["speedScale"] = VOICE_SPEED
    query["pitchScale"] = 0.0
    query["intonationScale"] = 0.96
    query["volumeScale"] = 1.0
    query["prePhonemeLength"] = 0.08
    query["postPhonemeLength"] = 0.16
    out.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def verify_inputs() -> None:
    for required in [FFMPEG, BGM, *FRAMES]:
        if not required.exists():
            raise FileNotFoundError(required)
    urllib.request.urlopen(f"{VOICEVOX}/version", timeout=5).read()


def build_audio() -> tuple[list[float], Path]:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    padded_wavs = []
    durations = []

    for idx, text in enumerate(VOICE_TEXT, start=1):
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

    voice_list = WORK_DIR / "voice_segments.txt"
    with voice_list.open("w", encoding="utf-8") as file:
        for wav in padded_wavs:
            file.write(f"file '{wav.as_posix()}'\n")

    voice_all = AUDIO_DIR / "voice.wav"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", voice_list, "-c", "copy", voice_all])
    return durations, voice_all


def build_video(durations: list[float], voice_all: Path) -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)

    frame_list = WORK_DIR / "frames.txt"
    with frame_list.open("w", encoding="utf-8") as file:
        for frame, duration in zip(FRAMES, durations):
            file.write(f"file '{frame.as_posix()}'\n")
            file.write(f"duration {duration:.3f}\n")
        file.write(f"file '{FRAMES[-1].as_posix()}'\n")

    silent_video = WORK_DIR / "silent.mp4"
    run(
        [
            FFMPEG,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            frame_list,
            "-vf",
            "scale=1080:1920,format=yuv420p",
            "-r",
            "30",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            silent_video,
        ]
    )
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


def write_manifest(durations: list[float], voice_all: Path) -> None:
    MANIFEST.write_text(
        json.dumps(
            {
                "title": TITLE,
                "speaker": f"VOICEVOX speaker id {SPEAKER}",
                "voice_speed": VOICE_SPEED,
                "bgm": str(BGM),
                "bgm_volume": BGM_VOLUME,
                "frames": [str(path) for path in FRAMES],
                "narration": NARRATION,
                "voice_text": VOICE_TEXT,
                "durations_seconds": [round(value, 3) for value in durations],
                "total_seconds": round(sum(durations), 3),
                "voice_audio": str(voice_all),
                "asset_video": str(OUT),
                "final_video": str(FINAL_OUT),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8-sig",
    )


def main() -> None:
    verify_inputs()
    durations, voice_all = build_audio()
    build_video(durations, voice_all)
    write_manifest(durations, voice_all)
    print(OUT)
    print(FINAL_OUT)


if __name__ == "__main__":
    main()
