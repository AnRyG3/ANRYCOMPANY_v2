# ARCHITECTURE

## SNS-OS全体構成

```text
SNS-OS/
├─ content/
├─ analytics/
├─ automation/
├─ database/
├─ posting/
├─ dashboard/
├─ knowledge/
├─ AGENTS.md
├─ ARCHITECTURE.md
└─ AI_RULES.md
```

## データの流れ

```text
ネタ入力
↓
AI採点
↓
台本生成
↓
画像生成
↓
動画生成
↓
投稿管理
↓
数値回収
↓
学習
↓
改善提案
```

## 主要ディレクトリ

| ディレクトリ | 役割 |
|---|---|
| `content/` | リール、ブログ、LINEスタンプ素材 |
| `analytics/` | KPI、保存率、バズ分析、学習ループ |
| `automation/` | n8n、Pythonパイプライン、自動化設定 |
| `database/` | CSV、JSON、投稿管理DB |
| `posting/` | 投稿予約、投稿済み管理 |
| `dashboard/` | 初心者マニュアル、運用画面用資料 |
| `knowledge/` | 勝ちフック、バズ構成、維持率パターン |

## 中核ファイル

| ファイル | 役割 |
|---|---|
| `workflow.md` | SNS-OS基本ワークフロー |
| `theme_to_post_flow.md` | テーマ起点の投稿生成フロー |
| `database/csv/content_db.csv` | コンテンツDB |
| `database/csv/post_management.csv` | 投稿管理 |
| `database/csv/kpi_management.csv` | KPI管理 |
| `automation/ai-sns-pipeline/pipeline_manager.py` | Pythonパイプライン |
| `analytics/learning-loop/learning_loop.py` | 投稿結果の学習ループ |
| `analytics/scoring-system/score_engine.py` | 投稿前スコアリング |

## 設計思想

- CSVを人間が編集しやすい管理DBにする
- JSONをAIとn8nが読みやすい設定DBにする
- Pythonは分析と自動生成の実行エンジンにする
- n8nは外部サービス接続のハブにする
- knowledgeは勝ちパターンの長期記憶として扱う

