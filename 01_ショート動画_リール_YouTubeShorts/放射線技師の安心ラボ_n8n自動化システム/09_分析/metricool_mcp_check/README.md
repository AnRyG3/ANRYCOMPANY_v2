# Metricool MCP 接続確認

Metricool MCPへ接続できるか、AI Agentを使う前に確認する。

## 利用条件

このn8n向け確認方法はMetricoolのAPI Keyを使用するため、AdvancedまたはCustomプランが必要。

無料プランでは実行しない。

## 手順

1. Metricoolのアカウント設定でAPI Keyを確認する。
2. `open_env.cmd` を開く。
3. `METRICOOL_API_KEY=` の右側へAPI Keyを貼り付けて保存する。
4. `run_check.cmd` を開く。

成功した場合は `Metricool MCP 接続: 成功` と表示される。

## セキュリティ

- API Keyはチャット、Obsidian、READMEへ貼り付けない。
- `.env` はGit管理対象外。
- API KeyはMetricool MCPに強い操作権限を与えるため、共有しない。
