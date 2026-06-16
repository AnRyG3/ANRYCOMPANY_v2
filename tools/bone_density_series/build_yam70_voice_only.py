from pathlib import Path
import json
import subprocess
import urllib.parse
import urllib.request
import wave


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "bone_density_series" / "06_yam70_meaning"
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_audio_work"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20

DISPLAY_NARRATION = [
    "骨密度（こつみつど）の検査結果、数字を見て不安になっていませんか？",
    "「YAM（やむち）70%」って書いてあるけど、これって大丈夫なの…？",
    "大丈夫です。その数字、ちゃんと意味があります。",
    "YAM（やむち）とは「若年成人平均値」のこと。20〜44歳の骨密度（こつみつど）を100%とした比較です。",
    "80%以上は正常。70〜80%は骨量（こつりょう）減少。70%未満は骨粗しょう症（こつそしょうしょう）。",
    "70%という数字は「骨粗しょう症（こつそしょうしょう）の境界ライン」です。",
    "でも、数字だけで全てが決まるわけではありません。年齢・体型・生活習慣も含めて医師が総合判断します。",
    "結果を見て焦（あせ）る気持ち、おかしくないです。でも数字の意味を知ると、少し落ち着きませんか？",
    "結果に「要精密検査」や「骨粗しょう症（こつそしょうしょう）」と書いてあった方（かた）は、整形外科への受診をおすすめします。",
    "検査を受けたあなたの行動は、正解です。",
    "この動画、あとで見返せるように保存しておいてください。",
    "骨密度（こつみつど）シリーズは続きます。フォローして待っていてください。",
]

VOICEVOX_TEXT = [
    "こつみつどの検査結果、数字を見て不安になっていませんか。",
    "やむち、70パーセントって書いてあるけど、これって大丈夫なの。そう感じるかたもいます。",
    "大丈夫です。その数字には、ちゃんと意味があります。",
    "やむちとは、若年成人平均値のこと。20歳から44歳のこつみつどを100パーセントとした比較です。",
    "80パーセント以上は正常。70から80パーセントは、こつりょう減少。70パーセント未満は、こつそしょうしょうとされます。",
    "70パーセントという数字は、こつそしょうしょうの境界ラインです。",
    "でも、数字だけで全てが決まるわけではありません。年齢、体型、生活習慣も含めて、医師が総合判断します。",
    "結果を見てあせる気持ち、おかしくないです。でも数字の意味を知ると、少し落ち着きませんか。",
    "結果に、要精密検査や、こつそしょうしょうと書いてあった、かたは、整形外科への受診をおすすめします。",
    "検査を受けたあなたの行動は、正解です。",
    "この動画、あとで見返せるように保存しておいてください。",
    "こつみつどシリーズは続きます。フォローして待っていてください。",
]

MIN_DURATIONS = [3.1, 4.1, 2.8, 4.6, 6.0, 3.6, 5.8, 4.6, 4.8, 3.2, 3.5, 3.8]


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
    query["intonationScale"] = 0.95
    query["volumeScale"] = 1.0
    query["prePhonemeLength"] = 0.08
    query["postPhonemeLength"] = 0.14
    out.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path):
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def main():
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    if not FFMPEG.exists():
        raise FileNotFoundError(FFMPEG)

    padded_wavs = []
    durations = []
    for idx, text in enumerate(VOICEVOX_TEXT, start=1):
        voice = AUDIO_DIR / f"voice_{idx:02d}.wav"
        padded = WORK_DIR / f"voice_{idx:02d}_padded.wav"
        synthesize_voice(text, voice)
        duration = max(MIN_DURATIONS[idx - 1], wav_duration(voice) + 0.42)
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

    voice_txt = WORK_DIR / "voice_segments.txt"
    with voice_txt.open("w", encoding="utf-8") as f:
        for wav in padded_wavs:
            f.write(f"file '{wav.as_posix()}'\n")

    combined = AUDIO_DIR / "voice.wav"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", voice_txt, "-c", "copy", combined])

    script_path = ASSET_DIR / "voicevox_script.md"
    script_path.write_text(
        "# VOICEVOX読み上げ用\n\n"
        + "\n".join(f"{idx}. {text}" for idx, text in enumerate(VOICEVOX_TEXT, start=1))
        + "\n",
        encoding="utf-8",
    )

    manifest = {
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": "1.20x",
        "display_narration": DISPLAY_NARRATION,
        "voicevox_text": VOICEVOX_TEXT,
        "durations_seconds": [round(value, 3) for value in durations],
        "total_seconds": round(sum(durations), 3),
        "segments": [str(AUDIO_DIR / f"voice_{idx:02d}.wav") for idx in range(1, 13)],
        "combined_voice": str(combined),
    }
    (ASSET_DIR / "audio_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(combined)


if __name__ == "__main__":
    main()
