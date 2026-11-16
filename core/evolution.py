from database.db import get_connection

def build_evolution_report():
    with get_connection() as c:
        predictions = c.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
        experiments = c.execute("SELECT COUNT(*) FROM experiments").fetchone()[0]
        observations = c.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
        rows = c.execute("""
            SELECT e.title AS experiment, e.target_value AS target,
                   COALESCE(SUM(o.value),0) AS actual, COUNT(o.id) AS n
            FROM experiments e LEFT JOIN observations o ON o.experiment_id=e.id
            GROUP BY e.id ORDER BY e.id DESC
        """).fetchall()
    comparisons = []
    for r in rows:
        if r["n"] == 0:
            continue
        actual = float(r["actual"])
        target = float(r["target"])
        if actual >= target:
            interpretation = "The recorded total met or exceeded the experiment target. Consider which conditions helped."
        else:
            interpretation = "The recorded total was below the experiment target. Review obstacles and whether the target or plan was realistic."
        comparisons.append({
            "experiment": r["experiment"], "target": target,
            "actual": actual, "interpretation": interpretation
        })
    return {
        "predictions": predictions, "experiments": experiments,
        "observations": observations, "comparisons": comparisons
    }
