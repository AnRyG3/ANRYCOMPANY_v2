# n8n Manual Trigger 基本パイプライン

## フロー

```text
Manual Trigger
↓
Read CSV / Google Sheets
↓
Run Command または Execute Command
↓
Write CSV / Google Sheets
↓
通知
```

## 目的

SNS-OSのAIパイプラインを、まず手動実行で安全にテストする。

完全自動化の前に、CSV読み込み、Python実行、結果保存、通知までを確認する。

## n8nノード構成

### 1. Manual Trigger

手動でワークフローを開始する。

用途:

- 初回テスト
- 投稿前チェック
- ネタ生成の手動実行

### 2. Read CSV / Google Sheets

読み込む候補:

```text
SNS-OS/database/csv/content_db.csv
SNS-OS/automation/ai-sns-pipeline/data/ideas.csv
SNS-OS/automation/ai-sns-pipeline/data/kpi_management.csv
```

Google Sheetsで管理する場合は、同じ列名でシートを作る。

### 3. Run Command / Execute Command

実行するPython:

```powershell
SNS-OS/automation/ai-sns-pipeline/pipeline_manager.py
```

または学習ループ:

```powershell
SNS-OS/analytics/learning-loop/learning_loop.py
```

Pythonの実行例:

```powershell
python SNS-OS/automation/ai-sns-pipeline/pipeline_manager.py
```

`python` が通らない場合は、Python実行ファイルのフルパスを使う。

### 4. Write CSV / Google Sheets

出力先:

```text
SNS-OS/automation/ai-sns-pipeline/outputs/latest_pipeline_report.md
SNS-OS/automation/ai-sns-pipeline/data/buzz_db.csv
SNS-OS/analytics/learning-loop/reports/latest_learning_report.md
SNS-OS/analytics/learning-loop/db/winning_pattern_db.csv
```

Google Sheetsへ書き戻す場合:

- 投稿スコア
- 改善提案
- バズ判定
- 次回テーマ
- 勝ちパターン

### 5. 通知

通知内容:

```text
AI SNSパイプラインが完了しました。
レポート: latest_pipeline_report.md
勝ちパターンDB: buzz_db.csv
```

通知先候補:

- Gmail
- Slack
- Discord
- LINE Notify代替
- Notion

## 最初のテスト手順

1. Manual Triggerを置く
2. Execute Commandで `pipeline_manager.py` を実行する
3. 成功したら `latest_pipeline_report.md` を確認する
4. 次にGoogle Sheets読み込みを追加する
5. 最後に通知を追加する

## エラー時の確認

- Pythonのパスが通っているか
- n8nがローカルファイルにアクセスできるか
- CSVの列名が変わっていないか
- OneDrive同期中でファイルがロックされていないか
- 実行権限があるか

