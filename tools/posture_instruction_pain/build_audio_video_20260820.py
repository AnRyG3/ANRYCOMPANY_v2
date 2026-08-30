from pathlib import Path
import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "posture_instruction_pain_20260820"
FRAME_DIR = ROOT / "reel_assets" / "posture_instruction_pain_telop_frames_20260820"
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

OUT = VIDEO_DIR / "姿勢の指示が痛くてつらい時_20260820.mp4"
FINAL_OUT = FINAL_DIR / OUT.name

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
BGM_VOLUME = "-25dB"
TAIL_PAD_SECONDS = 0.14

FRAMES = [
    "telop_01_opening_patient_pain_pause.png",
    "telop_02_patient_endures_pain.png",
    "telop_03_patient_hesitates_to_speak.png",
    "telop_04_patient_feeling_accepted.png",
    "telop_05_patient_stops_before_forcing.png",
    "telop_06_rt_checks_before_posture.png",
    "telop_07_patient_tells_rt.png",
    "telop_08_rt_accepts_pain_report.png",
    "telop_09_adjusted_posture_ready.png",
    "telop_10_save_cta_phone.png",
]

DISPLAY_NARRATION = [
    "「この姿勢、痛くて動けないかも」と思った時。",
    "それでも、「これくらい我慢すればいいか」と、痛みを抑え込んでしまう。",
    "申告すると迷惑がられるのではと、言い出せずにいる。",
    "その気持ち、おかしくありません。",
    "強い痛みを我慢して、無理に動く必要はありません。",
    "診療放射線技師は、姿勢の指示の前後で、無理がないか確認しながら進めます。",
    "それでも伝えにくいと感じたときは、遠慮なく伝えていただいて大丈夫です。",
    "「大げさに思われないか」と、ためらってしまうこともあります。痛みを伝えることは、大げさなことではありません。",
    "我慢するより、伝えていただく方が、検査を進めやすくなります。",
    "自分や家族の検査前に見返せるように、保存しておいてください。検査のリアルをこれからも届けます。フォローしてお待ちください。",
]

VOICE_TEXT = [
    "この姿勢、痛くて動けないかも、と思った時。",
    "それでも、これくらい我慢すればいいかと、痛みを抑え込んでしまう。",
    "申告すると迷惑がられるのではと、言い出せずにいる。",
    "その気持ち、おかしくありません。",
    "強い痛みを我慢して、無理に動く必要はありません。",
    "診療放射線技師は、姿勢の指示の前後で、無理がないか確認しながら進めます。",
    "それでも伝えにくいと感じたときは、遠慮なく伝えていただいて大丈夫です。",
    "大げさに思われないかと、ためらってしまうこともあります。痛みを伝えることは、大げさなことではありません。",
    "我慢するより、伝えていただくほうが、検査を進めやすくなります。",
    "自分や家族の検査前に見返せるように、保存しておいてください。検査のリアルを、これからも届けます。フォローしてお待ちください。",
]


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
            "postPhonemeLength": 0.14,
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
    voice_durations: list[float] = []
    for index, text in enumerate(VOICE_TEXT, start=1):
        voice = AUDIO_DIR / f"voice_{index:02d}.wav"
        padded = WORK_DIR / f"voice_{index:02d}_padded.wav"
        synthesize_voice(text, voice)
        voice_duration = wav_duration(voice)
        duration = voice_duration + TAIL_PAD_SECONDS
        voice_durations.append(voice_duration)
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
        "title": "姿勢の指示が痛くてつらい時",
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": VOICE_SPEED,
        "tail_pad_seconds": TAIL_PAD_SECONDS,
        "bgm": str(BGM),
        "bgm_volume": BGM_VOLUME,
        "frames": [str(path) for path in frame_paths],
        "display_narration": DISPLAY_NARRATION,
        "voice_text": VOICE_TEXT,
        "voice_durations_seconds": [round(value, 3) for value in voice_durations],
        "segment_durations_seconds": [round(value, 3) for value in durations],
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
