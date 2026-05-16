def generate_video_plan(idea, script_data):
    return {
        "vrew_flow": [
            "VOICEVOXまたはナレーション音声を読み込む",
            "自動字幕を生成する",
            "専門用語の誤変換を修正する",
            "字幕を短く区切る"
        ],
        "capcut_flow": [
            "9:16で新規作成",
            "冒頭1秒に強フックを大きく表示",
            "2〜4秒ごとに画面変化",
            "重要語を青で強調",
            "最後に保存CTAとコメントCTA"
        ],
        "telop_design": "白背景、濃いグレー文字、重要語は青、1画面2行まで。",
        "bgm_tempo": "medium",
        "length_sec": 35
    }
