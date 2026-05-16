# AGENTS

## 目的

SNS-OS内で動くAIエージェントの役割を定義する。

## Agent一覧

| Agent | 役割 | 主な参照先 |
|---|---|---|
| Idea Agent | ネタ収集、テーマ生成、シリーズ化 | `database/csv/content_db.csv`, `knowledge/` |
| Scoring Agent | 投稿前スコアリング、危険表現確認 | `analytics/scoring-system/` |
| Script Agent | リール台本、Shorts台本、TikTok台本作成 | `content/reels/` |
| Visual Agent | 画像プロンプト、サムネ案、構図提案 | `content/`, `knowledge/` |
| Posting Agent | 投稿予約、投稿済み管理 | `posting/` |
| Analytics Agent | KPI記録、保存率分析、投稿ランキング | `analytics/` |
| Learning Agent | 勝ちパターン抽出、再学習、改善提案 | `analytics/learning-loop/`, `knowledge/` |
| Blog Agent | リールからブログへ横展開 | `content/blog/` |
| Stamp Agent | LINEスタンプ企画、販促導線 | `content/line-stamps/` |

## 基本ルール

- 各AgentはCSVとJSONを正本として扱う
- 投稿前に必ずScoring Agentを通す
- 投稿後はAnalytics AgentでKPIを記録する
- 伸びた投稿はLearning Agentが `knowledge/` へ反映する
- 医療不安を煽る表現は避ける
- 最終的に安心感で終わる構成を優先する

