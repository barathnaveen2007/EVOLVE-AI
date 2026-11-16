import streamlit as st
from datetime import date, timedelta
from database.db import init_db, get_connection
from core.future_lab import generate_scenarios
from core.evolution import build_evolution_report
from core.experiment import create_experiment, add_observation, get_experiment_summary
from core.prediction import save_prediction, list_predictions

st.set_page_config(page_title="EVOLVE AI", page_icon="🌱", layout="wide")
init_db()

st.markdown("""
<style>
.main {background: #0b1020;}
.block-container {padding-top: 2rem; max-width: 1250px;}
[data-testid="stMetric"] {background: rgba(255,255,255,.04); padding: 14px; border-radius: 12px;}
</style>
""", unsafe_allow_html=True)

def conn():
    return get_connection()

def load_profile():
    with conn() as c:
        return c.execute("SELECT * FROM profiles WHERE id=1").fetchone()

def load_goals():
    with conn() as c:
        return c.execute("SELECT * FROM goals ORDER BY created_at DESC").fetchall()

st.sidebar.title("🌱 EVOLVE AI")
st.sidebar.caption("Your life, understood. Your future, explored.")
page = st.sidebar.radio("Navigate", [
    "Dashboard", "My Profile", "Goals", "Future Lab",
    "Experiments", "Prediction Ledger", "Evolution Report"
])
st.sidebar.divider()
st.sidebar.caption("Prototype note: scenario scores are transparent heuristics, not guaranteed predictions.")

if page == "Dashboard":
    st.title("Your personal intelligence dashboard")
    st.write("EVOLVE AI helps you explore plans, test recommendations and learn from actual outcomes.")
    profile = load_profile()
    goals = load_goals()
    with conn() as c:
        pred_count = c.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
        exp_count = c.execute("SELECT COUNT(*) FROM experiments").fetchone()[0]
        obs_count = c.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
    a,b,c1,d = st.columns(4)
    a.metric("Active goals", sum(1 for g in goals if g["status"] == "Active"))
    b.metric("Saved predictions", pred_count)
    c1.metric("Experiments", exp_count)
    d.metric("Observations", obs_count)
    st.subheader("Your current profile")
    if profile and profile["name"]:
        st.write(f"**{profile['name']}** · {profile['occupation'] or 'Role not set'}")
        st.write(profile["about"] or "Add a short description in My Profile.")
    else:
        st.info("Start by adding your profile and one goal.")
    st.subheader("Current goals")
    if goals:
        for g in goals[:5]:
            st.write(f"**{g['title']}** — {g['status']} · Target: {g['target_date'] or 'Not set'}")
    else:
        st.caption("No goals yet. Create one in the Goals section.")
    st.info("Suggested workflow: create a goal → compare scenarios → save a prediction → run an experiment → record results → review evolution.")

elif page == "My Profile":
    st.title("My Profile")
    st.write("Give EVOLVE AI useful context. Only enter information you are comfortable storing locally.")
    p = load_profile()
    with st.form("profile"):
        name = st.text_input("Name or nickname", value=p["name"] or "")
        occupation = st.text_input("Current role / study status", value=p["occupation"] or "")
        skills = st.text_area("Skills and experience", value=p["skills"] or "", placeholder="Python basics, beginner machine learning...")
        availability = st.number_input("Hours available per week", min_value=0.0, max_value=100.0, value=float(p["weekly_hours"] or 5), step=0.5)
        preferences = st.text_area("Preferences and working style", value=p["preferences"] or "", placeholder="Prefer practical projects, short daily sessions...")
        constraints = st.text_area("Constraints", value=p["constraints"] or "", placeholder="College schedule, limited budget...")
        about = st.text_area("Anything else EVOLVE AI should know", value=p["about"] or "")
        if st.form_submit_button("Save profile", type="primary"):
            with conn() as c:
                c.execute("""UPDATE profiles SET name=?, occupation=?, skills=?, weekly_hours=?,
                    preferences=?, constraints=?, about=?, updated_at=CURRENT_TIMESTAMP WHERE id=1""",
                    (name, occupation, skills, availability, preferences, constraints, about))
            st.success("Profile saved locally.")

elif page == "Goals":
    st.title("Goals")
    with st.form("new_goal", clear_on_submit=True):
        title = st.text_input("What do you want to achieve?", placeholder="Become an AI engineer")
        description = st.text_area("Why is this important? What does success look like?")
        target = st.date_input("Target date", value=date.today() + timedelta(days=180))
        if st.form_submit_button("Create goal", type="primary"):
            if not title.strip():
                st.error("Please enter a goal title.")
            else:
                with conn() as c:
                    c.execute("INSERT INTO goals(title, description, target_date) VALUES(?,?,?)",
                              (title.strip(), description, target.isoformat()))
                st.success("Goal created.")
    st.subheader("Your goals")
    for g in load_goals():
        with st.expander(f"{g['title']} · {g['status']}"):
            st.write(g["description"] or "No description.")
            st.caption(f"Target date: {g['target_date'] or 'Not set'}")
            new_status = st.selectbox("Status", ["Active", "Paused", "Completed"], index=["Active","Paused","Completed"].index(g["status"]), key=f"status{g['id']}")
            if st.button("Update status", key=f"up{g['id']}"):
                with conn() as c:
                    c.execute("UPDATE goals SET status=? WHERE id=?", (new_status, g["id"]))
                st.rerun()

elif page == "Future Lab":
    st.title("🔮 Future Lab")
    st.write("Compare possible approaches. Scores are rule-based planning indicators, not probabilities of success.")
    goals = load_goals()
    if not goals:
        st.warning("Create a goal first.")
    else:
        goal_map = {f"{g['title']} (#{g['id']})": g for g in goals}
        selected = st.selectbox("Choose a goal", list(goal_map.keys()))
        goal = goal_map[selected]
        p = load_profile()
        hours = st.number_input("Hours you can realistically spend each week", 0.5, 80.0, float(p["weekly_hours"] or 5), 0.5)
        consistency = st.slider("How confident are you that you can follow a schedule?", 1, 10, 6)
        practical = st.slider("How much do you prefer learning by doing?", 1, 10, 7)
        if st.button("Generate possible futures", type="primary"):
            scenarios = generate_scenarios(hours, consistency, practical)
            st.session_state["scenarios"] = scenarios
            st.session_state["scenario_goal_id"] = goal["id"]
        scenarios = st.session_state.get("scenarios", [])
        if scenarios and st.session_state.get("scenario_goal_id") == goal["id"]:
            st.subheader("Alternative paths")
            cols = st.columns(len(scenarios))
            for col, s in zip(cols, scenarios):
                with col:
                    st.markdown(f"### {s['name']}")
                    st.metric("Planning fit score", f"{s['score']}/100")
                    st.progress(s["score"] / 100)
                    st.write(s["description"])
                    st.caption("Why this score?")
                    st.write(s["rationale"])
                    if st.button(f"Choose {s['name']}", key=f"choose{s['key']}"):
                        pred_id = save_prediction(goal["id"], s, hours, consistency, practical)
                        st.session_state["chosen_prediction"] = pred_id
                        st.success(f"Saved as prediction #{pred_id}. You can now create an experiment.")
            if st.session_state.get("chosen_prediction"):
                st.info(f"Latest saved prediction: #{st.session_state['chosen_prediction']}")

elif page == "Experiments":
    st.title("🧪 Experiment Studio")
    st.write("Turn a selected plan into a small, measurable test.")
    predictions = list_predictions()
    if not predictions:
        st.info("Save a scenario from Future Lab before creating an experiment.")
    else:
        pred_options = {f"Prediction #{p['id']} — {p['scenario_name']} (Goal #{p['goal_id']})": p for p in predictions}
        chosen = st.selectbox("Choose a saved prediction", list(pred_options.keys()))
        pred = pred_options[chosen]
        with st.form("experiment"):
            title = st.text_input("Experiment name", value=f"7-day test: {pred['scenario_name']}")
            duration = st.number_input("Duration (days)", min_value=1, max_value=90, value=7)
            measure = st.text_input("What will you measure?", value="Completed focused study sessions")
            target = st.number_input("Target amount over the experiment", min_value=1, max_value=1000, value=5)
            if st.form_submit_button("Create experiment", type="primary"):
                eid = create_experiment(pred["id"], title, int(duration), measure, float(target))
                st.success(f"Experiment #{eid} created.")
    with conn() as c:
        experiments = c.execute("""SELECT e.*, p.scenario_name FROM experiments e
            JOIN predictions p ON p.id=e.prediction_id ORDER BY e.id DESC""").fetchall()
    st.subheader("Record actual outcomes")
    if experiments:
        emap = {f"#{e['id']} {e['title']}": e for e in experiments}
        label = st.selectbox("Experiment", list(emap.keys()))
        e = emap[label]
        st.caption(f"Measure: {e['measure']} · Target: {e['target_value']} · Duration: {e['duration_days']} days")
        with st.form("observation"):
            observed = st.number_input("Actual measured amount", min_value=0.0, value=0.0, step=1.0)
            note = st.text_area("What happened? What helped or got in the way?")
            if st.form_submit_button("Save observation"):
                add_observation(e["id"], observed, note)
                st.success("Observation saved.")
        st.subheader("Experiment history")
        for e in experiments:
            summary = get_experiment_summary(e["id"])
            with st.expander(f"Experiment #{e['id']}: {e['title']}"):
                st.write(f"**{summary['count']}** observation(s)")
                for item in summary["items"]:
                    st.write(f"{item['created_at'][:10]} · {item['value']} · {item['notes'] or 'No note'}")
    else:
        st.caption("No experiments created yet.")

elif page == "Prediction Ledger":
    st.title("📒 Prediction Accountability Ledger")
    st.write("Original predictions are preserved so later outcomes can be compared fairly.")
    preds = list_predictions()
    if not preds:
        st.info("No predictions yet. Generate and save one in Future Lab.")
    else:
        for p in preds:
            with st.expander(f"Prediction #{p['id']} · {p['scenario_name']} · {p['created_at'][:10]}"):
                st.write(f"**Goal:** {p['goal_title']}")
                st.write(f"**Forecast:** {p['forecast_text']}")
                st.write(f"**Assumptions:** {p['assumptions']}")
                st.write(f"**Confidence:** {p['confidence']}/100")
                st.caption(f"Planning fit score at creation: {p['score']}/100. This is not a probability.")

elif page == "Evolution Report":
    st.title("🌱 Evolution Report")
    st.write("A transparent review of what EVOLVE AI predicted and what your recorded results show.")
    report = build_evolution_report()
    a,b,c = st.columns(3)
    a.metric("Saved predictions", report["predictions"])
    b.metric("Experiments", report["experiments"])
    c.metric("Recorded observations", report["observations"])
    if report["comparisons"]:
        st.subheader("Forecast versus reality")
        for item in report["comparisons"]:
            st.markdown(f"**{item['experiment']}**")
            st.write(f"Target: {item['target']} · Recorded actual total: {item['actual']}")
            st.write(item["interpretation"])
    else:
        st.info("Record experiment observations to unlock comparisons.")
    st.subheader("What the system can responsibly learn")
    st.write("- Which schedules you actually completed.")
    st.write("- Which obstacles repeatedly appeared in your notes.")
    st.write("- Whether the selected experiment met its measurable target.")
    st.write("- Which assumptions should be reconsidered next time.")
    st.warning("This prototype updates its recommendations using recorded evidence and transparent rules. It does not retrain the underlying language model or guarantee future outcomes.")
