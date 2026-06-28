from pathlib import Path
import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "ct_series" / "ct_contrast_kidney_function_v1"
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
OUT = ASSET_DIR / "腎機能が低下していると造影剤は使えないの.mp4"
FINAL_OUT = (
    ROOT
    / "01_ショート動画_リール_YouTubeShorts"
    / "インスタ完成形"
    / "腎機能が低下していると造影剤は使えないの.mp4"
)

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
BGM_VOLUME = "-24dB"

NARRATION = [
    "腎臓が悪いから、造影剤は使えないかもしれない。そう言われて、不安になっていませんか。",
    "検査ができないのか、自分の体はそんなに悪いのか。心配になるのは、おかしくありません。",
    "実は、腎機能が低下していても、造影剤を使える場合があります。使う前に、腎機能をきちんと確認しているからです。",
    "造影剤は、使用後に腎臓でこし取られ、尿として体の外に出ていきます。腎機能が低下していると、この排泄に時間がかかることがあります。",
    "そのため、検査の前に血液検査で腎機能を確認します。このすうちをもとに、医師が、使えるかどうか、どのくらいの量にするかを判断します。",
    "腎機能が低下しているかたには、必要に応じて、造影剤の量を調整したり、水分補給などの対策をとることがあります。",
    "近年は、CT装置や画像処理の進歩により、必要最小限の造影剤量を検討しやすくなっています。",
    "腎機能が著しく低下している場合は、造影剤の使用が難しいと判断されることがあります。その場合も、別の検査方法を検討することができます。",
    "透析を受けているかたは、腎臓から造影剤が排泄されにくい状態ですが、造影CTを受けられているケースもあります。その後の対応は、担当の医師が状態に合わせて判断します。",
    "腎機能が低下しているから、何もできない、ではなく、あなたの状態に合った方法を、チームで考えている、ということです。不安なことは、遠慮なく担当のスタッフに聞いてみてください。",
    "この投稿が参考になったら、保存しておくと後で見返せます。",
    "ほかにも検査の不安を解消する投稿をしています。フォローして、次の投稿も受け取ってください。",
]

FRAMES = [
    "s01_waiting_room_anxiety_telop.png",
    "s02_concerned_closeup_telop.png",
    "s03_rt_tech_ct_room_telop.png",
    "s04_water_kidney_model_telop.png",
    "s05_doctor_lab_result_explanation_telop.png",
    "s06_iv_hydration_support_telop.png",
    "s07_modern_ct_scanner_telop.png",
    "s08_doctor_reviewing_chart_telop.png",
    "s09_dialysis_patient_telop.png",
    "s10_team_support_corridor_telop.png",
    "s11_cta_save_smartphone_telop.png",
    "s12_cta_follow_home_phone_telop.png",
]


def run(cmd):
    subprocess.run([str(part) for part in cmd], check=True)


def post_json(path, params=None, payload=None):
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


def synthesize_voice(text: str, out: Path):
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


def min_duration_for(index: int) -> float:
    if index in {4, 5, 8, 9, 10}:
        return 6.0
    if index in {3, 6, 7, 12}:
        return 4.8
    return 3.8


def main():
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_OUT.parent.mkdir(parents=True, exist_ok=True)

    frames = [FRAME_DIR / name for name in FRAMES]
    for required in [FFMPEG, BGM, *frames]:
        if not required.exists():
            raise FileNotFoundError(required)

    padded_wavs = []
    durations = []
    for idx, text in enumerate(NARRATION, start=1):
        voice = AUDIO_DIR / f"voice_{idx:02d}.wav"
        padded = WORK_DIR / f"voice_{idx:02d}_padded.wav"
        synthesize_voice(text, voice)
        duration = max(min_duration_for(idx), wav_duration(voice) + 0.45)
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
        for frame, duration in zip(frames, durations):
            f.write(f"file '{frame.as_posix()}'\n")
            f.write(f"duration {duration:.3f}\n")
        f.write(f"file '{frames[-1].as_posix()}'\n")

    voice_txt = WORK_DIR / "voice_segments.txt"
    with voice_txt.open("w", encoding="utf-8") as f:
        for wav in padded_wavs:
            f.write(f"file '{wav.as_posix()}'\n")

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
        "title": "腎機能が低下していると、造影剤は使えないの？",
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": VOICE_SPEED,
        "bgm": str(BGM),
        "bgm_volume": BGM_VOLUME,
        "frames": [str(path) for path in frames],
        "narration": NARRATION,
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
