from pathlib import Path
import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "exam_anxiety_tell_staff_bridge"
FRAME_DIR = ASSET_DIR / "text_frames_approved_v2"
AUDIO_DIR = ASSET_DIR / "audio_approved_v2"
WORK_DIR = ASSET_DIR / "_video_work_approved_v2"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
OUT = ASSET_DIR / "検査中に気分が悪くなったら伝えて大丈夫です_v2.mp4"
FINAL_OUT = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形" / OUT.name

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
BGM_VOLUME = "-25dB"

FRAMES = [
    "01_text_patient_unwell_ct.png",
    "02_text_rt_tech_reassuring_distance.png",
    "03_text_clean_exam_room_symptoms.png",
    "04_text_patient_hesitates.png",
    "05_text_rt_tech_monitor_attention.png",
    "06_text_contrast_iv_line_closeup.png",
    "07_text_patient_speaks_to_rt_no_gantry.png",
    "08_text_patient_resting.png",
    "09_text_rt_tech_reassuring_nod.png",
    "10_text_patient_leaves_relaxed.png",
    "11_text_smartphone_save_cta.png",
    "12_text_rt_tech_bowing_cta.png",
]

DISPLAY_NARRATION = [
    "検査中、なんだか気分が悪くなった。でも、今さら言えないと我慢してしまったこと、ありませんか。",
    "そのサイン、我慢せずにすぐ伝えてもらって大丈夫です。",
    "めまい、冷や汗、気持ち悪さ。体調の変化には、いろいろな形があります。",
    "検査を台無しにしたくない。迷惑をかけたくない。そう思ってしまいますよね。",
    "でも私たち診療放射線技師は、そういう小さな変化にこそ気づきたいと思っています。",
    "造影剤を使う検査や、長い時間同じ姿勢を保つ検査では、体調の変化を感じることがあります。",
    "気持ち悪いです。めまいがします。その一言だけで十分です。",
    "必要であれば、検査を一時中断して、休んでいただくこともできます。",
    "体調を伝えたからといって、検査そのものが失敗になるわけではありません。",
    "我慢せずに伝えることが、安心して検査を受けるための一歩になります。",
    "この情報、あとで見返したいという方は、スマートフォンに保存しておいてください。",
    "診療放射線技師の発信、フォローで応援お願いします。",
]

VOICEVOX_TEXT = [
    "検査中、なんだか気分が悪くなった。でも、今さら言えないと我慢してしまったこと、ありませんか。",
    "そのサイン、我慢せずにすぐ伝えてもらって大丈夫です。",
    "めまい、冷や汗、気持ち悪さ。体調の変化には、いろいろな形があります。",
    "検査を台無しにしたくない。迷惑をかけたくない。そう思ってしまいますよね。",
    "でも私たち診療放射線技師は、そういう小さな変化にこそ気づきたいと思っています。",
    "造影剤を使う検査や、長い時間同じ姿勢を保つ検査では、体調の変化を感じることがあります。",
    "気持ち悪いです。めまいがします。その一言だけで十分です。",
    "必要であれば、検査を一時中断して、休んでいただくこともできます。",
    "体調を伝えたからといって、検査そのものが失敗になるわけではありません。",
    "我慢せずに伝えることが、安心して検査を受けるための一歩になります。",
    "この情報、あとで見返したいというかたは、スマートフォンに保存しておいてください。",
    "診療放射線技師の発信、フォローで応援お願いします。",
]
MIN_DURATIONS = [5.2, 3.3, 4.2, 4.4, 4.8, 5.8, 4.0, 4.2, 4.3, 4.5, 4.4, 4.0]


def run(cmd: list[Path | str]) -> None:
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
    with urllib.request.urlopen(req, timeout=90) as res:
        return res.read()


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

    manifest = {
        "output": str(OUT),
        "final_output": str(FINAL_OUT),
        "frames": [str(path) for path in frame_paths],
        "audio": str(voice_all),
        "bgm": str(BGM),
        "speaker": SPEAKER,
        "voice_speed": VOICE_SPEED,
        "durations": durations,
        "display_narration": DISPLAY_NARRATION,
    }
    (ASSET_DIR / "video_manifest_approved_v2.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(OUT)
    print(FINAL_OUT)


if __name__ == "__main__":
    main()
