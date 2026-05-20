# 実行環境メモ

## Python

このSNS-OSでは、Python実行系は原則として1系統に統一する。

- 推奨: Python 3.12
- 理由: 安定版として依存ライブラリとの相性を優先するため
- 対象: `SNS-OS/automation/ai-sns-pipeline/`

## 運用ルール

1. `python --version` を確認してからパイプラインを実行する
2. 3.14など別バージョンで実行した後は、必要に応じて `__pycache__` を削除してから再実行する
3. `__pycache__` は `.gitignore` 対象なので、GitHubには上げない
4. n8nから実行する場合も、同じPython実行ファイルを指定する

## 現状メモ

`__pycache__` は以下に存在する。

- `SNS-OS/automation/ai-sns-pipeline/__pycache__/`
- `SNS-OS/automation/ai-sns-pipeline/modules/__pycache__/`

キャッシュは成果物ではないため、必要なら削除してよい。
