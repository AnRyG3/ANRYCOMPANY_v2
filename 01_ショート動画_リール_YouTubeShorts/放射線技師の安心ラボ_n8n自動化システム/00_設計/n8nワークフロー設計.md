# n8nワークフロー設計

## 1. ネタ生成フロー

### 入力

テーマ

### 処理

```mermaid
flowchart LR
    A["Manual Trigger / Webhook"] --> B["Set: テーマ入力"]
    B --> C["OpenAI ChatGPT API"]
    C --> D["Parse JSON"]
    D --> E["Google Sheets: ネタ管理へ保存"]
    D --> F["Google Drive: 台本txt保存"]
    E --> G["Notion: ネタDBへ保存"]
```

### ChatGPT出力

- タイトル
- フック
- 台本
- 保存誘導
- コメント誘導
- サムネ案
- ハッシュタグ候補

## 2. リール制作自動化

### 半自動化するもの

- 台本生成
- 画像プロンプト生成
- 音声台本生成
- ハッシュタグ生成
- 説明文生成
- サムネ案生成

### ワークフロー

```mermaid
flowchart TD
    A["Google Sheets: 状態=未作成"] --> B["ChatGPT: 台本生成"]
    B --> C["ChatGPT/Gemini: 画像プロンプト生成"]
    B --> D["ChatGPT: 音声台本生成"]
    B --> E["ChatGPT: ハッシュタグ生成"]
    B --> F["ChatGPT: 説明文生成"]
    B --> G["ChatGPT: サムネ案生成"]
    C --> H["Google Drive: prompt.txt保存"]
    D --> I["Google Drive: voice_script.txt保存"]
    E --> J["Google Sheets: hashtags更新"]
    F --> K["Google Sheets: caption更新"]
    G --> L["Google Sheets: thumbnail更新"]
```

## 3. ブログ制作自動化

### 入力

撮影法名

### 出力

- ブログ下書き
- SEO
- 見出し
- 内部リンク案
- 画像挿入位置
- Google Docs保存

### ワークフロー

```mermaid
flowchart LR
    A["入力: 撮影法名"] --> B["ChatGPT: 記事構成"]
    B --> C["Claude or ChatGPT: 長文下書き"]
    C --> D["ChatGPT: SEO生成"]
    D --> E["Google Docs: 下書き保存"]
    E --> F["Google Sheets: ブログ管理更新"]
    F --> G["Notion: ブログ一覧保存"]
```

## 4. LINEスタンプ管理自動化

### 入力

テーマ

### 出力

- 40個文言
- 画像プロンプト
- タイトル
- 説明文
- 審査チェック

### ワークフロー

```mermaid
flowchart LR
    A["入力: スタンプテーマ"] --> B["ChatGPT: 40個文言生成"]
    B --> C["Gemini: 画像プロンプト生成"]
    B --> D["ChatGPT: タイトル・説明文生成"]
    D --> E["ChatGPT: 審査チェック生成"]
    E --> F["Google Sheets: LINE管理更新"]
    C --> G["Google Drive: prompt保存"]
```

## 5. 投稿分析自動化

### 自動記録

- 再生数
- 保存数
- コメント数
- フォロー増加
- 投稿時間
- ハッシュタグ

### 注意

Instagram、TikTok、YouTubeの分析値取得は、公式APIや連携サービスの権限が必要。

最初は手入力でもよい。n8nは手入力された数値をもとに成功分析を自動化する。

## 6. 成功分析システム

### 抽出条件

- 保存率が高い
- 再生数が高い
- 完視聴率が高い

### 処理

```mermaid
flowchart TD
    A["Google Sheets: 投稿分析"] --> B["IF: 保存率・再生数・完視聴率判定"]
    B --> C["ChatGPT: 成功理由分析"]
    C --> D["Google Sheets: 成功パターンDB保存"]
    C --> E["Notion: バズ構成保存"]
    C --> F["次回ネタ候補を生成"]
```

