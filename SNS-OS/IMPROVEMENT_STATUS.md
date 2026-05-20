# 改善状況

## 2026-05-21 対応済み

| 優先度 | 項目 | 対応 |
|---|---|---|
| 高 | content配下が空 | `content/reels`、`content/blog`、`content/line-stamps` に既存制作物への実体リンク付き管理カードを追加 |
| 高 | メトリクスCSVがほぼ空 | `instagram_metrics.csv`、`youtube_metrics.csv`、`kpi_management.csv`、`past_reels_raw.csv` に既存学習データを転記 |
| 高 | GitHubバックアップ未完了 | origin設定は確認済み。未追跡ファイルが多いため、push前にステージ対象の確認が必要 |
| 中 | n8n稼働不明 | プロセス確認ではn8n稼働を確認できず。`automation/n8n/RUN_STATUS.md` に結果を記録 |
| 中 | posting/publishedが空 | `posting/published/published_posts.csv` に投稿済み5件を追加 |
| 低 | Python混在 | `ENVIRONMENT.md` にPython 3.12推奨とキャッシュ運用ルールを明記 |

## 次にやると良いこと

1. GitHubへバックアップする前に、今回追加したSNS-OS関連ファイルだけをステージする
2. n8nを起動し、manual trigger workflowをimportして手動実行する
3. 投稿後24時間、72時間、7日後のKPIを `kpi_management.csv` に追記する
4. `__pycache__` は必要になったタイミングで削除する
