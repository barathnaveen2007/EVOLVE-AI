from database.db import get_connection

def save_prediction(goal_id, scenario, weekly_hours, consistency, practical):
    with get_connection() as c:
        cur = c.execute("""INSERT INTO predictions
            (goal_id, scenario_key, scenario_name, score, forecast_text, assumptions,
             confidence, weekly_hours, consistency, practical)
            VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (goal_id, scenario["key"], scenario["name"], scenario["score"],
             scenario["forecast_text"], scenario["assumptions"],
             60, weekly_hours, consistency, practical))
        return cur.lastrowid

def list_predictions():
    with get_connection() as c:
        return c.execute("""SELECT p.*, g.title AS goal_title FROM predictions p
            JOIN goals g ON g.id=p.goal_id ORDER BY p.id DESC""").fetchall()
