from __future__ import annotations

import json
import re
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave
from pathlib import Path


ROOT = Path(r"F:\ANRYCAMPANY")
TEL0P_DIR = ROOT / "reel_assets" / "pre_exam_series" / "12_barium_laxative_return_telop"
ASSET_DIR = ROOT / "reel_assets" / "pre_exam_series" / "12_barium_laxative_return_production"
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_video_work"
VIDEO_DIR = ASSET_DIR / "video"
FINAL_DIR = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形"
MANIFEST = ASSET_DIR / "video_manifest.json"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
OUT = VIDEO_DIR / "バリウム検査_帰りの電車で下剤がいつ効くか不安なとき_20260914.mp4"
FINAL_OUT = FINAL_DIR / OUT.name

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
BGM_VOLUME = "-27dB"
TAIL_SECONDS = 0.18
MIN_DURATION = 2.4

FRAMES = [
    "telop_01_hook_station_concourse.png",
    "telop_02_station_gate.png",
    "telop_03_toilet_check.png",
    "telop_04_facility_guidance.png",
    "telop_05_timing_varies.png",
    "telop_06_call_facility.png",
    "telop_07_normalize_anxiety.png",
    "telop_08_save_cta.png",
    "telop_09_follow_cta.png",
]

DISPLAY_NARRATION = [
    "バリウム検査のあとに下剤を飲んだけど、帰りの電車で効いてきたらどうしよう。そう思うこと、ありますよね。",
    "バリウム検査のあと、電車で帰るときは、気になってしまうこともあります。",
    "乗る前に、駅や乗り換え先のお手洗いを確認しておくと、少し安心です。",
    "下剤の飲み方やタイミングは、施設ごとに案内が異なります。",
    "効き始めるまでの時間にも、個人差があります。",
    "心配なときは、帰る前に検査を受けた施設へ確認して大丈夫です。",
    "不安に思うこと自体は、おかしいことではありません。",
    "バリウム検査の前日に見返せるよう、この投稿を保存しておいてください。",
    "検査前後の小さな迷いに答える発信を続けています。フォローして、次回も見てください。",
]

# Kana substitutions are used only for reliable speech synthesis; display telops stay unchanged.
VOICE_TEXT = [
    "バリウム検査のあとに下剤を飲んだけど、帰りの電車で効いてきたらどうしよう。そう思うこと、ありますよね。",
    "バリウム検査のあと、電車で帰るときは、気になってしまうこともあります。",
    "乗る前に、駅や乗り換え先のお手洗いを確認しておくと、少し安心です。",
    "下剤の飲み方やタイミングは、施設ごとに案内が異なります。",
    "効き始めるまでの時間にも、個人差があります。",
    "心配なときは、帰る前に検査を受けた施設へ確認して大丈夫です。",
    "不安に思うこと自体は、おかしいことではありません。",
    "バリウム検査の前日に見返せるよう、この投稿を保存しておいてください。",
    "検査前後の小さな迷いに答える発信を続けています。フォローして、次回も見てください。",
]


def run(command: list[Path | str]) -> None:
    subprocess.run([str(part) for part in command], check=True)


def post_json(path: str, params: dict | None = None, payload: dict | None = None) -> bytes:
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
    query.update({"speedScale": VOICE_SPEED, "pitchScale": 0.0, "intonationScale": 0.95, "volumeScale": 1.0, "prePhonemeLength": 0.05, "postPhonemeLength": 0.10})
    output.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def media_duration(path: Path) -> float:
    result = subprocess.run([str(FFMPEG), "-i", str(path)], capture_output=True)
    stderr = result.stderr.decode("utf-8", errors="ignore")
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", stderr)
    if not match:
        raise RuntimeError(f"Could not read duration for {path}")
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def concat_list(paths: list[Path], destination: Path) -> None:
    destination.write_text("".join(f"file '{path.as_posix()}'\n" for path in paths), encoding="utf-8")


def main() -> None:
    for directory in [AUDIO_DIR, WORK_DIR, VIDEO_DIR, FINAL_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

    frame_paths = [TEL0P_DIR / name for name in FRAMES]
    for required in [FFMPEG, BGM, *frame_paths]:
        if not required.exists():
            raise FileNotFoundError(required)

    padded_wavs: list[Path] = []
    voice_durations: list[float] = []
    cut_durations: list[float] = []
    for index, text in enumerate(VOICE_TEXT, start=1):
        voice = AUDIO_DIR / f"voice_{index:02d}.wav"
        padded = WORK_DIR / f"voice_{index:02d}_padded.wav"
        synthesize_voice(text, voice)
        voice_duration = wav_duration(voice)
        cut_duration = max(MIN_DURATION, voice_duration + TAIL_SECONDS)
        run([FFMPEG, "-y", "-i", voice, "-af", f"apad=pad_dur={cut_duration:.3f},atrim=duration={cut_duration:.3f}", "-ar", "44100", "-ac", "2", padded])
        voice_durations.append(voice_duration)
        cut_durations.append(cut_duration)
        padded_wavs.append(padded)

    segments: list[Path] = []
    for index, (frame, duration) in enumerate(zip(frame_paths, cut_durations), start=1):
        segment = WORK_DIR / f"segment_{index:02d}.mp4"
        run([FFMPEG, "-y", "-loop", "1", "-t", f"{duration:.3f}", "-i", frame, "-vf", "scale=1080:1920,format=yuv420p", "-r", "30", "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p", segment])
        segments.append(segment)

    voice_txt, segments_txt = WORK_DIR / "voice_segments.txt", WORK_DIR / "video_segments.txt"
    concat_list(padded_wavs, voice_txt)
    concat_list(segments, segments_txt)
    voice_all, silent_video = AUDIO_DIR / "voice_all.wav", WORK_DIR / "silent_video.mp4"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", voice_txt, "-c", "copy", voice_all])
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", segments_txt, "-c", "copy", silent_video])
    run([FFMPEG, "-y", "-i", silent_video, "-i", voice_all, "-stream_loop", "-1", "-i", BGM, "-filter_complex", f"[1:a]volume=1.45[voice];[2:a]volume={BGM_VOLUME}[bgm];[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,alimiter=limit=0.95[a]", "-map", "0:v", "-map", "[a]", "-shortest", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT])
    shutil.copy2(OUT, FINAL_OUT)

    qa = {
        "video_duration_seconds": round(media_duration(OUT), 3),
        "audio_duration_seconds": round(media_duration(voice_all), 3),
        "voice_to_frame_mapping": "one narration segment per matching telop frame",
        "duration_strategy": "each frame ends 0.18 seconds after its matching speech; no long silent gap inserted",
    }
    manifest = {
        "title": "健診の帰り道、下剤がいつ効くか不安なときは",
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": VOICE_SPEED,
        "bgm": str(BGM),
        "bgm_volume": BGM_VOLUME,
        "tail_seconds_per_cut": TAIL_SECONDS,
        "frames": [str(path) for path in frame_paths],
        "display_narration": DISPLAY_NARRATION,
        "voice_text": VOICE_TEXT,
        "voice_durations_seconds": [round(value, 3) for value in voice_durations],
        "cut_durations_seconds": [round(value, 3) for value in cut_durations],
        "voice_audio": str(voice_all),
        "asset_video": str(OUT),
        "final_video": str(FINAL_OUT),
        "qa": qa,
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8-sig")
    print(OUT)
    print(FINAL_OUT)
    print(json.dumps(qa, ensure_ascii=False))


if __name__ == "__main__":
    main()
