from pathlib import Path
import json
import subprocess
import urllib.parse
import urllib.request
import wave


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "result_wait_series" / "05_scan_choice"
FRAME_DIR = ASSET_DIR / "final_text_frames"
WORK_DIR = ASSET_DIR / "_video_work"
AUDIO_DIR = ASSET_DIR / "audio"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
OUT = ASSET_DIR / "再検査_CT_MRI_エコーどれになるの.mp4"
FINAL_OUT = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形" / "再検査　CT・MRI・エコーどれになるの.mp4"

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20

NARRATION = [
    "再検査と言われたら、次はどの検査？",
    "シーティー？ エムアールアイ？ エコー？ 不安になりますよね。",
    "でも、悪い結果だから、とは限りません。",
    "もう少し詳しく見るために、検査を追加することがあります。",
    "シーティーは、体の中を断面で、広く確認。",
    "エムアールアイは、磁石と電波で、詳しく確認。",
    "エコーは、音を使って、動きや状態を確認。",
    "医師が、一番見やすい方法を、選んでいます。",
    "検査前の不安を、安心に変える情報を、発信中。",
    "不安になった時に見返せるように、保存してください。",
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


def calm_sentence_ending(query, keep_question=False):
    if keep_question or not query["accent_phrases"]:
        return query
    phrase = query["accent_phrases"][-1]
    voiced = [mora for mora in phrase["moras"] if mora["pitch"] > 0]
    for offset, mora in enumerate(voiced[-2:]):
        mora["pitch"] -= 0.16 + (0.10 * offset)
    return query


def synthesize_voice(text, out, keep_question=False):
    query = json.loads(post_json("/audio_query", {"text": text, "speaker": SPEAKER}))
    query["speedScale"] = 1.10
    query["pitchScale"] = 0.0
    query["intonationScale"] = 0.95
    query["volumeScale"] = 1.0
    query["prePhonemeLength"] = 0.08
    query["postPhonemeLength"] = 0.14
    calm_sentence_ending(query, keep_question=keep_question)
    out.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path):
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def main():
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_OUT.parent.mkdir(parents=True, exist_ok=True)

    frames = [FRAME_DIR / f"frame_{i:02d}.png" for i in range(1, 11)]
    missing = [str(path) for path in frames if not path.exists()]
    if missing:
        raise FileNotFoundError("\n".join(missing))
    if not BGM.exists():
        raise FileNotFoundError(BGM)

    padded_wavs = []
    durations = []
    for idx, text in enumerate(NARRATION, start=1):
        voice = AUDIO_DIR / f"voice_{idx:02d}.wav"
        padded = WORK_DIR / f"voice_{idx:02d}_padded.wav"
        synthesize_voice(text, voice, keep_question=(idx == 1))
        voice_duration = wav_duration(voice)
        min_duration = 3.0 if idx <= 8 else 3.5
        duration = max(min_duration, voice_duration + 0.45)
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
        "[1:a]volume=1.4[voice];[2:a]volume=-21dB[bgm];"
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
    FINAL_OUT.write_bytes(OUT.read_bytes())

    manifest = {
        "title": "再検査と言われたら、CT・MRI・エコーどれになるの？",
        "speaker": "VOICEVOX もち子さん normal style id 20",
        "bgm": str(BGM),
        "bgm_volume": "-21 dB",
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
