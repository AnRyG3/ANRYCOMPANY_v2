def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def enrich_kpi(row):
    reach = safe_float(row.get("reach"))
    saves = safe_float(row.get("saves"))
    comments = safe_float(row.get("comments"))
    follows = safe_float(row.get("follows"))
    views = safe_float(row.get("views"))
    retention = safe_float(row.get("retention_rate"))
    ctr = safe_float(row.get("ctr"))

    save_rate = saves / reach * 100 if reach else safe_float(row.get("save_rate"))
    comment_rate = comments / reach * 100 if reach else safe_float(row.get("comment_rate"))
    follow_rate = follows / reach * 100 if reach else safe_float(row.get("follow_rate"))

    return {
        **row,
        "views": views,
        "save_rate": round(save_rate, 2),
        "comment_rate": round(comment_rate, 2),
        "follow_rate": round(follow_rate, 2),
        "retention_rate": retention,
        "ctr": ctr,
    }


def rank_posts(kpi_rows):
    def score(row):
        return (
            min(row["views"] / 10000 * 20, 20)
            + min(row["save_rate"] / 5 * 25, 25)
            + min(row["comment_rate"] / 1 * 15, 15)
            + min(row["retention_rate"] / 70 * 25, 25)
            + min(row["ctr"] / 3 * 15, 15)
        )

    ranked = []
    for row in kpi_rows:
        enriched = enrich_kpi(row)
        enriched["pipeline_score"] = round(score(enriched), 1)
        ranked.append(enriched)
    return sorted(ranked, key=lambda item: item["pipeline_score"], reverse=True)
