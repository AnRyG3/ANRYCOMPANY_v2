# Instagramリール 共通点抽出・学習システム

## 目的

過去に伸びたInstagramリールを分析し、共通点を抽出してDB化する。

「なぜ伸びたか」を、冒頭ワード、尺、テロップ量、改行数、演出、BGMテンポ、コメント誘導、保存誘導、感情カテゴリに分解し、次回投稿の設計に反映する。

## フォルダ構成

```text
reel-learning-system/
├─ 01_raw_posts/
├─ 02_feature_db/
├─ 03_patterns/
├─ 04_reports/
└─ 05_templates/
```

## 分析項目

- 冒頭ワード
- 尺
- テロップ量
- 改行数
- 演出
- BGMテンポ
- コメント誘導
- 保存誘導
- 感情カテゴリ

## 運用手順

1. 伸びたリールを `01_raw_posts/past_reels_raw.csv` に登録する
2. 各投稿の特徴を `02_feature_db/reel_feature_db.csv` に入力する
3. 共通点を `03_patterns/winning_patterns.md` にまとめる
4. 月1回、`04_reports/monthly_learning_report.md` にレポート化する
5. 次回投稿前に `05_templates/reel_learning_checklist.md` で確認する

## 成功判定

以下のどれかを満たす投稿を「伸びた投稿」として登録する。

- 再生数が平均より高い
- 保存率が高い
- コメント率が高い
- フォロー率が高い
- 完視聴率が高い

