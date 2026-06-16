from pathlib import Path
import json
import subprocess
import urllib.parse
import urllib.request
import wave


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "bone_density_series" / "07_bone_density_screening_age"
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_audio_work"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20

DISPLAY_NARRATION = [
    "骨（こつ）密度検査って、いつから受ければいいの？\nそう思ったこと、ありませんか？",
    "まだ若いから大丈夫。\nそう思っているうちに、骨（ほね）は静かに変化しています。",
    "大丈夫です。\n受けるタイミングを知っておくだけで、安心につながります。",
    "女性は40代から意識を。\n閉経後は、骨（こつ）密度が下がりやすくなります。",
    "65歳以上の女性、70歳以上の男性は、症状がなくても骨（こつ）密度検査がすすめられることがあります。",
    "年齢に関係なく、こんな方（かた）は相談を。",
    "骨折したことがある方（かた）、閉経した方（かた）、身長が縮んできた方（かた）も、相談のきっかけになります。",
    "骨（こつ）粗しょう症は、痛みがないまま進むことがあります。\n気づいたときには骨折していた、ということもあります。",
    "まだ早い、はありません。\n知っておくことが、自分の骨（ほね）を守る第一歩です。",
    "この動画を見たあなたは、もう受けるタイミングを知っています。",
    "検査前の不安を、安心に変える情報を発信中。",
    "あとで確認できるように、保存してください。",
]

VOICEVOX_TEXT = [
    "こつみつど検査って、いつから受ければいいの。そう思ったこと、ありませんか。",
    "まだ若いから大丈夫。そう思っているうちに、ほねは静かに変化しています。",
    "大丈夫です。受けるタイミングを知っておくだけで、安心につながります。",
    "女性は、よんじゅうだいから意識を。へいけい後は、こつみつどが下がりやすくなります。",
    "ろくじゅうごさい以上の女性、ななじゅっさい以上の男性は、症状がなくても、こつみつど検査がすすめられることがあります。",
    "年齢に関係なく、こんなかたは相談を。",
    "骨折したことがあるかた、へいけいしたかた、身長が縮んできたかたも、相談のきっかけになります。",
    "こつそしょうしょうは、痛みがないまま進むことがあります。気づいたときには骨折していた、ということもあります。",
    "まだ早い、はありません。知っておくことが、自分のほねを守る第一歩です。",
    "この動画を見たあなたは、もう受けるタイミングを知っています。",
    "検査前の不安を、安心に変える情報を発信ちゅう。",
    "あとで確認できるように、保存してください。",
]

# Keep each audio segment aligned with the 12 still frames.
MIN_DURATIONS = [4.2, 4.5, 4.2, 4.5, 6.3, 3.2, 5.2, 5.8, 4.8, 3.8, 3.8, 3.4]


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
        "## 表示用ナレーション\n\n"
        + "\n\n".join(f"{idx}. {text}" for idx, text in enumerate(DISPLAY_NARRATION, start=1))
        + "\n\n## VOICEVOX入力文\n\n"
        + "\n\n".join(f"{idx}. {text}" for idx, text in enumerate(VOICEVOX_TEXT, start=1))
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
