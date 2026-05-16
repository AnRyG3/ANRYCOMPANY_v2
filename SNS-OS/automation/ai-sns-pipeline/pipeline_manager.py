import csv
import json
from pathlib import Path

from analytics import rank_posts
from learning_loop import failure_analysis, improvement_plan, judge_winner
from modules.image_prompt_generator import generate_image_prompts
from modules.script_generator import generate_script
from modules.video_plan_generator import generate_video_plan
from score_engine import score_idea


BASE_DIR = Path(__file__).resolve().parent


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fieldnames):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_pipeline_report(config, ideas, ranked_posts):
    lines = []
    lines.append("# AI SNS運営パイプライン レポート\n")

    lines.append("## ネタ入力 → AI採点 → 台本生成 → 画像生成 → 動画生成\n")
    for idea in ideas:
        score = score_idea(idea, config)
        script = generate_script(idea)
        image = generate_image_prompts(idea, script)
        video = generate_video_plan(idea, script)

        lines.append(f"### {idea.get('idea_id')}: {idea.get('theme')}")
        lines.append(f"- カテゴリ: {idea.get('category')}")
        lines.append(f"- 優先度: {idea.get('priority')}")
        lines.append(f"- AI採点: {score['score']} / 100")
        lines.append(f"- 危険ポイント: {', '.join(score['risks']) if score['risks'] else 'なし'}")
        lines.append(f"- 改善提案: {', '.join(score['improvements']) if score['improvements'] else '投稿候補'}")
        lines.append(f"- フック: {script['hook']}")
        lines.append(f"- 保存誘導: {script['save_cta']}")
        lines.append(f"- コメント誘導: {script['comment_cta']}")
        lines.append(f"- Geminiプロンプト: {image['gemini_prompt']}")
        lines.append(f"- サムネ案: {image['thumbnail']}")
        lines.append(f"- CapCut方針: {', '.join(video['capcut_flow'])}")
        lines.append("")

    lines.append("## 投稿管理 → 数値回収 → 学習 → 改善提案\n")
    lines.append("| 順位 | 投稿ID | スコア | 保存率 | コメント率 | 視聴維持率 | CTR | 勝ち判定 |")
    lines.append("|---:|---|---:|---:|---:|---:|---:|---|")
    for index, row in enumerate(ranked_posts, start=1):
        winner = judge_winner(row, config)
        lines.append(
            f"| {index} | {row.get('post_id')} | {row['pipeline_score']} | {row['save_rate']} | {row['comment_rate']} | {row['retention_rate']} | {row['ctr']} | {'勝ち' if winner else '改善'} |"
        )

    lines.append("\n## 失敗分析・次回改善\n")
    for row in ranked_posts:
        lines.append(f"### {row.get('post_id')}")
        for item in failure_analysis(row, config):
            lines.append(f"- {item}")
        lines.append("#### 次回改善")
        for item in improvement_plan(row, config):
            lines.append(f"- {item}")

    return "\n".join(lines) + "\n"


def update_buzz_db(config, ranked_posts):
    buzz_path = BASE_DIR / config["paths"]["buzz_db"]
    rows = []
    for row in ranked_posts:
        if judge_winner(row, config):
            rows.append({
                "post_id": row.get("post_id", ""),
                "theme": row.get("post_id", ""),
                "hook": "",
                "length_sec": "",
                "save_rate": row["save_rate"],
                "comment_rate": row["comment_rate"],
                "retention_rate": row["retention_rate"],
                "ctr": row["ctr"],
                "buzz_reason": f"pipeline_score={row['pipeline_score']}",
                "next_action": "同型で横展開"
            })
    fieldnames = ["post_id", "theme", "hook", "length_sec", "save_rate", "comment_rate", "retention_rate", "ctr", "buzz_reason", "next_action"]
    write_csv(buzz_path, rows, fieldnames)


def main():
    config = load_json(BASE_DIR / "config.json")
    ideas = load_csv(BASE_DIR / config["paths"]["ideas"])
    kpi_rows = load_csv(BASE_DIR / config["paths"]["kpi_management"])
    ranked_posts = rank_posts(kpi_rows)

    report = build_pipeline_report(config, ideas, ranked_posts)
    report_path = BASE_DIR / config["paths"]["report"]
    report_path.write_text(report, encoding="utf-8")
    update_buzz_db(config, ranked_posts)

    print(f"Pipeline report generated: {report_path}")


if __name__ == "__main__":
    main()
