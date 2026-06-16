from pathlib import Path
import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "ct_series" / "ct_mri_need_mri_v1"
FRAME_DIR = ASSET_DIR / "telop_frames"
WORK_DIR = ASSET_DIR / "_video_work"
AUDIO_DIR = ASSET_DIR / "audio"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
OUT = ASSET_DIR / "ct_mri_need_mri_v1.mp4"
FINAL_OUT = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形" / "CTを撮ったのに、なぜMRIも必要なの.mp4"

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20

NARRATION = [
    "CTを撮ったのに、またMRI？と思ったことはありませんか。",
    "そう思うのは、とても自然なことです。",
    "実は、CTとMRIは、見えやすいものが違う検査です。",
    "CTは、骨、肺、臓器の形を、全体として素早く確認するのが得意です。",
    "造影剤を使うと、血管の状態を詳しく見ることもあります。",
    "MRIは、神経や腱、婦人科の臓器、目立ちにくい骨折などを細かく確認したいときに使われます。",
    "つまり、CTでまず全体を確認して、",
    "気になる場所を、MRIでさらに詳しく見ることがあるんです。",
    "両方の検査が必要と言われると、不安になりますよね。",
    "理由が気になるときは、担当の医師や診療放射線技師に聞いて大丈夫です。",
    "検査前の不安を、安心に変える情報を発信中。",
    "あとで見返せるように、保存しておいてください。",
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
    query["speedScale"] = 1.2
    query["pitchScale"] = 0.0
    query["intonationScale"] = 0.95
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

    frames = [
        FRAME_DIR / "01_ct_mri_intro_telop.png",
        FRAME_DIR / "02_question_corridor_patient_telop.png",
        FRAME_DIR / "03_ct_mri_difference_telop.png",
        FRAME_DIR / "04_ct_room_telop.png",
        FRAME_DIR / "05_contrast_ct_telop.png",
        FRAME_DIR / "06_mri_room_telop.png",
        FRAME_DIR / "07_ct_overview_telop.png",
        FRAME_DIR / "08_mri_detail_telop.png",
        FRAME_DIR / "09_waiting_anxiety_patient_telop.png",
        FRAME_DIR / "10_consultation_patient_rttech_telop.png",
        FRAME_DIR / "11_fixed_message_telop.png",
        FRAME_DIR / "12_save_cta.png",
    ]
    for required in [*frames, FFMPEG, BGM]:
        if not required.exists():
            raise FileNotFoundError(required)

    padded_wavs = []
    durations = []
    for idx, text in enumerate(NARRATION, start=1):
        voice = AUDIO_DIR / f"voice_{idx:02d}.wav"
        padded = WORK_DIR / f"voice_{idx:02d}_padded.wav"
        synthesize_voice(text, voice)
        min_duration = 2.5
        if idx in {4, 6, 10}:
            min_duration = 3.3
        if idx in {11, 12}:
            min_duration = 3.0
        duration = max(min_duration, wav_duration(voice) + 0.38)
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
        BGM,
        "-filter_complex",
        "[1:a]volume=1.45[voice];[2:a]volume=-22dB[bgm];"
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
        "title": "CTを撮ったのに、なぜMRIも必要なの？",
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "speedScale": 1.2,
        "bgm": str(BGM),
        "bgm_volume": "-22 dB",
        "narration": NARRATION,
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
