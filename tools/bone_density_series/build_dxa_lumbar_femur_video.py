from pathlib import Path
import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "bone_density_series" / "03_dxa_lumbar_femur_reason"
FRAME_DIR = ASSET_DIR / "final_text_frames"
WORK_DIR = ASSET_DIR / "_video_work"
AUDIO_DIR = ASSET_DIR / "audio"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
OUT = ASSET_DIR / "DXA法って何_なぜ腰と大腿骨で測るの.mp4"
FINAL_OUT = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形" / "DXA法って何_なぜ腰と大腿骨で測るの.mp4"

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20

NARRATION = [
    "骨密度検査で出てくる、DXA法。どんな検査か、短く整理します。",
    "DXA法は、弱いエックス線を使って、骨密度を測る検査です。",
    "よく測られる場所は、腰の骨、腰椎と、足の付け根に近い大腿骨近位部です。",
    "ここが選ばれる理由は、骨折した時に生活への影響が大きい場所だからです。",
    "腰椎は、背骨の骨密度の変化を見やすい場所として使われます。",
    "大腿骨近位部は、転倒後の骨折リスクと関係しやすく、特に大切に見られます。",
    "一方で、健診などでは、かかとの検査が入口として使われることもあります。",
    "結果が気になる時は、自己判断せず、医療機関で確認してください。",
    "数字だけで不安になるより、今の状態を知って、次の行動につなげる検査です。",
    "骨密度検査の前に、見返せるように保存しておいてください。",
]


def run(cmd):
    subprocess.run([str(part) for part in cmd], check=True)


def find_bgm() -> Path:
    candidates = list((ROOT / "01_ショート動画_リール_YouTubeShorts").rglob("healing_wind.mp3"))
    if candidates:
        return candidates[0]
    raise FileNotFoundError("healing_wind.mp3")


def post_json(path, params=None, payload=None):
    query = urllib.parse.urlencode(params or {})
    url = f"{VOICEVOX}{path}"
    if query:
        url += f"?{query}"
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    if body is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.read()


def synthesize_voice(text, out):
    query = json.loads(post_json("/audio_query", {"text": text, "speaker": SPEAKER}))
    query["speedScale"] = 1.20
    query["pitchScale"] = 0.0
    query["intonationScale"] = 1.0
    query["volumeScale"] = 1.0
    query["prePhonemeLength"] = 0.08
    query["postPhonemeLength"] = 0.14
    out.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path):
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def main():
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_OUT.parent.mkdir(parents=True, exist_ok=True)
    bgm = find_bgm()

    frames = [FRAME_DIR / f"frame_{idx:02d}.png" for idx in range(1, 11)]
    for required in [*frames, FFMPEG, bgm]:
        if not required.exists():
            raise FileNotFoundError(required)

    voice_files = []
    for idx, text in enumerate(NARRATION, start=1):
        voice = AUDIO_DIR / f"voice_{idx:02d}.wav"
        synthesize_voice(text, voice)
        voice_files.append(voice)

    padded_wavs = []
    durations = []
    for frame_idx, voice in enumerate(voice_files, start=1):
        padded = WORK_DIR / f"voice_frame_{frame_idx:02d}_padded.wav"
        min_duration = 3.0
        if frame_idx in {4, 6, 9, 10}:
            min_duration = 3.4
        duration = max(min_duration, wav_duration(voice) + 0.45)
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
        for frame, duration in zip(frames, durations):
            f.write(f"file '{frame.as_posix()}'\n")
            f.write(f"duration {duration:.3f}\n")
        f.write(f"file '{frames[-1].as_posix()}'\n")

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
        bgm,
        "-filter_complex",
        "[1:a]volume=1.4[voice];[2:a]volume=-22dB[bgm];"
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
    shutil.copy2(OUT, FINAL_OUT)

    manifest = {
        "title": "DXA法って何？なぜ腰と大腿骨で測るの？",
        "speaker": "VOICEVOX speaker id 20",
        "bgm": str(bgm),
        "bgm_volume": "-22 dB",
        "durations_seconds": [round(value, 3) for value in durations],
        "total_seconds": round(sum(durations), 3),
        "asset_video": str(OUT),
        "final_video": str(FINAL_OUT),
    }
    (ASSET_DIR / "video_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(FINAL_OUT)


if __name__ == "__main__":
    main()
