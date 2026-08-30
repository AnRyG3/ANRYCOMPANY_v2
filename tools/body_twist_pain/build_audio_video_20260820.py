from pathlib import Path
import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "body_twist_pain_20260820"
FRAME_DIR = ROOT / "reel_assets" / "body_twist_pain_telop_frames_20260820"
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_video_work"
VIDEO_DIR = ASSET_DIR / "video"
MANIFEST = ASSET_DIR / "video_manifest_20260820.json"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = (
    ROOT
    / "01_ショート動画_リール_YouTubeShorts"
    / "インスタリール用"
    / "BGM フリー素材"
    / "Kind_Heart.mp3"
)
FINAL_DIR = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形"

OUT = VIDEO_DIR / "体をひねる指示_痛みで途中までしかできない時_20260820.mp4"
FINAL_OUT = FINAL_DIR / OUT.name

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
BGM_VOLUME = "-25dB"

FRAMES = [
    "telop_01_patient_instruction_moment.png",
    "telop_02_patient_twist_limit.png",
    "telop_03_patient_feeling_accepted.png",
    "telop_04_patient_stops_within_range.png",
    "telop_05_patient_tells_limit.png",
    "telop_06_rt_checks_positioning.png",
    "telop_07_patient_relieved_after_telling.png",
    "telop_08_patient_raises_hand_pain.png",
    "telop_09_save_cta_phone.png",
    "telop_10_follow_cta_rt_closing.png",
]

DISPLAY_NARRATION = [
    "検査中に「もう少し体をひねってください」と言われたとき。",
    "でも、途中まで動かしたところで痛くて、それ以上動けない。ここで止まっていいのか、無理して続けるべきか、迷ってしまう。",
    "その気持ち、おかしくありません。",
    "実は、動ける範囲までで止めていただいて構いません。",
    "「ここまでしか無理です」と伝えていただければ、可能な範囲で姿勢や撮り方を確認しながら進めます。",
    "最後まで動かせたかどうかより、正確に伝えていただくことの方が大切です。",
    "それでも、「途中でやめたら迷惑かな」と、感じてしまうことがある。途中で伝えていただくことは、迷惑ではなく、安全に進めるための大事な情報です。",
    "痛みが強くなったときは、我慢せずその場で伝えていただいて大丈夫です。",
    "検査前に不安になった時に見返せるよう、「ここまでしか無理」と伝えていいこと、保存しておいてください。",
    "検査のリアルをこれからも届けます。次も見たい方はフォローしてお待ちください。",
]

VOICE_TEXT = [
    "検査中に、もう少し体をひねってください、と言われたとき。",
    "でも、途中まで動かしたところで痛くて、それ以上動けない。ここで止まっていいのか、無理して続けるべきか、迷ってしまう。",
    "その気持ち、おかしくありません。",
    "実は、動ける範囲までで止めていただいて構いません。",
    "ここまでしか無理です、と伝えていただければ、可能な範囲で姿勢や撮りかたを確認しながら進めます。",
    "最後まで動かせたかどうかより、正確に伝えていただくことのほうが大切です。",
    "それでも、途中でやめたら迷惑かなと、感じてしまうことがある。途中で伝えていただくことは、迷惑ではなく、安全に進めるための大事な情報です。",
    "痛みが強くなったときは、我慢せず、その場で伝えていただいて大丈夫です。",
    "検査前に不安になった時に見返せるよう、ここまでしか無理、と伝えていいこと、保存しておいてください。",
    "検査のリアルを、これからも届けます。次も見たいかたは、フォローしてお待ちください。",
]

MIN_DURATIONS = [2.8, 5.6, 2.4, 3.4, 5.8, 4.2, 7.4, 4.8, 6.2, 4.8]


def run(cmd: list[Path | str]) -> None:
    subprocess.run([str(part) for part in cmd], check=True)


def post_json(path: str, params=None, payload=None) -> bytes:
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
            "prePhonemeLength": 0.08,
            "postPhonemeLength": 0.16,
        }
    )
    output.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


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
    for index, text in enumerate(VOICE_TEXT, start=1):
        voice = AUDIO_DIR / f"voice_{index:02d}.wav"
        padded = WORK_DIR / f"voice_{index:02d}_padded.wav"
        synthesize_voice(text, voice)
        duration = max(MIN_DURATIONS[index - 1], wav_duration(voice) + 0.18)
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

    silent_video = WORK_DIR / "silent.mp4"
    voice_all = AUDIO_DIR / "voice.wav"
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

    manifest = {
        "title": "体をひねる指示、痛みで途中までしかできない時",
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": VOICE_SPEED,
        "bgm": str(BGM),
        "bgm_volume": BGM_VOLUME,
        "frames": [str(path) for path in frame_paths],
        "display_narration": DISPLAY_NARRATION,
        "voice_text": VOICE_TEXT,
        "durations_seconds": [round(value, 3) for value in durations],
        "total_seconds": round(sum(durations), 3),
        "voice_audio": str(voice_all),
        "asset_video": str(OUT),
        "final_video": str(FINAL_OUT),
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(OUT)
    print(FINAL_OUT)
    print(round(sum(durations), 3))


if __name__ == "__main__":
    main()
