from __future__ import annotations

import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave
from pathlib import Path


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "ct_series" / "ct_contrast_breastfeeding_v1_images"
FRAME_DIR = ROOT / "reel_assets" / "ct_series" / "ct_contrast_breastfeeding_v1_telop_frames"
AUDIO_DIR = ROOT / "reel_assets" / "ct_series" / "ct_contrast_breastfeeding_v1_audio"
WORK_DIR = ROOT / "reel_assets" / "ct_series" / "ct_contrast_breastfeeding_v1_video_work"
MANIFEST = ROOT / "reel_assets" / "ct_series" / "ct_contrast_breastfeeding_v1_video_manifest.json"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
OUT = ROOT / "reel_assets" / "ct_series" / "造影CTのあと、授乳はどうすればいい？.mp4"
FINAL_OUT = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形" / OUT.name

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
BGM_VOLUME = "-25dB"

# One narration segment maps to exactly one telop frame. Durations come from the
# synthesized WAV files: no artificial still-frame padding or silent gaps.
SEGMENTS = [
    {
        "frame": "01_hook_baby_carrier_telop.png",
        "display": "造影CTのあと / 授乳して大丈夫？",
        "voice": "ぞうえいシーティーのあと、じゅにゅうして大丈夫かな。",
    },
    {
        "frame": "02_question_baby_carrier_telop.png",
        "display": "赤ちゃんのことだから / 気になりますよね",
        "voice": "赤ちゃんのことだから、気になりますよね。",
    },
    {
        "frame": "03_ask_before_leaving_telop.png",
        "display": "迷ったら / 帰る前に確認",
        "voice": "迷ったら、帰る前に担当スタッフへ確認を。",
    },
    {
        "frame": "04_empathy_after_exam_telop.png",
        "display": "慎重になるのは / 自然なことです",
        "voice": "慎重になるのは、自然なことです。",
    },
    {
        "frame": "05_reassuring_explanation_telop.png",
        "display": "多くの場合 / 授乳を続けられます",
        "voice": "特別な理由がなければ、じゅにゅうは続けられるとされています。",
    },
    {
        "frame": "06_calm_ct_room_telop.png",
        "display": "赤ちゃんに届く量は / ごくわずかです",
        "voice": "赤ちゃんの体に取り込まれる量は、ごくわずかです。",
    },
    {
        "frame": "07_ask_staff_telop.png",
        "display": "個別の状況は / 担当スタッフに確認",
        "voice": "個別の状況では、対応が変わることもあります。",
    },
    {
        "frame": "08_leave_reassured_telop.png",
        "display": "自分で時間を / 決めなくて大丈夫",
        "voice": "自分で時間を決めなくて大丈夫です。",
    },
    {
        "frame": "09_save_cta_telop.png",
        "display": "検査日に見返せるよう / 保存",
        "voice": "検査日に見返せるよう、保存してください。",
    },
    {
        "frame": "10_follow_cta_telop.png",
        "display": "次の検査に備えて / フォロー",
        "voice": "次の検査に備えて、フォローしてください。",
    },
]


def run(command: list[Path | str]) -> None:
    subprocess.run([str(item) for item in command], check=True)


def post_json(path: str, params=None, payload=None) -> bytes:
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
    query.update(
        {
            "speedScale": VOICE_SPEED,
            "pitchScale": 0.0,
            "intonationScale": 0.96,
            "pauseLengthScale": 0.32,
            "volumeScale": 1.0,
            "prePhonemeLength": 0.02,
            "postPhonemeLength": 0.04,
        }
    )
    output.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def main() -> None:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_OUT.parent.mkdir(parents=True, exist_ok=True)
    if not FFMPEG.exists() or not BGM.exists():
        raise FileNotFoundError("ffmpeg or BGM is missing")

    frame_paths = [FRAME_DIR / segment["frame"] for segment in SEGMENTS]
    for frame in frame_paths:
        if not frame.exists():
            raise FileNotFoundError(frame)

    voice_paths, durations = [], []
    for index, segment in enumerate(SEGMENTS, start=1):
        voice = AUDIO_DIR / f"voice_{index:02d}.wav"
        synthesize_voice(segment["voice"], voice)
        voice_paths.append(voice)
        durations.append(wav_duration(voice))

    voice_list = WORK_DIR / "voice_segments.txt"
    voice_list.write_text("".join(f"file '{p.as_posix()}'\n" for p in voice_paths), encoding="utf-8")
    voice_all = AUDIO_DIR / "voice.wav"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", voice_list, "-c", "copy", voice_all])

    video_segments = []
    for index, (frame, duration) in enumerate(zip(frame_paths, durations), start=1):
        segment = WORK_DIR / f"segment_{index:02d}.mp4"
        run(
            [
                FFMPEG, "-y", "-loop", "1", "-t", f"{duration:.3f}", "-i", frame,
                "-vf", "scale=1080:1920,format=yuv420p", "-r", "30", "-c:v", "libx264",
                "-tune", "stillimage", "-pix_fmt", "yuv420p", segment,
            ]
        )
        video_segments.append(segment)

    video_list = WORK_DIR / "video_segments.txt"
    video_list.write_text("".join(f"file '{p.as_posix()}'\n" for p in video_segments), encoding="utf-8")
    silent_video = WORK_DIR / "silent.mp4"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", video_list, "-c", "copy", silent_video])
    run(
        [
            FFMPEG, "-y", "-i", silent_video, "-i", voice_all, "-stream_loop", "-1", "-i", BGM,
            "-filter_complex", f"[1:a]volume=1.4[voice];[2:a]volume={BGM_VOLUME}[bgm];"
            "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
            "alimiter=limit=0.95[a]",
            "-map", "0:v", "-map", "[a]", "-shortest", "-c:v", "copy", "-c:a", "aac",
            "-b:a", "192k", "-movflags", "+faststart", OUT,
        ]
    )
    shutil.copy2(OUT, FINAL_OUT)
    MANIFEST.write_text(
        json.dumps(
            {
                "title": "造影CTのあと、授乳はどうすればいい？",
                "speaker": f"VOICEVOX speaker id {SPEAKER}",
                "voice_speed": VOICE_SPEED,
                "transition_silence_seconds": 0.0,
                "voice_text": [s["voice"] for s in SEGMENTS],
                "display_text": [s["display"] for s in SEGMENTS],
                "frames": [str(p) for p in frame_paths],
                "durations_seconds": [round(v, 3) for v in durations],
                "total_seconds": round(sum(durations), 3),
                "voice_audio": str(voice_all),
                "asset_video": str(OUT),
                "final_video": str(FINAL_OUT),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8-sig",
    )
    print(OUT)
    print(FINAL_OUT)
    print(round(sum(durations), 3))


if __name__ == "__main__":
    main()
