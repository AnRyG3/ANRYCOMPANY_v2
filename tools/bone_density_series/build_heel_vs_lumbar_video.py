from pathlib import Path
import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "bone_density_series" / "02_heel_vs_lumbar"
FRAME_DIR = ASSET_DIR / "final_text_frames"
WORK_DIR = ASSET_DIR / "_video_work"
AUDIO_DIR = ASSET_DIR / "audio"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "healing_wind.mp3"
OUT = ASSET_DIR / "骨密度検査かかとで測るの腰で測るの.mp4"
FINAL_OUT = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形" / "骨密度検査かかとで測るの腰で測るの.mp4"

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20

NARRATION = [
    "こつみつど検査は、かかとで測るの？腰で測るの？",
    "どこで測るかは、検査の目的で変わります。",
    "健診では、かかとで測る検査を見ることがあります。",
    "かかとは、音波で、骨の状態の目安を見ます。",
    "詳しく調べる時は、腰や、足のつけ根を測ることがあります。",
    "ここは、骨折すると、生活に影響が大きい場所です。",
    "できさほうでは、弱いエックス線を使って、こつみつどを測ります。",
    "かかとは、骨の健康に気づく入口。",
    "腰や足のつけ根は、より詳しく見る検査。",
    "どちらが正解ではなく、役割が違います。",
    "結果が気になる時は、医療機関で確認してください。",
    "検査前の不安を、安心に変える情報を発信中。",
    "こつみつど検査の前に、見返せるように保存してください。",
]

FRAME_TO_NARRATION = [
    [0],
    [1],
    [2],
    [3],
    [4],
    [5],
    [6],
    [7],
    [8],
    [9, 10],
    [11],
    [12],
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

    frames = [FRAME_DIR / f"frame_{idx:02d}.png" for idx in range(1, 13)]
    for required in [*frames, FFMPEG, BGM]:
        if not required.exists():
            raise FileNotFoundError(required)

    voice_files = []
    for idx, text in enumerate(NARRATION, start=1):
        voice = AUDIO_DIR / f"voice_{idx:02d}.wav"
        synthesize_voice(text, voice)
        voice_files.append(voice)

    padded_wavs = []
    durations = []
    for frame_idx, narration_indices in enumerate(FRAME_TO_NARRATION, start=1):
        segment_files = [voice_files[i] for i in narration_indices]
        if len(segment_files) == 1:
            segment = segment_files[0]
        else:
            list_file = WORK_DIR / f"frame_{frame_idx:02d}_voice_list.txt"
            with list_file.open("w", encoding="utf-8") as f:
                for wav in segment_files:
                    f.write(f"file '{wav.as_posix()}'\n")
            segment = WORK_DIR / f"frame_{frame_idx:02d}_voice.wav"
            run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", segment])

        padded = WORK_DIR / f"voice_frame_{frame_idx:02d}_padded.wav"
        min_duration = 2.6
        if frame_idx in {5, 6, 7, 10, 11, 12}:
            min_duration = 3.1
        duration = max(min_duration, wav_duration(segment) + 0.45)
        durations.append(duration)
        run([
            FFMPEG,
            "-y",
            "-i",
            segment,
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
        BGM,
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
        "title": "骨密度検査、かかとで測るの？ 腰で測るの？",
        "speaker": "VOICEVOX speaker id 20",
        "pronunciation_note": "骨密度 is read as こつみつど; DXA法 is read as できさほう",
        "bgm": str(BGM),
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
