import csv
import json
from collections import Counter
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
POST_RESULTS = BASE_DIR / "csv" / "post_results.csv"
RULES_PATH = BASE_DIR / "rules" / "learning_rules.json"
REPORT_PATH = BASE_DIR / "reports" / "latest_learning_report.md"
WINNING_DB = BASE_DIR / "db" / "winning_pattern_db.csv"


def load_rules():
    with RULES_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def to_float(value, default=0.0):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except ValueError:
        return default


def load_posts():
    with POST_RESULTS.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def calc_rates(post):
    reach = to_float(post.get("reach"))
    saves = to_float(post.get("saves"))
    comments = to_float(post.get("comments"))
    follows = to_float(post.get("follows"))
    if reach <= 0:
        return {"save_rate": 0, "comment_rate": 0, "follow_rate": 0}
    return {
        "save_rate": round(saves / reach * 100, 2),
        "comment_rate": round(comments / reach * 100, 2),
        "follow_rate": round(follows / reach * 100, 2),
    }


def normalized(value, benchmark):
    if benchmark <= 0:
        return 0
    return min(100, (value / benchmark) * 100)


def buzz_score(post, rules):
    rates = calc_rates(post)
    benchmarks = rules["benchmarks"]
    weights = rules["weights"]
    score = 0
    score += normalized(to_float(post.get("views")), benchmarks["views"]) * weights["views"]
    score += normalized(rates["save_rate"], benchmarks["save_rate"]) * weights["save_rate"]
    score += normalized(rates["comment_rate"], benchmarks["comment_rate"]) * weights["comment_rate"]
    score += normalized(rates["follow_rate"], benchmarks["follow_rate"]) * weights["follow_rate"]
    score += normalized(to_float(post.get("completion_rate")), benchmarks["completion_rate"]) * weights["completion_rate"]
    return round(score, 1), rates


def buzz_label(score, rules):
    thresholds = rules["buzz_thresholds"]
    if score >= thresholds["buzz"]:
        return "バズ判定"
    if score >= thresholds["strong"]:
        return "強い"
    if score >= thresholds["normal"]:
        return "通常"
    return "改善"


def common_points(posts):
    fields = [
        "hook",
        "length_sec",
        "telop_count",
        "line_break_count",
        "effect_style",
        "bgm_tempo",
        "comment_cta",
        "save_cta",
        "emotion_category",
    ]
    result = {}
    for field in fields:
        values = [p.get(field, "") for p in posts if p.get(field, "")]
        result[field] = Counter(values).most_common(5)
    return result


def failure_analysis(post, rates, rules):
    failures = []
    benchmarks = rules["benchmarks"]
    failure_rules = rules["failure_rules"]
    if rates["save_rate"] < benchmarks["save_rate"]:
        failures.append(failure_rules["low_save_rate"])
    if rates["comment_rate"] < benchmarks["comment_rate"]:
        failures.append(failure_rules["low_comment_rate"])
    if to_float(post.get("completion_rate")) < benchmarks["completion_rate"]:
        failures.append(failure_rules["low_completion_rate"])
    if rates["follow_rate"] < benchmarks["follow_rate"]:
        failures.append(failure_rules["low_follow_rate"])
    return failures


def next_improvement(post, rates, rules):
    ideas = []
    if rates["save_rate"] < rules["benchmarks"]["save_rate"]:
        ideas.append("保存型に寄せる: 『検査前に見返せる3つのポイント』へ変更。")
    if rates["comment_rate"] < rules["benchmarks"]["comment_rate"]:
        ideas.append("コメント誘導を選択式にする: 『CTとMRIどっちが怖いですか？』")
    if to_float(post.get("completion_rate")) < rules["benchmarks"]["completion_rate"]:
        ideas.append("尺を短くし、中盤の説明を1つ削る。")
    if rates["follow_rate"] < rules["benchmarks"]["follow_rate"]:
        ideas.append("放射線技師視点と次回予告を追加する。")
    if not ideas:
        ideas.append("同じ構成で別テーマへ横展開する。")
    return ideas


def write_winning_db(rows):
    headers = [
        "post_id",
        "theme",
        "hook",
        "length_sec",
        "telop_count",
        "effect_style",
        "bgm_tempo",
        "emotion_category",
        "buzz_score",
        "reason",
        "next_idea",
    ]
    with WINNING_DB.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def generate_report():
    rules = load_rules()
    posts = load_posts()
    analyzed = []
    winning_rows = []

    for post in posts:
        score, rates = buzz_score(post, rules)
        label = buzz_label(score, rules)
        failures = failure_analysis(post, rates, rules)
        improvements = next_improvement(post, rates, rules)
        row = {
            "post": post,
            "score": score,
            "rates": rates,
            "label": label,
            "failures": failures,
            "improvements": improvements,
        }
        analyzed.append(row)
        if label in ["バズ判定", "強い"]:
            winning_rows.append({
                "post_id": post.get("post_id", ""),
                "theme": post.get("theme", ""),
                "hook": post.get("hook", ""),
                "length_sec": post.get("length_sec", ""),
                "telop_count": post.get("telop_count", ""),
                "effect_style": post.get("effect_style", ""),
                "bgm_tempo": post.get("bgm_tempo", ""),
                "emotion_category": post.get("emotion_category", ""),
                "buzz_score": score,
                "reason": f"{label}: 保存率{rates['save_rate']}%, コメント率{rates['comment_rate']}%, 完視聴率{post.get('completion_rate', '')}%",
                "next_idea": "同型で別テーマへ展開",
            })

    analyzed.sort(key=lambda x: x["score"], reverse=True)
    write_winning_db(winning_rows)

    winners = [x["post"] for x in analyzed if x["label"] in ["バズ判定", "強い"]]
    points = common_points(winners or [x["post"] for x in analyzed])

    lines = []
    lines.append("# 最新 学習ループレポート\n")
    lines.append("## 投稿ランキング\n")
    lines.append("| 順位 | 投稿ID | テーマ | バズスコア | 判定 | 保存率 | コメント率 | フォロー率 | 完視聴率 |")
    lines.append("|---:|---|---|---:|---|---:|---:|---:|---:|")
    for i, item in enumerate(analyzed, start=1):
        post = item["post"]
        rates = item["rates"]
        lines.append(
            f"| {i} | {post.get('post_id','')} | {post.get('theme','')} | {item['score']} | {item['label']} | {rates['save_rate']} | {rates['comment_rate']} | {rates['follow_rate']} | {post.get('completion_rate','')} |"
        )

    lines.append("\n## 共通点抽出\n")
    for field, values in points.items():
        readable = ", ".join([f"{value}({count})" for value, count in values]) or "データなし"
        lines.append(f"- {field}: {readable}")

    lines.append("\n## 失敗分析\n")
    for item in analyzed:
        post = item["post"]
        if item["failures"]:
            lines.append(f"### {post.get('post_id','')}: {post.get('theme','')}")
            for failure in item["failures"]:
                lines.append(f"- {failure}")

    lines.append("\n## 次回改善提案\n")
    for item in analyzed[:5]:
        post = item["post"]
        lines.append(f"### {post.get('post_id','')}: {post.get('theme','')}")
        for idea in item["improvements"]:
            lines.append(f"- {idea}")

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return REPORT_PATH


if __name__ == "__main__":
    path = generate_report()
    print(f"Learning report generated: {path}")
