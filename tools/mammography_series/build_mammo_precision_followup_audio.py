from pathlib import Path
import json
import subprocess
import urllib.parse
import urllib.request
import wave


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "mammography_series" / "mammo_result_notice_v1"
AUDIO_DIR = ASSET_DIR / "audio_precision_followup_20260623"
WORK_DIR = ASSET_DIR / "_audio_work_precision_followup_20260623"
MANIFEST = ASSET_DIR / "audio_manifest_precision_followup_20260623.json"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.20

NARRATION = [
    "マンモの結果に、要精密検査と書いてあったかたへ。",
    "まず、がんが確定したわけではありません。",
    "要精密検査は、もう少し詳しく見ましょう、という案内です。",
    "カテゴリー3は、良性の可能性が比較的高いものの、念のため確認が必要という意味です。",
    "次にやることは一つ。乳腺科、乳腺外科、乳腺外来への受診です。",
    "精密検査では、乳腺エコーなどで、より詳しく確認します。",
    "検診で一度エコーを受けていても、改めて見ることがあります。より丁寧に確認するためです。",
    "通知が来た時に不安になるのは、自然なことです。次の一歩は受診するだけです。",
    "検査前の不安を、安心に変える情報を発信中です。",
    "あとで見返せるように、保存しておいてください。",
]

MIN_DURATIONS = [3.0, 3.0, 3.4, 4.8, 4.0, 3.6, 5.2, 5.0, 3.4, 3.4]


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
    query["speedScale"] = VOICE_SPEED
    query["pitchScale"] = 0.0
    query["intonationScale"] = 0.95
    query["volumeScale"] = 1.0
    query["prePhonemeLength"] = 0.08
    query["postPhonemeLength"] = 0.16
    out.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path):
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def main():
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    for required in [FFMPEG, BGM]:
        if not required.exists():
            raise FileNotFoundError(required)

    padded_wavs = []
    durations = []
    for idx, text in enumerate(NARRATION, start=1):
        voice = AUDIO_DIR / f"voice_{idx:02d}.wav"
        padded = WORK_DIR / f"voice_{idx:02d}_padded.wav"
        synthesize_voice(text, voice)
        duration = max(MIN_DURATIONS[idx - 1], wav_duration(voice) + 0.45)
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

    segments = WORK_DIR / "voice_segments.txt"
    with segments.open("w", encoding="utf-8") as f:
        for wav in padded_wavs:
            f.write(f"file '{wav.as_posix()}'\n")

    voice_all = AUDIO_DIR / "voice.wav"
    bgm_mix = AUDIO_DIR / "voice_with_bgm.m4a"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", segments, "-c", "copy", voice_all])
    run(
        [
            FFMPEG,
            "-y",
            "-i",
            voice_all,
            "-stream_loop",
            "-1",
            "-i",
            BGM,
            "-filter_complex",
            "[0:a]volume=1.45[voice];[1:a]volume=-25dB[bgm];"
            "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=1:normalize=0,"
            "alimiter=limit=0.95[a]",
            "-map",
            "[a]",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            bgm_mix,
        ]
    )

    manifest = {
        "title": "マンモで要精密検査、次に何をする？",
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": f"{VOICE_SPEED:.2f}x",
        "bgm": str(BGM),
        "bgm_volume": "-25 dB",
        "voice_volume": "1.45x",
        "narration": NARRATION,
        "durations_seconds": [round(value, 3) for value in durations],
        "total_seconds": round(sum(durations), 3),
        "segment_files": [str(AUDIO_DIR / f"voice_{idx:02d}.wav") for idx in range(1, len(NARRATION) + 1)],
        "voice_file": str(voice_all),
        "voice_with_bgm_file": str(bgm_mix),
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(bgm_mix)


if __name__ == "__main__":
    main()
