# Metricool MCP n8n接続手順

## 重要

Metricoolの無料プランでは、n8nのHeader Authに必要なAPI Keyは発行されない。

この手順は、MetricoolをAdvancedまたはCustomプランへ変更した場合のみ使用する。

## 目的

Metricoolに接続済みのInstagramとYouTubeから、分析班が週次指標を取得する。

## 接続済みSNS

- Instagram: `rt.education.ch`
- YouTube: 診療放射線技師の安心ラボ

## n8nの設定

先にMetricoolの契約プランを確認する。AdvancedまたはCustomの場合のみ、`metricool_mcp_check` の手順で接続テストを行う。

1. n8nで新しいワークフローを作る。
2. `AI Agent` ノードを追加する。
3. `AI Agent` のツールに `MCP Client Tool` を追加する。
4. Endpointに次を入力する。

```text
https://ai.metricool.com/mcp
```

5. Authenticationで `Header Auth` を選ぶ。
6. Credentialを新規作成する。
7. Nameに次を入力する。

```text
X-Mc-Auth
```

8. ValueにMetricoolのアカウント設定画面で確認したAPI Keyを入力する。
9. Credentialを保存する。

## セキュリティ

- API KeyはこのチャットやObsidianへ貼り付けない。
- API Keyはn8nのCredentialだけに保存する。
- Metricool MCPには分析値の閲覧だけでなく、投稿作成や公開などの操作権限もある。
- 初期運用では分析取得のみを実行する。

## 最初の取得テスト

次の内容で取得できるか確認する。

```text
接続中のブランド一覧を表示してください。
診療放射線技師の安心ラボについて、InstagramとYouTubeの接続状態を表示してください。
直近7日間のInstagramリールとYouTube Shortsの分析値を取得してください。
投稿は作成、編集、公開しないでください。
```

## 成功後

1. 毎週月曜日に、前週月曜日から日曜日までの分析値を取得する。
2. CSVまたはJSONで分析フォルダへ保存する。
3. YouTubeとInstagramの比較Excelを作成する。
4. Obsidianへ対策メモを記録する。
