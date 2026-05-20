# n8n稼働確認

## 2026-05-21 確認結果

- workflowファイル: あり
- 接続設定: `SNS-OS/automation/n8n/n8n_connection_config.json`
- 稼働プロセス: n8nは確認できず
- 確認時に見えたNode系プロセス: `node_repl` のみ

## 判断

この状態では「n8n設定ファイルはあるが、n8n本体が稼働しているとは確認できない」。
自動化は、n8n起動、ワークフローimport、手動トリガー実行、出力ファイル更新確認までを次のチェック項目にする。

## 次の確認項目

1. n8nを起動する
2. `manual_trigger_pipeline.json` をimportする
3. 手動実行で `automation/ai-sns-pipeline/outputs/latest_pipeline_report.md` が更新されるか確認する
4. 成功したらこのファイルの稼働状態を `running` に更新する
