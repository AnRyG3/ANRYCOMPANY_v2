# Metricool 連携状況

更新日: 2026-05-31

## 連携済み

- Instagram: `rt.education.ch`
- YouTube: 診療放射線技師の安心ラボ
- Metricoolブランド: InstagramとYouTubeが同じブランド内に表示されることを確認済み

## 目的

InstagramとYouTubeの結果をMetricoolに集約し、分析班が週次で確認できるようにする。

## 次の作業

1. 無料プランでは、Metricool画面からInstagramとYouTubeのCSVを週次でダウンロードする。
2. CSVを分析保管場所へ入れる。
3. 分析班が週次ExcelとObsidian記録を更新する。
4. 将来Advanced以上へ変更した場合は、Metricool MCPをn8nへ接続して自動取得へ切り替える。

## 補足

- YouTubeはMetricoolで指標がそろうまで時間がかかる場合がある。
- 当面、YouTube StudioのCSVは月末確認用のバックアップとして残す。
- Instagramはフォロワー数が少ない間、一部の視聴者属性が表示されない場合がある。
- Metricoolのn8n接続にはAPI Keyが必要。API KeyはAdvancedまたはCustomプランで利用できる。
