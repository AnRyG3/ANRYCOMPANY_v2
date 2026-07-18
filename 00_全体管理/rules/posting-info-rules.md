# ANRYCAMPANY Posting Info Rules

Use this file when creating or updating posting notes.

- Use Japanese text.
- Match nearby posting notes when readable.
- Keep descriptions calm and practical.
- End with a save/check CTA when suitable.
- Do not include `#ANRYCAMPANY` in hashtags.
- Keep hashtags to only the necessary tags. Default to 6-8 tags, and do not exceed 10 unless the user explicitly asks.
- Choose hashtags from: main exam/topic, patient concern, clinical category, audience intent, and `#診療放射線技師`. Avoid broad filler or duplicate-meaning tags.
- When a final video is approved with phrases such as "動画OK", "これでOK", or "採用", present posting title, description, and hashtags in chat unless it is unclear whether the approval is for the official final file.

## Required Fields

```markdown
# {video_title}

## 公開情報

- 公開予約: YYYY-MM-DD HH:MM
- YouTube Shorts: {url}
- 状態: 公開予約済み

## 投稿タイトル

{posting_title}

## 動画タイトル

{video_title}

## 説明文

{description}

## ハッシュタグ

#{tag1} #{tag2} ...

## 素材

- 完成動画: `{absolute_final_video_path}`
- 素材フォルダ: `{absolute_asset_folder}`

## メモ

- シリーズ名または本数
- 最終構成: {image_count}枚、{duration}秒
- 音声読み: {important_readings}
- 修正履歴で重要なもの
```
