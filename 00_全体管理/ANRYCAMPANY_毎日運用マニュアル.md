# ANRYCAMPANY 毎日運用マニュアル

ANRYCAMPANYは、動画を作るだけではなく、投稿後の数字を見て次の動画を良くすることで回る。
このファイルは、専門知識がなくても毎回同じ流れで運用するための入口。

## まず見る場所

毎回ここから始める。

1. `00_全体管理/Codex_最初に読む.md`
2. `SNS-OS/database/csv/post_management.csv`
3. `SNS-OS/database/csv/kpi_management.csv`
4. `SNS-OS/database/csv/buzz_analysis_db.csv`
5. `SNS-OS/dashboard/manual/今日の運用チェック.md`

## 毎日の流れ

### 1. 今日やることを決める

見るファイル:

- `00_全体管理/今日やること.md`
- `SNS-OS/database/csv/post_management.csv`

決めること:

- 今日作る動画
- 今日投稿する動画
- 今日数字を見る投稿

Codexへの依頼例:

```text
今日ANRYCAMPANYでやるべきことを、投稿管理表と直近の流れを見て3つに絞ってください。
```

### 2. 投稿したら記録する

見るファイル:

- `SNS-OS/posting/published/published_posts.csv`
- `SNS-OS/database/csv/post_management.csv`

記録すること:

- 投稿した日
- 投稿先
- タイトル
- テーマ
- 投稿URLがあればURL
- 状態を `published` にする

Codexへの依頼例:

```text
この動画を今日Instagramに投稿しました。SNS-OSの投稿済み管理に追加してください。
タイトルは「〇〇」です。
```

### 3. 投稿後の数字を入れる

見るファイル:

- `SNS-OS/database/csv/kpi_management.csv`
- `SNS-OS/analytics/instagram_metrics.csv`
- `SNS-OS/analytics/youtube_metrics.csv`
- `SNS-OS/analytics/tiktok_metrics.csv`

見るタイミング:

- 投稿後24時間
- 投稿後72時間
- 投稿後7日

最低限入れる数字:

- 再生数
- リーチ
- いいね数
- 保存数
- コメント数
- シェア数
- フォロー増加
- 完視聴率

Codexへの依頼例:

```text
この投稿の数字を分析表に入れてください。
再生数は〇〇、保存数は〇〇、コメント数は〇〇、フォロー増加は〇〇です。
```

### 4. 伸びた理由を残す

見るファイル:

- `SNS-OS/database/csv/buzz_analysis_db.csv`
- `SNS-OS/analytics/reel-learning-system/03_patterns/winning_patterns.md`

判断の目安:

- 保存率が高い
- コメント率が高い
- フォロー率が高い
- 同じテーマの平均より再生数が高い
- 視聴者の不安や疑問に強く刺さっている

Codexへの依頼例:

```text
この投稿が伸びた理由を分析して、勝ちパターンDBに追加してください。
次に使い回せる構成も提案してください。
```

### 5. 次の動画に反映する

見るファイル:

- `SNS-OS/database/csv/content_db.csv`
- `SNS-OS/knowledge/winning_hooks.json`
- `SNS-OS/knowledge/viral_patterns.json`
- `SNS-OS/knowledge/retention_patterns.json`

Codexへの依頼例:

```text
直近の分析結果を見て、次に作るべきショート動画を1本だけ提案してください。
過去に伸びた型を使ってください。
```

## 週1回の流れ

週に1回、次の4つだけ決める。

1. 伸びた動画
2. 伸びなかった動画
3. 次も使う型
4. やめる型

Codexへの依頼例:

```text
今週の投稿管理表とKPIを見て、ANRYCAMPANYの週次レビューを作ってください。
来週作る動画テーマも3つ出してください。
```

## 今の問題点

現在は、フォルダと表はある。
ただし、運用が毎回ここに戻ってくる形になっていない。

つまり問題は「知識がないこと」ではなく、次の流れが固定されていないこと。

```text
作る
↓
投稿する
↓
数字を入れる
↓
理由を残す
↓
次の動画に反映する
```

この5つを毎回やれば、ANRYCAMPANYは会社のように回り始める。

