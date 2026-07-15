from pathlib import Path
import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "bone_healing_xray_check_video"
FRAME_DIR = ROOT / "reel_assets" / "bone_healing_xray_check_telop_frames"
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_work"
FINAL_DIR = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"

TITLE = "骨がくっついたかどうか_レントゲンだけでわかるの"
OUT = ASSET_DIR / f"{TITLE}.mp4"
FINAL_OUT = FINAL_DIR / f"{TITLE}.mp4"
MANIFEST = ASSET_DIR / "video_manifest.json"

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
BGM_VOLUME = "-27dB"

FRAMES = [FRAME_DIR / f"frame_{idx:02d}_telop.png" for idx in range(1, 13)]

NARRATION = [
    "そろそろ骨がくっついてる頃かな。レントゲンだけで本当にわかるのかな。そう感じること、ありますよね。",
    "はい。多くの場合は、X線写真、いわゆるレントゲンで骨のくっつき具合を確認できます。",
    "骨折した部分には、新しい骨、かこつが少しずつできてきます。",
    "そのかこつが骨折線をしっかりまたいでいるかどうかを見て、くっつき具合を判断しています。",
    "私たちが撮影するときも、骨折した部分がはっきり写る向きを意識しています。",
    "ただ、骨折の場所や写り方によっては、くっつき具合をはっきり判断しづらいこともあります。",
    "そういうときは、医師の判断でシーティーなどを使って、より詳しく確認することもあります。",
    "これは骨のくっつき方が一人ひとり違うためで、決して珍しいことではありません。",
    "レントゲンだけで大丈夫かなと、心配しすぎなくて大丈夫です。必要に応じて丁寧に確認しています。",
    "次に骨のくっつき具合を確認することがあれば、医師の判断を信頼して、安心してくださいね。",
    "この投稿、スマートフォンに保存しておくと安心です。",
    "診療放射線技師の発信。フォローで応援お願いします。",
]

MIN_DURATIONS = [5.6, 4.1, 4.3, 5.7, 5.2, 5.5, 5.2, 5.0, 6.5, 5.8, 4.0, 4.0]


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

    for idx, text in enumerate(NARRATION, start=1):
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
