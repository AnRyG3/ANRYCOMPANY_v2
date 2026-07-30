from pathlib import Path
import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "ct_mri_cough_during_exam_20260729"
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
OUT = ASSET_DIR / "検査中に咳が出そうなとき我慢しなくて大丈夫.mp4"
FINAL_OUT = (
    ROOT
    / "01_ショート動画_リール_YouTubeShorts"
    / "インスタ完成形"
    / OUT.name
)

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
BGM_VOLUME = "-25dB"

FRAMES = [
    "s01_patient_cough_urge_telop.png",
    "s02_worried_about_disturbing_image_telop.png",
    "s03_pre_exam_reassurance_telop.png",
    "s04_exam_room_environment_telop.png",
    "s05_body_tension_from_overholding_telop.png",
    "s06_staff_can_confirm_telop.png",
    "s07_image_review_workstation_telop.png",
    "s08_hesitating_to_signal_telop.png",
    "s09_staff_intercom_reassurance_telop.png",
    "s10_cta_save_smartphone_telop.png",
    "s11_cta_follow_rt_tech_telop.png",
]

DISPLAY_NARRATION = [
    "検査中に咳が出そう。これ、我慢しないといけないんですよね。",
    "咳をしたら画像が乱れて、迷惑をかけてしまうんじゃないか。そんな不安、ありますよね。",
    "その気持ち、おかしくありません。",
    "実は、検査中に咳が出そうになる方は、珍しくありません。",
    "無理に我慢すると、かえって身体に力が入り、動いてしまうことがあります。",
    "咳が出そうなときは、無理に我慢しすぎなくて大丈夫です。咳が出たことも、スタッフ側で確認できます。",
    "必要に応じて、画像を確認したり、撮り直しをすることもあります。",
    "それでも、検査の途中で知らせていいのかと迷ってしまう。",
    "検査中も、スタッフは様子を確認しています。つらいときは、遠慮せずに知らせてください。",
    "不安なとき、思い出せるようにスマートフォンに保存しておいてください。",
    "検査のこと、これからも一緒に考えていきます。フォローして待っていてください。",
]

VOICE_TEXT = [
    "検査中に咳がでそう。これ、我慢しないといけないんですよね。",
    "咳をしたら画像が乱れて、迷惑をかけてしまうんじゃないか。そんな不安、ありますよね。",
    "その気持ち、おかしくありません。",
    "実は、検査中に、せきがでそうになるかたは、珍しくありません。",
    "無理に我慢すると、かえってからだに力が入り、動いてしまうことがあります。",
    "咳がでそうなときは、無理に我慢しすぎなくて大丈夫です。咳が出たことも、スタッフ側で確認できます。",
    "必要に応じて、画像を確認したり、撮り直しをすることもあります。",
    "それでも、検査の途中で知らせていいのかと、迷ってしまう。",
    "検査中も、スタッフは様子を確認しています。つらいときは、遠慮せずに知らせてください。",
    "不安なとき、思い出せるように、スマートフォンに保存しておいてください。",
    "検査のこと、これからも一緒に考えていきます。フォローして待っていてください。",
]

MIN_DURATIONS = [4.2, 5.8, 3.2, 4.2, 4.8, 6.2, 4.6, 4.0, 5.8, 4.8, 4.8]


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
    FINAL_OUT.parent.mkdir(parents=True, exist_ok=True)

    frame_paths = [FRAME_DIR / frame for frame in FRAMES]
    for required in [FFMPEG, BGM, *frame_paths]:
        if not required.exists():
            raise FileNotFoundError(required)

    padded_wavs = []
    durations = []
    for index, text in enumerate(VOICE_TEXT, start=1):
        voice = AUDIO_DIR / f"voice_{index:02d}.wav"
        padded = WORK_DIR / f"voice_{index:02d}_padded.wav"
        synthesize_voice(text, voice)
        duration = max(MIN_DURATIONS[index - 1], wav_duration(voice) + 0.35)
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
    frames_txt.write_text(
        "".join(
            f"file '{frame.as_posix()}'\nduration {duration:.3f}\n"
            for frame, duration in zip(frame_paths, durations)
        )
        + f"file '{frame_paths[-1].as_posix()}'\n",
        encoding="utf-8",
    )

    voice_txt = WORK_DIR / "voice_segments.txt"
    voice_txt.write_text("".join(f"file '{wav.as_posix()}'\n" for wav in padded_wavs), encoding="utf-8")

    silent_video = WORK_DIR / "silent.mp4"
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
            "-tune",
            "stillimage",
            "-pix_fmt",
            "yuv420p",
            silent_video,
        ]
    )
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
        "title": "検査中に咳が出そうなとき、我慢しなくて大丈夫？",
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
