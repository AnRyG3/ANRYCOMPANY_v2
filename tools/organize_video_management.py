from pathlib import Path


ROOT = Path(r"F:\ANRYCAMPANY")
COMPLETE_DIR = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形"
POST_DIR = ROOT / "ANRYCAMPANY" / "投稿情報"
OUT = ROOT / "ANRYCAMPANY" / "01_動画管理.md"


SCHEDULED = [
    {
        "date": "2026-06-15 19:00",
        "platform": "YouTube Shorts",
        "title": "CTを撮ったのに、なぜMRIも必要なの？",
        "series": "CT・MRI",
        "url": "https://youtube.com/shorts/c-YhHFPccVw?feature=share",
        "video": "01_ショート動画_リール_YouTubeShorts/インスタ完成形/CTを撮ったのに、なぜMRIも必要なの.mp4",
        "note": "SNS-OS/content/reels/2026-06-15_ct_mri_need_mri.md",
    },
    {
        "date": "2026-06-16 19:00",
        "platform": "YouTube Shorts",
        "title": "乳がん検診、何歳から受ければいいの？",
        "series": "マンモグラフィー",
        "url": "https://youtube.com/shorts/suG27BPKF9g?feature=share",
        "video": "01_ショート動画_リール_YouTubeShorts/インスタ完成形/乳がん検診_何歳から受ければいいの.mp4",
        "note": "ANRYCAMPANY/投稿情報/2026-06-16_乳がん検診_何歳から受ければいいの.md",
    },
]


def series_for(name: str) -> str:
    if any(key in name for key in ["乳がん", "マンモ", "高濃度乳房", "乳腺"]):
        return "マンモグラフィー"
    if any(key in name for key in ["骨密度", "DXA", "かかと"]):
        return "骨密度"
    if any(key in name for key in ["CT", "MRI", "造影"]):
        return "CT・MRI"
    if "エコー" in name:
        return "エコー"
    if any(key in name for key in ["検査前", "検査後", "再検査", "検査結果"]):
        return "検査前後・結果"
    if any(key in name for key in ["放射線", "レントゲン", "温泉", "湿布", "西日本"]):
        return "放射線・レントゲン"
    return "その他"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def build() -> str:
    completed = sorted(
        COMPLETE_DIR.glob("*.mp4"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    post_notes = sorted(POST_DIR.glob("20*.md"), key=lambda path: path.name)

    lines: list[str] = []
    lines.append("# 動画管理")
    lines.append("")
    lines.append("最終更新: 2026-06-12")
    lines.append("")
    lines.append("このメモは、ANRYCAMPANYの動画制作・予約・投稿情報を毎回確認するための入口です。")
    lines.append(
        "完成動画は `F:\\ANRYCAMPANY\\01_ショート動画_リール_YouTubeShorts\\インスタ完成形`、"
        "投稿情報は `F:\\ANRYCAMPANY\\ANRYCAMPANY\\投稿情報` を基準にします。"
    )
    lines.append("")
    lines.append("## まず見る表")
    lines.append("")
    lines.append("| 公開予定 | 状態 | 投稿先 | シリーズ | 動画タイトル | URL |")
    lines.append("|---|---|---|---|---|---|")
    for item in SCHEDULED:
        lines.append(
            f"| {item['date']} | 予約済み | {item['platform']} | {item['series']} | "
            f"{item['title']} | {item['url']} |"
        )
    lines.append("")
    lines.append("## 予約済み")
    lines.append("")
    lines.append("| 公開予定 | 投稿先 | タイトル | 完成動画 | 投稿情報 |")
    lines.append("|---|---|---|---|---|")
    for item in SCHEDULED:
        lines.append(
            f"| {item['date']} | {item['platform']} | {item['title']} | "
            f"`{item['video']}` | `{item['note']}` |"
        )
    lines.append("")
    lines.append("## 投稿情報つき動画")
    lines.append("")
    lines.append("| 日付 | 状態 | タイトル | Obsidian投稿情報 |")
    lines.append("|---|---|---|---|")
    for note in post_notes:
        stem = note.stem
        date = stem[:10]
        title = stem[11:] if len(stem) > 11 else stem
        status = "投稿情報あり"
        if date <= "2026-06-13":
            status = "投稿済み/要確認"
        if date == "2026-06-16":
            status = "予約済み"
        lines.append(f"| {date} | {status} | {title} | [[投稿情報/{stem}]] |")
    lines.append("")
    lines.append("## 完成動画一覧")
    lines.append("")
    lines.append(f"完成動画数: {len(completed)}")
    lines.append("")
    lines.append("| 系列 | ファイル名 | 保存場所 |")
    lines.append("|---|---|---|")
    for movie in completed:
        lines.append(f"| {series_for(movie.stem)} | {movie.name} | `{rel(movie)}` |")
    lines.append("")
    lines.append("## 制作・管理メモ")
    lines.append("")
    lines.append("- 新しく完成した動画は、まずこのメモの「まず見る表」か「投稿情報つき動画」に追加する。")
    lines.append("- 公開予約が完了したら「予約済み」に日時、URL、完成動画パス、投稿情報メモを入れる。")
    lines.append(
        "- YouTube Shorts予約は `SNS-OS/posting/scheduled/scheduled_posts.csv`、"
        "`SNS-OS/database/csv/post_management.csv`、"
        "`SNS-OS/database/csv/post_status.csv` にも反映する。"
    )
    lines.append("- Obsidian投稿情報は `ANRYCAMPANY/投稿情報` に1本1ファイルで残す。")
    lines.append("- 医療・検査系の表記では、新規文に必ず「診療放射線技師」を使う。")
    lines.append("")
    lines.append("## 次に整理したいこと")
    lines.append("")
    lines.append("- 過去動画の投稿済みURLを確認し、完成動画一覧にURL列を追加する。")
    lines.append("- InstagramとYouTube Shortsのどちらに投稿済みかを分ける。")
    lines.append("- 投稿後KPI入力済みかどうかを、週次分析CSVとつなげる。")
    return "\n".join(lines) + "\n"


def main() -> None:
    OUT.write_text(build(), encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
