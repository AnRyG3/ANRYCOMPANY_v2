import json
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
RULE_PATH = BASE_DIR / "rules" / "scoring_rules.json"


def load_rules():
    with RULE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def normalize_text(value):
    if value is None:
        return ""
    if isinstance(value, list):
        return " ".join(str(v) for v in value)
    return str(value)


def keyword_score(text, criterion):
    max_score = criterion["max"]
    positives = criterion.get("positive_keywords", [])
    weak_patterns = criterion.get("weak_patterns", [])

    hit_count = sum(1 for kw in positives if kw.lower() in text.lower())
    weak_count = sum(1 for kw in weak_patterns if kw.lower() in text.lower())

    if not positives:
        base = max_score * 0.5
    else:
        base = min(max_score, (hit_count / max(1, min(len(positives), 4))) * max_score)

    penalty = weak_count * (max_score * 0.18)
    return max(0, round(base - penalty, 1))


def calculate_score(post, rules):
    text_parts = [
        post.get("title", ""),
        post.get("hook", ""),
        post.get("script", ""),
        post.get("caption", ""),
        post.get("thumbnail_text", ""),
        post.get("comment_cta", ""),
        post.get("save_cta", ""),
        post.get("telop_notes", "")
    ]
    text = normalize_text(text_parts)

    detail = {}
    total = 0
    for key, criterion in rules["criteria"].items():
        score = keyword_score(text, criterion)
        detail[key] = {
            "label": criterion["label"],
            "score": score,
            "max": criterion["max"]
        }
        total += score

    total = round(min(rules["max_score"], total), 1)
    return total, detail


def detect_risks(post, rules):
    text = normalize_text(post.values())
    risks = []
    for kw in rules.get("risk_keywords", []):
        if kw.lower() in text.lower():
            risks.append(f"医療表現リスク: 「{kw}」は強すぎる可能性があります。")

    if len(normalize_text(post.get("hook", ""))) > 35:
        risks.append("フックが長めです。冒頭3秒で読める短さにしてください。")

    if "保存" not in text and "見返" not in text:
        risks.append("保存誘導が弱いです。保存する理由を明確にしてください。")

    if "コメント" not in text and "ありますか" not in text and "教えて" not in text:
        risks.append("コメント誘導が弱いです。答えやすい問いを入れてください。")

    return risks


def improvement_suggestions(detail):
    suggestions = []
    for key, item in detail.items():
        ratio = item["score"] / item["max"] if item["max"] else 0
        label = item["label"]
        if ratio >= 0.8:
            continue
        if key == "hook_power":
            suggestions.append("フックに「実は」「それ誤解です」「怖い人へ」などの停止ワードを入れる。")
        elif key == "save_potential":
            suggestions.append("保存価値を上げるために「検査前に見返す」「3つのポイント」型へ寄せる。")
        elif key == "comment_power":
            suggestions.append("コメント誘導は「CTとMRIどっちが怖いですか？」のように選択式にする。")
        elif key == "empathy":
            suggestions.append("冒頭で視聴者の不安や経験を代弁する。")
        elif key == "surprise":
            suggestions.append("一般人が知らない意外な事実や誤解訂正を入れる。")
        elif key == "expertise":
            suggestions.append("放射線技師視点として、現場で見ているポイントを1つ入れる。")
        elif key == "ctr_potential":
            suggestions.append("サムネに「危険？」「実は」「違い」などタップしたくなる語を入れる。")
        elif key == "first_3_sec_retention":
            suggestions.append("3秒以内に結論の方向性を出し、前置きを削る。")
        elif key == "title_strength":
            suggestions.append("タイトルにCT、MRI、レントゲン、被ばくなど検索語を入れる。")
        elif key == "telop_visibility":
            suggestions.append("テロップは1画面2行まで、大きく、重要語だけ色を変える。")
    return suggestions


def buzz_probability(score, rules):
    for _, item in sorted(rules["buzz_probability"].items(), key=lambda x: x[1]["min_score"], reverse=True):
        if score >= item["min_score"]:
            return item["label"]
    return "要改善"


def ab_test_ideas(post):
    title = post.get("title", "投稿")
    return [
        {
            "test": "フックA/B",
            "A": post.get("hook", ""),
            "B": "それ、実は誤解です。"
        },
        {
            "test": "サムネA/B",
            "A": post.get("thumbnail_text", ""),
            "B": f"{title}｜実は？"
        },
        {
            "test": "CTA A/B",
            "A": "あとで見返せるよう保存してね",
            "B": "検査前に見返せるよう保存推奨"
        }
    ]


def score_post(post):
    rules = load_rules()
    total, detail = calculate_score(post, rules)
    risks = detect_risks(post, rules)
    suggestions = improvement_suggestions(detail)
    return {
        "score": total,
        "max_score": rules["max_score"],
        "buzz_probability": buzz_probability(total, rules),
        "detail": detail,
        "improvement_suggestions": suggestions,
        "risk_points": risks,
        "ab_test_ideas": ab_test_ideas(post)
    }


if __name__ == "__main__":
    sample_post = {
        "title": "CTって危険？放射線技師が解説",
        "hook": "CTが怖い人、これだけ知ってください",
        "script": "結論、必要な検査なら過度に怖がりすぎなくて大丈夫です。放射線技師は撮影条件と範囲を確認しています。不安な時は相談して大丈夫です。",
        "caption": "検査前に見返せるよう保存してね。",
        "thumbnail_text": "CTって危険？",
        "comment_cta": "CTで不安だったことはありますか？",
        "save_cta": "検査前に見返せるよう保存推奨",
        "telop_notes": "白背景、青強調、大きい文字、2行まで"
    }
    result = score_post(sample_post)
    print(json.dumps(result, ensure_ascii=False, indent=2))
