import json


def contains_any(text, keywords):
    text = text.lower()
    return any(str(keyword).lower() in text for keyword in keywords)


def score_idea(idea, config):
    theme = idea.get("theme", "")
    category = idea.get("category", "")
    target = idea.get("target", "")
    pain = idea.get("pain_point", "")
    tags = idea.get("medical_tags", "")
    text = f"{theme} {category} {target} {pain} {tags}"
    weights = config["score_weights"]

    scores = {
        "hook_power": 0,
        "save_potential": 0,
        "empathy": 0,
        "ctr_potential": 0,
        "comment_power": 0,
        "expertise": 0,
        "buzz_potential": 0,
    }

    if contains_any(text, ["危険", "怖い", "誤解", "知らない", "ポイント", "理由"]):
        scores["hook_power"] = weights["hook_power"]
    else:
        scores["hook_power"] = weights["hook_power"] * 0.45

    if contains_any(text, ["検査前", "ポイント", "保存", "被ばく", "CT", "MRI", "整形撮影"]):
        scores["save_potential"] = weights["save_potential"]
    else:
        scores["save_potential"] = weights["save_potential"] * 0.5

    if contains_any(text, ["怖い", "不安", "分からない", "曖昧", "心配"]):
        scores["empathy"] = weights["empathy"]
    else:
        scores["empathy"] = weights["empathy"] * 0.4

    if contains_any(theme, ["危険", "理由", "違い", "誤解", "ポイント"]):
        scores["ctr_potential"] = weights["ctr_potential"]
    else:
        scores["ctr_potential"] = weights["ctr_potential"] * 0.5

    if contains_any(text, ["どっち", "ありますか", "経験", "怖い", "分からない"]):
        scores["comment_power"] = weights["comment_power"] * 0.8
    else:
        scores["comment_power"] = weights["comment_power"] * 0.45

    if contains_any(tags, config["medical_tags"]):
        scores["expertise"] = weights["expertise"]
    else:
        scores["expertise"] = weights["expertise"] * 0.5

    if category in ["不安解消", "医療雑学", "整形撮影"]:
        scores["buzz_potential"] = weights["buzz_potential"] * 0.9
    else:
        scores["buzz_potential"] = weights["buzz_potential"] * 0.55

    total = round(sum(scores.values()), 1)
    risks = []
    for keyword in config.get("risk_keywords", []):
        if keyword in text:
            risks.append(f"危険表現: {keyword}")

    improvements = []
    if scores["hook_power"] < weights["hook_power"] * 0.8:
        improvements.append("冒頭に『実は』『それ誤解です』『怖い人へ』を入れる。")
    if scores["save_potential"] < weights["save_potential"] * 0.8:
        improvements.append("保存価値を『検査前に見返す3ポイント』へ寄せる。")
    if scores["comment_power"] < weights["comment_power"] * 0.8:
        improvements.append("コメント誘導を選択式にする。")

    return {
        "score": total,
        "detail": scores,
        "risks": risks,
        "improvements": improvements,
    }
