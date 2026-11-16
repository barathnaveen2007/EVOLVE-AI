from database.db import get_connection

def create_experiment(prediction_id, title, duration_days, measure, target_value):
    with get_connection() as c:
        cur = c.execute("""INSERT INTO experiments
            (prediction_id, title, duration_days, measure, target_value)
            VALUES(?,?,?,?,?)""",
            (prediction_id, title, duration_days, measure, target_value))
        return cur.lastrowid

def add_observation(experiment_id, value, notes=""):
    with get_connection() as c:
        cur = c.execute("INSERT INTO observations(experiment_id,value,notes) VALUES(?,?,?)",
                        (experiment_id, value, notes))
        return cur.lastrowid

def get_experiment_summary(experiment_id):
    with get_connection() as c:
        rows = c.execute("SELECT * FROM observations WHERE experiment_id=? ORDER BY id",
                         (experiment_id,)).fetchall()
    return {"count": len(rows), "items": rows}
