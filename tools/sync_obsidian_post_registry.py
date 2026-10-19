"""Obsidian の投稿情報ノートを予約一覧へ同期し、登録漏れを検証する。"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(r"F:\ANRYCAMPANY")
VAULT = ROOT / "ANRYCAMPANY"
POST_DIR = VAULT / "投稿情報"
POST_INDEX = POST_DIR / "投稿情報_一覧.md"
VIDEO_MANAGEMENT = VAULT / "01_動画管理.md"


def read_text(path: Path) -> tuple[str, str]:
    raw = path.read_bytes()
    newline = "\r\n" if b"\r\n" in raw else "\n"
    return raw.decode("utf-8-sig"), newline


def write_text(path: Path, text: str) -> None:
    path.write_bytes(text.encode("utf-8"))


def frontmatter_value(note: str, key: str) -> str:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.+?)\s*$", note)
    if not match:
        raise ValueError(f"投稿情報ノートに {key} がありません")
    return match.group(1).strip()


def title_from_note(note: str) -> str:
    match = re.search(r"(?m)^#\s+(.+?)\s*$", note)
    if not match:
        raise ValueError("投稿情報ノートにタイトル見出しがありません")
    return match.group(1).strip()


def upsert_table_row(text: str, heading: str, row: str, key: str, newline: str) -> str:
    start = text.find(heading)
    if start < 0:
        raise ValueError(f"{heading} が見つかりません")
    next_heading = text.find(newline + "## ", start + len(heading))
    end = len(text) if next_heading < 0 else next_heading
    section = text[start:end]
    lines = section.splitlines(keepends=True)
    matches = [i for i, line in enumerate(lines) if key in line]
    if len(matches) > 1:
        raise ValueError(f"{heading} に同じ投稿が複数あります")
    if matches:
        lines[matches[0]] = row + newline
    else:
        separator = next(
            (i for i, line in enumerate(lines) if re.match(r"^\|\s*-{3,}", line)),
            None,
        )
        if separator is None:
            raise ValueError(f"{heading} の表区切りが見つかりません")
        lines.insert(separator + 1, row + newline)
    return text[:start] + "".join(lines) + text[end:]


def count(text: str, value: str) -> int:
    return text.count(value)


def sync(note_name: str, series: str, video_path: str) -> None:
    note_path = POST_DIR / note_name
    if note_path.suffix != ".md":
        note_path = note_path.with_suffix(".md")
    if not note_path.exists():
        raise FileNotFoundError(note_path)

    note, _ = read_text(note_path)
    title = title_from_note(note)
    publish_at = frontmatter_value(note, "publish_at")
    youtube_url = frontmatter_value(note, "youtube_shorts")
    status = frontmatter_value(note, "status")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", publish_at):
        raise ValueError("publish_at は YYYY-MM-DD HH:MM 形式にしてください")
    if not youtube_url.startswith("https://youtube.com/shorts/"):
        raise ValueError("youtube_shorts が YouTube Shorts URL ではありません")

    stem = note_path.stem
    note_link = f"[[{stem}]]"
    vault_link = f"[[投稿情報/{stem}]]"
    post_date = publish_at[:10]

    index, index_newline = read_text(POST_INDEX)
    index_row = f"| {post_date} | {status} | {title} | {note_link} |"
    index = upsert_table_row(index, "## 投稿日順（新しい順）", index_row, note_link, index_newline)

    management, management_newline = read_text(VIDEO_MANAGEMENT)
    overview_row = f"| {publish_at} | {status} | YouTube Shorts | {series} | {title} | {youtube_url} |"
    scheduled_row = f"| {publish_at} | YouTube Shorts | {title} | `{video_path}` | `{note_path.relative_to(ROOT).as_posix()}` |"
    note_row = f"| {post_date} | {status} | {title} | {vault_link} |"
    management = upsert_table_row(management, "## まず見る表", overview_row, youtube_url, management_newline)
    management = upsert_table_row(management, "## 予約済み", scheduled_row, str(note_path.relative_to(ROOT).as_posix()), management_newline)
    management = upsert_table_row(management, "## 投稿情報つき動画", note_row, vault_link, management_newline)

    if count(index, note_link) != 1:
        raise ValueError("投稿情報一覧の同期検証に失敗しました")
    for required in (youtube_url, str(note_path.relative_to(ROOT).as_posix()), vault_link):
        if count(management, required) != 1:
            raise ValueError(f"動画管理の同期検証に失敗しました: {required}")

    write_text(POST_INDEX, index)
    write_text(VIDEO_MANAGEMENT, management)
    print(f"同期済み: {note_path}")
    print(f"公開予約済み: {publish_at}")
    print(f"YouTube Shorts: {youtube_url}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--note", required=True, help="投稿情報フォルダ内のノート名")
    parser.add_argument("--series", required=True)
    parser.add_argument("--video", required=True, help="F:\\ANRYCAMPANY からの相対パス")
    args = parser.parse_args()
    sync(args.note, args.series, args.video)


if __name__ == "__main__":
    main()
