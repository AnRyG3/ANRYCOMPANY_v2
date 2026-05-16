# DB構成

## post_results.csv

投稿結果の元データ。

| カラム | 内容 |
|---|---|
| post_id | 投稿ID |
| published_date | 投稿日 |
| title | タイトル |
| theme | テーマ |
| hook | 冒頭ワード |
| length_sec | 尺 |
| telop_count | テロップ量 |
| line_break_count | 改行数 |
| effect_style | 演出 |
| bgm_tempo | BGMテンポ |
| comment_cta | コメント誘導 |
| save_cta | 保存誘導 |
| emotion_category | 感情カテゴリ |
| views | 再生数 |
| reach | リーチ |
| saves | 保存数 |
| comments | コメント数 |
| follows | フォロー増加 |
| completion_rate | 完視聴率 |

## 自動計算

| 指標 | 計算 |
|---|---|
| 保存率 | saves ÷ reach × 100 |
| コメント率 | comments ÷ reach × 100 |
| フォロー率 | follows ÷ reach × 100 |
| バズスコア | 再生・保存率・コメント率・フォロー率・完視聴率の加重平均 |

## winning_pattern_db.csv

バズ判定された投稿を保存するDB。

| カラム | 内容 |
|---|---|
| post_id | 投稿ID |
| theme | テーマ |
| hook | 冒頭ワード |
| length_sec | 尺 |
| telop_count | テロップ量 |
| effect_style | 演出 |
| bgm_tempo | BGMテンポ |
| emotion_category | 感情カテゴリ |
| buzz_score | バズスコア |
| reason | 勝ち理由 |
| next_idea | 次回改善案 |

