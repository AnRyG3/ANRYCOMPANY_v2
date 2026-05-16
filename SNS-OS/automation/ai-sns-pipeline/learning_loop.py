def judge_winner(row, config):
    cond = config["winning_conditions"]
    return (
        row["save_rate"] >= cond["save_rate"]
        or row["comment_rate"] >= cond["comment_rate"]
        or row["retention_rate"] >= cond["retention_rate"]
        or row["ctr"] >= cond["ctr"]
    )


def failure_analysis(row, config):
    cond = config["winning_conditions"]
    failures = []
    if row["save_rate"] < cond["save_rate"]:
        failures.append("保存率が弱い: 保存したくなるチェックリスト化が必要。")
    if row["comment_rate"] < cond["comment_rate"]:
        failures.append("コメント率が弱い: 選択式の問いかけを追加。")
    if row["retention_rate"] < cond["retention_rate"]:
        failures.append("視聴維持率が弱い: 尺短縮または中盤の説明削減。")
    if row["ctr"] < cond["ctr"]:
        failures.append("CTRが弱い: サムネとタイトルを強化。")
    return failures


def improvement_plan(row, config):
    failures = failure_analysis(row, config)
    if not failures:
        return ["同じ構成で別テーマへ横展開する。", "シリーズ化して次回予告を入れる。"]
    return failures
