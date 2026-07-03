from pathlib import Path
import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "xray_clothing_wrinkles_buttons_v1"
FRAME_DIR = ASSET_DIR / "telop_frames"
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_video_work"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"

TITLE = "レントゲンで服のしわやボタンは写るの"
OUT = ASSET_DIR / f"{TITLE}.mp4"
FINAL_OUT = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形" / f"{TITLE}.mp4"
MANIFEST = ASSET_DIR / "video_manifest.json"

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2

FRAMES = [
    "frame_01_patient_worried_gown_telop.png",
    "frame_02_rt_reassures_patient_telop.png",
    "frame_03_gown_handoff_telop.png",
    "frame_04_pre_shoot_check_telop.png",
    "frame_05_rt_monitor_prep_telop.png",
    "frame_06_patient_relaxed_xray_position_telop.png",
    "frame_07_metal_buttons_clothing_telop.png",
    "frame_08_button_shadow_monitor_telop.png",
    "frame_09_change_guidance_telop.png",
    "frame_10_smooth_exam_exchange_telop.png",
    "frame_11_save_cta_background_telop.png",
    "frame_12_follow_cta_background_telop.png",
]

DISPLAY_NARRATION = [
    "服にしわがあると、ちゃんと写らないんじゃ、と思ったことはありませんか。",
    "実は、そこまで心配しなくて大丈夫です。",
    "検査着に着替えていただいたり、しわが出にくい体勢を、診療放射線技師がご案内しています。",
    "撮影前に、しわが入っていないかを確認してから撮影しています。",
    "事前に確認しているので、安心して検査を受けていただけます。",
    "患者さんご自身が気にしすぎなくても、現場でちゃんと確認しています。",
    "一方でボタンは、素材や位置によって写り込むことがあります。",
    "金属製のボタンなどは、画像に影響することがあるためです。",
    "検査着に着替えていただいたり、外していただくことがあります。",
    "これも、検査をスムーズに進めるための工夫のひとつです。",
    "知らなかった、という方は、ぜひ保存してくださいね。",
    "他の検査の疑問も、このアカウントで解消していきます。フォローして待っていてください。",
]

VOICEVOX_TEXT = [
    "服にしわがあると、ちゃんと写らないんじゃ、と思ったことはありませんか。",
    "実は、そこまで心配しなくて大丈夫です。",
    "検査着に着替えていただいたり、しわが出にくい体勢を、診療放射線技師がご案内しています。",
    "撮影前に、しわが入っていないかを確認してから撮影しています。",
    "事前に確認しているので、安心して検査を受けていただけます。",
    "患者さんご自身が気にしすぎなくても、現場でちゃんと確認しています。",
    "一方でボタンは、素材や位置によって写り込むことがあります。",
    "金属製のボタンなどは、画像に影響することがあるためです。",
    "検査着に着替えていただいたり、外していただくことがあります。",
    "これも、検査をスムーズに進めるための工夫のひとつです。",
    "知らなかった、というかたは、ぜひ保存してくださいね。",
    "ほかの検査の疑問も、このアカウントで解消していきます。フォローして待っていてください。",
]

MIN_DURATIONS = [4.0, 3.2, 5.8, 4.4, 4.0, 4.6, 4.5, 4.0, 4.2, 3.8, 3.4, 5.2]


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
    with urllib.request.urlopen(req, timeout=60) as res:
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
            "[1:a]volume=1.45[voice];[2:a]volume=-24dB[bgm];"
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
        "title": TITLE,
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": VOICE_SPEED,
        "bgm": str(BGM),
        "bgm_volume": "-24 dB",
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
