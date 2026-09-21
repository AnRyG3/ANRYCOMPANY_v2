from __future__ import annotations

import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave
from pathlib import Path


ROOT = Path(r"F:\ANRYCAMPANY")
FRAME_DIR = ROOT / "reel_assets" / "ct_series" / "ct_contrast_dominant_arm_v1_telop_frames"
AUDIO_DIR = ROOT / "reel_assets" / "ct_series" / "ct_contrast_dominant_arm_v1_audio"
WORK_DIR = ROOT / "reel_assets" / "ct_series" / "ct_contrast_dominant_arm_v1_video_work"
ASSET_OUT = ROOT / "reel_assets" / "ct_series" / "造影CTの注射、利き腕でも大丈夫？.mp4"
FINAL_OUT = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形" / ASSET_OUT.name
MANIFEST = ROOT / "reel_assets" / "ct_series" / "ct_contrast_dominant_arm_v1_video_manifest.json"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
BGM_VOLUME = "-25dB"


# Every visual frame has exactly one spoken segment. The video uses the WAV's
# measured duration directly, with no added still-frame padding or silent gap.
SEGMENTS = [
    {"frame": "scene_01_hook_patient_thought_telop.png", "voice": "ききうでに、注射しても、大丈夫かな。"},
    {"frame": "scene_02_action_tell_nurse_telop.png", "voice": "気になるときは、注射の前に、反対の腕はできますか、と伝えて大丈夫です。"},
    {"frame": "scene_03_ct_preparation_telop.png", "voice": "ぞうえいシーティーでは、検査に必要な速さで、ぞうえい剤を注入します。"},
    {"frame": "scene_04_check_arm_telop.png", "voice": "そのため、けっかんの状態や、検査内容を確認して、注射する腕を決めます。"},
    {"frame": "scene_05_reassured_patient_telop.png", "voice": "ききうでだから、必ず避けるわけではありません。"},
    {"frame": "scene_06_share_preference_telop.png", "voice": "きぼうを伝えることは、わがままではありません。"},
    {"frame": "scene_07_staff_explains_telop.png", "voice": "けっかんの状態などによっては、きぼうにそえないこともあります。理由をスタッフに確認して大丈夫です。"},
    {"frame": "scene_08_ready_for_ct_telop.png", "voice": "理由がわかると、安心して検査に進めます。"},
    {"frame": "scene_09_save_cta_home_telop.png", "voice": "検査前日に見返せるよう、保存しておいてください。次の投稿も、フォローしてご覧ください。"},
]


def run(command: list[Path | str]) -> None:
    subprocess.run([str(item) for item in command], check=True)


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
    query.update({
        "speedScale": VOICE_SPEED,
        "pitchScale": 0.0,
        "intonationScale": 0.96,
        "pauseLengthScale": 0.32,
        "prePhonemeLength": 0.02,
        "postPhonemeLength": 0.04,
        "volumeScale": 1.0,
    })
    output.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def concat_list(paths: list[Path], output: Path) -> None:
    output.write_text("".join(f"file '{path.as_posix()}'\n" for path in paths), encoding="utf-8")


def main() -> None:
    if not FFMPEG.exists() or not BGM.exists():
        raise FileNotFoundError("ffmpeg or BGM is missing")
    frames = [FRAME_DIR / item["frame"] for item in SEGMENTS]
    missing = [str(path) for path in frames if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing telop frames: " + ", ".join(missing))

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_OUT.parent.mkdir(parents=True, exist_ok=True)

    voice_paths, durations = [], []
    for index, segment in enumerate(SEGMENTS, start=1):
        voice_path = AUDIO_DIR / f"voice_{index:02d}.wav"
        synthesize_voice(segment["voice"], voice_path)
        voice_paths.append(voice_path)
        durations.append(wav_duration(voice_path))

    voice_list = WORK_DIR / "voice_segments.txt"
    concat_list(voice_paths, voice_list)
    voice_all = AUDIO_DIR / "voice.wav"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", voice_list, "-c", "copy", voice_all])

    video_segments = []
    for index, (frame, duration) in enumerate(zip(frames, durations), start=1):
        segment = WORK_DIR / f"segment_{index:02d}.mp4"
        run([
            FFMPEG, "-y", "-loop", "1", "-t", f"{duration:.3f}", "-i", frame,
            "-vf", "scale=1080:1920,format=yuv420p", "-r", "30", "-c:v", "libx264",
            "-tune", "stillimage", "-pix_fmt", "yuv420p", segment,
        ])
        video_segments.append(segment)

    video_list = WORK_DIR / "video_segments.txt"
    concat_list(video_segments, video_list)
    silent_video = WORK_DIR / "silent.mp4"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", video_list, "-c", "copy", silent_video])
    run([
        FFMPEG, "-y", "-i", silent_video, "-i", voice_all, "-stream_loop", "-1", "-i", BGM,
        "-filter_complex", f"[1:a]volume=1.4[voice];[2:a]volume={BGM_VOLUME}[bgm];"
        "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,alimiter=limit=0.95[a]",
        "-map", "0:v", "-map", "[a]", "-shortest", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", ASSET_OUT,
    ])
    shutil.copy2(ASSET_OUT, FINAL_OUT)

    MANIFEST.write_text(json.dumps({
        "title": "造影CTの注射、利き腕でも大丈夫？",
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": VOICE_SPEED,
        "transition_silence_seconds": 0.0,
        "voice_text": [item["voice"] for item in SEGMENTS],
        "frames": [str(path) for path in frames],
        "durations_seconds": [round(value, 3) for value in durations],
        "total_seconds": round(sum(durations), 3),
        "voice_audio": str(voice_all),
        "asset_video": str(ASSET_OUT),
        "final_video": str(FINAL_OUT),
    }, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(ASSET_OUT)
    print(FINAL_OUT)
    print(round(sum(durations), 3))


if __name__ == "__main__":
    main()
