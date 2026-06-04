# tools 案内

制作・変換・整理に使うスクリプトとローカル環境を用途別に保管する。

## 現行の制作スクリプト

| フォルダ | 内容 |
|---|---|
| `pre_exam_series` | 検査前シリーズ |
| `echo_series` | エコーシリーズ |
| `mammography_series` | マンモグラフィーシリーズ |
| `result_wait_series` | 検査結果・再検査シリーズ |
| `line_stamp_builders` | LINEスタンプ制作・分割・整形 |
| `ct_video_builders` | CT動画制作 |

## 共通ツール

| フォルダ | 内容 |
|---|---|
| `image_generation` | 画像生成 |
| `spreadsheet_work` | 表計算の作業用 |
| `n8n-local` | n8nローカル環境 |
| `runtime` | ローカル実行環境 |
| `ffmpeg` | 動画・音声変換 |

## 過去スクリプト

| フォルダ | 内容 |
|---|---|
| `legacy_reel_builders` | 過去のCT・MRI・共通エンドカード用 |
| `legacy_line_stamp_builders` | 過去のLINEスタンプ用。文字化け済みの旧スクリプトを含む |

## ルール

- 新しいスクリプトは用途に合うフォルダへ置く。
- `runtime` と `ffmpeg` は移動しない。
- `__pycache__` は自動生成キャッシュなので作業対象にしない。
- `legacy_*` は過去素材の確認用。新しい制作では使わない。
