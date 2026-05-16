# Instagramリール 学習ループシステム

## 目的

投稿結果をAIが学習し、次回投稿へ反映するための分析システム。

投稿後の再生数、保存率、コメント率、フォロー率などを記録し、バズ判定、共通点抽出、失敗分析、次回改善提案、投稿ランキング、勝ちパターンDB化を行う。

## 機能

- 投稿データ保存
- 再生数記録
- 保存率記録
- コメント率記録
- バズ判定
- 共通点抽出
- 失敗分析
- 次回改善提案
- 投稿ランキング
- 勝ちパターンDB

## ファイル構成

```text
learning-loop/
├─ README.md
├─ learning_loop.py
├─ csv/
│  └─ post_results.csv
├─ db/
│  ├─ db_schema.md
│  └─ winning_pattern_db.csv
├─ rules/
│  └─ learning_rules.json
├─ docs/
│  └─ 初心者向け解説.md
└─ reports/
   └─ latest_learning_report.md
```

## 使い方

1. `csv/post_results.csv` に投稿結果を入力する
2. `learning_loop.py` を実行する
3. `reports/latest_learning_report.md` に分析結果が出る
4. バズ判定された投稿は `db/winning_pattern_db.csv` に保存される

## 学習ループ

```text
投稿
↓
数値記録
↓
ランキング
↓
勝ちパターン抽出
↓
失敗分析
↓
次回改善提案
↓
次回投稿へ反映
```

