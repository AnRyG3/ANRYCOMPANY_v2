# AI SNS運営パイプライン

## 目的

Instagramリール運用を半自動化し、ネタ入力から分析・改善までを一連の流れとして管理する。

## 処理フロー

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

## フォルダ構成

```text
ai-sns-pipeline/
├─ README.md
├─ pipeline_manager.py
├─ score_engine.py
├─ learning_loop.py
├─ analytics.py
├─ config.json
├─ data/
│  ├─ ideas.csv
│  ├─ post_management.csv
│  ├─ kpi_management.csv
│  └─ buzz_db.csv
├─ modules/
│  ├─ script_generator.py
│  ├─ image_prompt_generator.py
│  └─ video_plan_generator.py
├─ outputs/
│  └─ latest_pipeline_report.md
└─ docs/
   └─ 初心者向け解説.md
```

## 必要機能

### 1. ネタ入力

- ネタDB
- カテゴリ管理
- 医療系タグ
- 優先度

### 2. AI採点

- フック力
- 保存率期待
- 共感性
- CTR期待
- コメント誘導
- 専門性
- バズ期待値

### 3. 台本生成

- リール台本
- Shorts対応
- TikTok対応
- CTA生成
- 保存誘導

### 4. 画像生成

- Gemini用プロンプト
- image generation用プロンプト
- サムネ生成
- 構図提案

### 5. 動画生成

- Vrew連携想定
- CapCut編集フロー
- テロップ設計
- BGMテンポ管理

### 6. 投稿管理

- 投稿予定
- 投稿済み
- CSV管理
- KPI管理

### 7. 数値回収

- 再生数
- 保存率
- コメント率
- 視聴維持率
- CTR

### 8. 学習

- バズ共通点抽出
- 失敗分析
- 勝ちパターンDB
- 投稿ランキング

### 9. 改善提案

- 次回改善案
- A/Bテスト案
- フック改善
- 尺改善
- CTA改善

## 実行方法

```powershell
python pipeline_manager.py
```

`python` が通らない場合は、Python実行ファイルのフルパスで実行する。

