def generate_script(idea):
    theme = idea.get("theme", "")
    pain = idea.get("pain_point", "不安")
    category = idea.get("category", "")

    hook = f"{theme}と思っている人へ"
    if "危険" in theme or "怖い" in pain:
        hook = f"{theme}が不安な人へ"
    elif "理由" in theme:
        hook = "これ、9割知らない"
    elif "ポイント" in theme:
        hook = "技師が見るポイント"

    script = [
        f"0〜3秒: {hook}",
        f"3〜8秒: 結論、過度に不安になりすぎなくて大丈夫です。",
        f"8〜18秒: 理由は、検査には目的があり、必要な情報を得るために行われるからです。",
        f"18〜28秒: 放射線技師の視点では、撮影条件や見やすさを確認しています。",
        f"28〜35秒: 不安な時は相談してOK。あとで見返せるよう保存してね。"
    ]

    return {
        "hook": hook,
        "script": "\n".join(script),
        "shorts_note": "YouTube Shortsではタイトルに検索語を入れる。",
        "tiktok_note": "TikTokでは冒頭テロップを大きくし、コメント誘導を強める。",
        "save_cta": "あとで見返せるよう保存してね。",
        "comment_cta": "この検査で不安だったことはありますか？"
    }
