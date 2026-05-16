# SNS運営OS

## 目的

Instagramリール、ブログ、LINEスタンプ運用を一元管理するためのSNS運営OS。

投稿ネタ管理、投稿予約管理、投稿済み管理、保存率分析、バズ構成DB参照、ハッシュタグ自動提案、リールからブログへの横展開、LINEスタンプ販促導線、n8n自動化接続までを1つの管理構造にまとめる。

## フォルダ構成

```text
SNS-OS/
├─ content/
│  ├─ reels/
│  ├─ blog/
│  └─ line-stamps/
├─ analytics/
│  ├─ kpi/
│  └─ buzz/
├─ automation/
│  └─ n8n/
├─ database/
│  ├─ csv/
│  └─ json/
├─ posting/
│  ├─ scheduled/
│  └─ published/
└─ dashboard/
   └─ manual/
```

## 基本運用

1. `database/csv/content_db.csv` にネタを登録する
2. `database/csv/post_management.csv` で投稿予定日と媒体を決める
3. `database/csv/post_status.csv` で進行状況を管理する
4. 投稿後、`database/csv/kpi_management.csv` に数値を入れる
5. 伸びた投稿は `database/csv/buzz_analysis_db.csv` に成功パターンとして登録する
6. n8n連携は `automation/n8n/n8n_connection_config.json` を参照する

## 投稿フロー

```text
ネタ登録
↓
台本・記事・スタンプ案作成
↓
画像・音声・サムネ作成
↓
投稿予約
↓
投稿済み管理
↓
KPI入力
↓
保存率・バズ分析
↓
次回ネタへ横展開
```

## 横展開ルール

リールで伸びたテーマは、ブログ化、画像投稿化、LINEスタンプ販促導線へ展開する。

例:

```text
リール: CTが怖い人へ
ブログ: CT被ばくは危険？放射線技師が解説
画像投稿: CT前に知っておく3つ
LINEスタンプ導線: あんりぃの「だいじょうぶ」系スタンプ紹介
```

