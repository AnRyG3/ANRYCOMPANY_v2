from pathlib import Path
import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "mammography_series" / "02_mammo_vs_ultrasound"
BG_DIR = ASSET_DIR / "generated_backgrounds"
FRAME_DIR = ASSET_DIR / "final_text_frames"
WORK_DIR = ASSET_DIR / "_video_work"
AUDIO_DIR = ASSET_DIR / "audio"
CTA = ROOT / "reel_assets" / "common" / "reel_end_card_save.png"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
OUT = ASSET_DIR / "マンモと乳腺エコーどっちがいいの.mp4"
FINAL_OUT = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形" / "マンモと乳腺エコーどっちがいいの.mp4"

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
SIZE = (1080, 1920)

TEXTS = [
    ["マンモと乳腺エコー", "どっちがいいの？"],
    ["実は", "得意なことが違います"],
    ["マンモは", "小さな石灰化を見つけるのが得意"],
    ["エコーは", "しこりの性状を観察するのが得意"],
    ["どちらか一方が", "必ず優れているわけではありません"],
    ["年齢や症状などで", "必要な検査は変わります"],
    ["気になる症状があれば", "まず医療機関へ相談してください"],
    ["迷ったときは", "ひとりで悩まなくて大丈夫"],
    ["検査前の不安を", "安心に変える情報を発信中"],
]

NARRATION = [
    "マンモと乳腺エコー、どっちがいいの。",
    "実は、得意なことが違います。",
    "マンモは、小さな石灰化を見つけるのが得意です。",
    "エコーは、しこりの性状を観察するのが得意です。",
    "どちらか一方が、必ず優れているわけではありません。",
    "年齢や症状などで、必要な検査は変わります。",
    "気になる症状があれば、まず医療機関へ相談してください。",
    "迷ったときは、ひとりで悩まなくて大丈夫。",
    "検査前の不安を、安心に変える情報を発信中。",
    "あとで見返せるように、保存してまた見よう。",
]

BG_FILES = [
    BG_DIR / "01_comparison.png",
    BG_DIR / "01_comparison.png",
    BG_DIR / "02_mammography_calcifications.png",
    BG_DIR / "03_ultrasound_mass.png",
    BG_DIR / "01_comparison.png",
    BG_DIR / "04_consultation.png",
    BG_DIR / "04_consultation.png",
    BG_DIR / "04_consultation.png",
    BG_DIR / "04_consultation.png",
]

FONT_BOLD = [
    r"C:\Windows\Fonts\YuGothB.ttc",
    r"C:\Windows\Fonts\YuGothM.ttc",
    r"C:\Windows\Fonts\meiryob.ttc",
    r"C:\Windows\Fonts\meiryo.ttc",
]


def run(cmd):
    subprocess.run([str(part) for part in cmd], check=True)


def choose_font(size):
    for path in FONT_BOLD:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def cover_image(path):
    im = Image.open(path).convert("RGB")
    scale = max(SIZE[0] / im.width, SIZE[1] / im.height)
    new_size = (round(im.width * scale), round(im.height * scale))
    im = im.resize(new_size, Image.Resampling.LANCZOS)
    left = (im.width - SIZE[0]) // 2
    top = (im.height - SIZE[1]) // 2
    return im.crop((left, top, left + SIZE[0], top + SIZE[1]))


def fit_font(draw, lines, max_width, start_size=86, min_size=48):
    for size in range(start_size, min_size - 1, -2):
        font = choose_font(size)
        widths = [draw.textbbox((0, 0), line, font=font, stroke_width=3)[2] for line in lines]
        if max(widths) <= max_width:
            return font
    return choose_font(min_size)


def draw_center_text(im, lines, index):
    draw = ImageDraw.Draw(im, "RGBA")
    max_width = 940
    y_center = 410 if index in (3, 4) else 490
    start_size = 78 if index in (3, 4, 5, 7) else 86
    line_gap = 22
    font = fit_font(draw, lines, max_width, start_size=start_size)
    bboxes = [draw.textbbox((0, 0), line, font=font, stroke_width=3) for line in lines]
    heights = [box[3] - box[1] for box in bboxes]
    widths = [box[2] - box[0] for box in bboxes]
    total_h = sum(heights) + line_gap * (len(lines) - 1)
    y = y_center - total_h // 2
    text_w = max(widths)
    pad_x, pad_y = 54, 42
    box = (
        (SIZE[0] - text_w) // 2 - pad_x,
        y - pad_y,
        (SIZE[0] + text_w) // 2 + pad_x,
        y + total_h + pad_y,
    )
    shadow = (box[0] + 8, box[1] + 10, box[2] + 8, box[3] + 10)
    draw.rounded_rectangle(shadow, radius=34, fill=(8, 35, 56, 92))
    draw.rounded_rectangle(box, radius=34, fill=(255, 255, 255, 232))
    yy = y
    for line, height, bbox in zip(lines, heights, bboxes):
        x = (SIZE[0] - (bbox[2] - bbox[0])) // 2
        draw.text(
            (x, yy),
            line,
            font=font,
            fill=(18, 58, 88, 255),
            stroke_width=2,
            stroke_fill=(255, 255, 255, 255),
        )
        yy += height + line_gap
    return im


def make_contact_sheet(paths, out_path):
    thumb_w, thumb_h = 270, 480
    label_h = 32
    cols = 5
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (thumb_w * cols, (thumb_h + label_h) * rows), (245, 247, 250))
    font = ImageFont.load_default()
    for idx, path in enumerate(paths):
        im = Image.open(path).convert("RGB")
        im.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), "white")
        tile.paste(im, ((thumb_w - im.width) // 2, 0))
        ImageDraw.Draw(tile).text((8, thumb_h + 9), Path(path).name, fill=(0, 0, 0), font=font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
    sheet.save(out_path)


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
    query["speedScale"] = 1.10
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
    FRAME_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_OUT.parent.mkdir(parents=True, exist_ok=True)
    for required in [*BG_FILES, CTA, FFMPEG, BGM]:
        if not required.exists():
            raise FileNotFoundError(required)

    frames = []
    for idx, (lines, bg_file) in enumerate(zip(TEXTS, BG_FILES), start=1):
        frame = draw_center_text(cover_image(bg_file), lines, idx)
        out = FRAME_DIR / f"frame_{idx:02d}.png"
        frame.save(out)
        frames.append(out)
    cta_out = FRAME_DIR / "frame_10.png"
    shutil.copy2(CTA, cta_out)
    frames.append(cta_out)
    make_contact_sheet(frames, ASSET_DIR / "_contact_sheet_final_text_frames.png")
    make_contact_sheet(sorted(BG_DIR.glob("*.png")), ASSET_DIR / "_contact_sheet_generated_backgrounds.png")

    padded_wavs = []
    durations = []
    for idx, text in enumerate(NARRATION, start=1):
        voice = AUDIO_DIR / f"voice_{idx:02d}.wav"
        padded = WORK_DIR / f"voice_{idx:02d}_padded.wav"
        synthesize_voice(text, voice)
        duration = max(3.0 if idx < 9 else 3.4, wav_duration(voice) + 0.45)
        durations.append(duration)
        run([
            FFMPEG, "-y", "-i", voice, "-af",
            f"apad=pad_dur={duration:.3f},atrim=duration={duration:.3f}",
            "-ar", "44100", "-ac", "2", padded,
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
        FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", frames_txt,
        "-vf", "scale=1080:1920,format=yuv420p", "-r", "30",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", silent,
    ])
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", voice_txt, "-c", "copy", voice_all])
    run([
        FFMPEG, "-y", "-i", silent, "-i", voice_all, "-stream_loop", "-1", "-i", BGM,
        "-filter_complex",
        "[1:a]volume=1.4[voice];[2:a]volume=-21dB[bgm];"
        "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=1:normalize=0,"
        "alimiter=limit=0.95[a]",
        "-map", "0:v", "-map", "[a]", "-shortest", "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k", OUT,
    ])
    shutil.copy2(OUT, FINAL_OUT)

    manifest = {
        "title": "マンモと乳腺エコーどっちがいいの？",
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
