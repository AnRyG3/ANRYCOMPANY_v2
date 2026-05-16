# 投稿フローREADME

## 1. ネタ登録

`database/csv/content_db.csv` に、リール、ブログ、LINEスタンプの元ネタを登録する。

## 2. 投稿管理

`database/csv/post_management.csv` で、媒体、投稿日、テーマ、投稿状態を管理する。

## 3. ステータス管理

`database/csv/post_status.csv` で、制作の進行状況を管理する。

## 4. KPI管理

投稿後は `database/csv/kpi_management.csv` に再生数、保存数、コメント数、フォロー増加を入力する。

## 5. バズ分析

保存率・再生数・フォロー率が高い投稿は `database/csv/buzz_analysis_db.csv` に登録する。

## 6. 横展開

伸びたリールはブログ、YouTube Shorts、画像投稿、LINEスタンプ販促へ展開する。

## ステータス一覧

```text
idea
script
image
voice
editing
scheduled
published
analyzed
repurpose
archived
```

