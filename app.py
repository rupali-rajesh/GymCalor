import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, date, timedelta
from database import (
    init_db, register_user, login_user,
    save_prediction, get_user_predictions,
    log_meal, get_meals_by_date, get_weekly_meals, delete_meal, get_streak,
    update_calorie_goal, get_calorie_goal,
    get_all_users, get_user_stats, get_inactive_users,
    add_trainer_note, get_trainer_notes, delete_trainer_note
)

# ── Init DB ───────────────────────────────────────────────────────────────────
init_db()

# ── Owner credentials ─────────────────────────────────────────────────────────
OWNER_EMAIL    = "rupalirajesh06@gmail.com"
OWNER_PASSWORD = "Rupa1234"

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GymCalor",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0E1117; font-family: 'Inter', sans-serif; }
    h1, h2, h3 { color: #E2E8F0; }

    .stButton>button {
        background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%);
        color: white; border-radius: 8px; border: none;
        padding: 10px 24px; font-weight: 600;
        transition: all 0.3s ease; width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 65, 108, 0.4);
    }
    div[data-testid="stMetricValue"] {
        font-size: 2.5rem; color: #FF4B2B; font-weight: 700;
    }
    .header-title {
        text-align: center;
        background: -webkit-linear-gradient(#FF416C, #FF4B2B);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 3rem; font-weight: 800;
        margin-bottom: 0px; padding-bottom: 0px;
    }
    .header-sub {
        text-align: center; color: #A0AEC0;
        font-size: 1.2rem; margin-top: 0px; margin-bottom: 2rem;
    }
    div.stTabs [data-baseweb="tab-list"] { gap: 24px; }
    div.stTabs [data-baseweb="tab"] {
        height: 50px; white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        padding-top: 10px; padding-bottom: 10px;
        font-weight: 600; font-size: 1.1rem; color: #A0AEC0;
    }
    div.stTabs [aria-selected="true"] {
        color: #FF4B2B; border-bottom: 2px solid #FF4B2B;
    }
    .banner {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-left: 4px solid #FF4B2B; border-radius: 8px;
        padding: 12px 18px; margin-bottom: 16px;
        color: #E2E8F0; font-size: 1rem;
    }
    .note-card {
        background: #1A202C; border-radius: 8px;
        padding: 12px 16px; margin-bottom: 10px;
        border-left: 3px solid #FF4B2B; color: #E2E8F0;
    }
    .user-card {
        background: #1A202C; border-radius: 10px;
        padding: 16px; margin-bottom: 12px; color: #E2E8F0;
    }
    .inactive-badge {
        background: #FF4B2B; color: white;
        padding: 2px 10px; border-radius: 12px;
        font-size: 0.78rem; font-weight: 600;
    }
    .active-badge {
        background: #38A169; color: white;
        padding: 2px 10px; border-radius: 12px;
        font-size: 0.78rem; font-weight: 600;
    }
    .gain-badge {
        background: #3A86FF; color: white;
        padding: 2px 10px; border-radius: 12px;
        font-size: 0.78rem; font-weight: 600;
    }
    .lose-badge {
        background: #FF4B2B; color: white;
        padding: 2px 10px; border-radius: 12px;
        font-size: 0.78rem; font-weight: 600;
    }
    section[data-testid="stSidebar"] { background-color: #161b27; }
</style>
""", unsafe_allow_html=True)

# ── Session state defaults ────────────────────────────────────────────────────
for key, val in {
    "logged_in": False,
    "is_owner": False,
    "user": None,
    "history": []
}.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ══════════════════════════════════════════════════════════════════════════════
# AUTH PAGE
# ══════════════════════════════════════════════════════════════════════════════
def show_auth():
    _, mid, _ = st.columns([1, 1.5, 1])
    with mid:
        st.markdown(
            "<div style='text-align:center;font-size:2.8rem;font-weight:800;"
            "background:-webkit-linear-gradient(#FF416C,#FF4B2B);"
            "-webkit-background-clip:text;-webkit-text-fill-color:transparent'>"
            "💪 GymCalor</div>", unsafe_allow_html=True
        )
        st.markdown(
            "<div style='text-align:center;color:#718096;margin-bottom:24px'>"
            "Track your burn. Know your numbers.</div>", unsafe_allow_html=True
        )

        tab_login, tab_signup = st.tabs(["Log In", "Sign Up"])

        # ── LOGIN ──────────────────────────────────────────────────────────────
        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            email = st.text_input("Email", key="l_email", placeholder="you@email.com")
            pwd   = st.text_input("Password", key="l_pwd", type="password", placeholder="Your password")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Log In", key="btn_login"):
                # Owner check
                if email.strip() == OWNER_EMAIL and pwd == OWNER_PASSWORD:
                    st.session_state.logged_in = True
                    st.session_state.is_owner  = True
                    st.session_state.user      = {"name": "Rupali", "id": -1}
                    st.rerun()
                elif not email or not pwd:
                    st.warning("Please fill in both fields.")
                else:
                    ok, user, msg = login_user(email.strip(), pwd)
                    if ok:
                        st.session_state.logged_in = True
                        st.session_state.is_owner  = False
                        st.session_state.user      = user
                        st.rerun()
                    else:
                        st.error(msg)

        # ── SIGN UP ────────────────────────────────────────────────────────────
        with tab_signup:
            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                s_name  = st.text_input("Full Name",        key="s_name",  placeholder="Your name")
                s_email = st.text_input("Email",            key="s_email", placeholder="you@email.com")
                s_pwd   = st.text_input("Password",         key="s_pwd",   type="password", placeholder="Min 6 characters")
                s_pwd2  = st.text_input("Confirm Password", key="s_pwd2",  type="password")
            with c2:
                s_age    = st.number_input("Age",        min_value=10,   max_value=100,  value=22,   key="s_age")
                s_weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=60.0, key="s_weight")
                s_height = st.number_input("Height (m)", min_value=1.0,  max_value=2.5,  value=1.65, key="s_height")
                s_goal_type = st.selectbox(
                    "My Fitness Goal",
                    ["lose", "gain"],
                    format_func=lambda x: "🔥 Lose Weight / Burn Fat" if x == "lose" else "💪 Gain Muscle / Bulk Up",
                    key="s_goal_type"
                )
                s_goal = st.number_input(
                    "Daily Calorie Goal (kcal)",
                    min_value=1000, max_value=6000,
                    value=1800 if s_goal_type == "lose" else 2500,
                    key="s_goal"
                )
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Create Account", key="btn_signup"):
                if not s_name or not s_email or not s_pwd or not s_pwd2:
                    st.warning("Please fill in all fields.")
                elif s_pwd != s_pwd2:
                    st.error("Passwords don't match.")
                elif len(s_pwd) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    ok, result = register_user(
                        s_name, s_email, s_pwd,
                        s_age, s_weight, s_height, s_goal, s_goal_type
                    )
                    if ok:
                        st.success("Account created! Head to Log In 🎉")
                    else:
                        st.error(result)

        st.markdown(
            "<div style='text-align:center;color:#718096;font-size:0.82rem;margin-top:16px'>"
            "Your data stays on your machine — no cloud, no tracking.</div>",
            unsafe_allow_html=True
        )


# ══════════════════════════════════════════════════════════════════════════════
# OWNER DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def show_owner():
    with st.sidebar:
        st.markdown("### 🏋️ Owner Panel")
        st.markdown("Logged in as **Rupali**")
        st.markdown("---")
        st.markdown("View all gym members, their calorie stats, meal logs, fitness goals, and leave notes.")
        st.markdown("---")
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.session_state.is_owner  = False
            st.session_state.user      = None
            st.rerun()

    st.markdown("<h1 class='header-title'>💪 GymCalor — Owner Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p class='header-sub'>Your complete view of every gym member</p>", unsafe_allow_html=True)

    all_users    = get_all_users()
    inactive     = get_inactive_users(days=3)
    inactive_ids = {u["id"] for u in inactive}

    tab_overview, tab_members, tab_inactive = st.tabs([
        "📊 Overview", "👥 All Members", "⚠️ Inactive Members"
    ])

    # ── OVERVIEW ──────────────────────────────────────────────────────────────
    with tab_overview:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Members",      len(all_users))
        c2.metric("Inactive (3+ days)", len(inactive))
        c3.metric("Active Today",       len(all_users) - len(inactive))
        gainers = sum(1 for u in all_users if u.get("goal_type") == "gain")
        c4.metric("Muscle Gainers 💪",  gainers)

        st.markdown("---")
        st.markdown("### 📋 Member Summary")

        if all_users:
            summary_data = []
            for u in all_users:
                try:
                    stats = get_user_stats(u["id"])
                except Exception:
                    stats = {}
                bmi = round(stats.get("bmi") or 0, 1)
                goal_label = "💪 Gain Muscle" if u.get("goal_type") == "gain" else "🔥 Lose Weight"
                summary_data.append({
                    "Name":                u["name"],
                    "Email":               u["email"],
                    "Fitness Goal":        goal_label,
                    "Calorie Goal":        f"{u.get('calorie_goal', 2000)} kcal",
                    "Avg Calories Burned": f"{round(stats.get('avg_calories') or 0, 1)} kcal",
                    "Total Sessions":      stats.get("total_sessions") or 0,
                    "BMI":                 bmi if bmi > 0 else "—",
                    "Meals Today (kcal)":  stats.get("meals_today") or 0,
                    "Status":              "⚠️ Inactive" if u["id"] in inactive_ids else "✅ Active"
                })
            if summary_data:
                st.dataframe(pd.DataFrame(summary_data), use_container_width=True)
        else:
            st.info("No members have signed up yet.")

    # ── ALL MEMBERS ───────────────────────────────────────────────────────────
    with tab_members:
        if not all_users:
            st.info("No members yet.")
        else:
            for u in all_users:
                try:
                    stats = get_user_stats(u["id"])
                except Exception:
                    stats = {}
                active  = u["id"] not in inactive_ids
                status_badge = "<span class='active-badge'>Active</span>" if active else "<span class='inactive-badge'>Inactive</span>"
                goal_badge   = "<span class='gain-badge'>💪 Gain Muscle</span>" if u.get("goal_type") == "gain" \
                               else "<span class='lose-badge'>🔥 Lose Weight</span>"
                bmi_val = round(stats.get("bmi") or 0, 1)

                with st.expander(f"👤  {u['name']}  —  {u['email']}"):
                    st.markdown(f"{status_badge} &nbsp; {goal_badge}", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)

                    col1, col2, col3, col4, col5 = st.columns(5)
                    col1.metric("Avg Burn",        f"{round(stats.get('avg_calories') or 0, 1)} kcal")
                    col2.metric("Sessions",         stats.get("total_sessions") or 0)
                    col3.metric("BMI",              bmi_val if bmi_val > 0 else "—")
                    col4.metric("Meals Today",      f"{stats.get('meals_today') or 0} kcal")
                    col5.metric("Calorie Goal",     f"{u.get('calorie_goal', 2000)} kcal")

                    # Tip based on goal
                    if u.get("goal_type") == "gain":
                        st.markdown(
                            "<div class='banner'>💡 This member is trying to <b>gain muscle</b>. "
                            "They should be eating above their calorie goal and focusing on strength training.</div>",
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            "<div class='banner'>💡 This member is trying to <b>lose weight</b>. "
                            "They should maintain a calorie deficit and focus on cardio + HIIT.</div>",
                            unsafe_allow_html=True
                        )

                    # Recent meals
                    meals = stats.get("recent_meals", [])
                    if meals:
                        st.markdown("**Recent Meal Logs:**")
                        meal_df = pd.DataFrame(meals)[["log_date", "meal_type", "food_name", "calories"]]
                        meal_df.columns = ["Date", "Meal", "Food", "Calories (kcal)"]
                        st.dataframe(meal_df, use_container_width=True)
                    else:
                        st.caption("No meals logged yet.")

                    st.markdown("---")

                    # Trainer notes
                    st.markdown("**📝 Notes for this Member:**")
                    notes = get_trainer_notes(u["id"])
                    if notes:
                        for n in notes:
                            cols = st.columns([10, 1])
                            with cols[0]:
                                st.markdown(
                                    f"<div class='note-card'>📌 {n['note']}"
                                    f"<br><small style='color:#718096'>{n['created_at']}</small></div>",
                                    unsafe_allow_html=True
                                )
                            with cols[1]:
                                if st.button("🗑", key=f"del_note_{n['id']}"):
                                    delete_trainer_note(n["id"])
                                    st.rerun()
                    else:
                        st.caption("No notes yet.")

                    new_note = st.text_area(
                        "Leave a note for this member:",
                        key=f"note_{u['id']}",
                        placeholder="e.g. Increase protein intake, great progress this week!"
                    )
                    if st.button("Save Note", key=f"save_{u['id']}"):
                        if new_note.strip():
                            add_trainer_note(u["id"], new_note.strip())
                            st.success("Note saved!")
                            st.rerun()
                        else:
                            st.warning("Note can't be empty.")

    # ── INACTIVE ──────────────────────────────────────────────────────────────
    with tab_inactive:
        if not inactive:
            st.success("All members have been active in the last 3 days 🎉")
        else:
            st.warning(f"{len(inactive)} member(s) haven't logged in for 3+ days.")
            for u in inactive:
                last = u.get("last_active") or "Never"
                st.markdown(
                    f"<div class='user-card'>👤 <b>{u['name']}</b> — {u['email']}"
                    f"<br><small style='color:#A0AEC0'>Last active: {last}</small></div>",
                    unsafe_allow_html=True
                )


# ══════════════════════════════════════════════════════════════════════════════
# USER APP
# ══════════════════════════════════════════════════════════════════════════════
def show_app():
    user    = st.session_state.user
    user_id = user["id"]

    goal, goal_type = get_calorie_goal(user_id)

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"### 👋 {user['name']}")
        h = user.get("height") or 1
        w = user.get("weight") or 0
        bmi_side = round(w / (h ** 2), 1) if h and w else "—"
        st.markdown(f"**BMI:** {bmi_side}")

        goal_label = "💪 Gain Muscle" if goal_type == "gain" else "🔥 Lose Weight"
        st.markdown(f"**Goal:** {goal_label}")
        st.markdown("---")

        st.markdown("**Update My Goal**")
        new_goal_type = st.selectbox(
            "Fitness Goal",
            ["lose", "gain"],
            index=0 if goal_type == "lose" else 1,
            format_func=lambda x: "🔥 Lose Weight / Burn Fat" if x == "lose" else "💪 Gain Muscle / Bulk Up",
            key="sidebar_goal_type"
        )
        new_goal = st.number_input(
            "Daily Calorie Goal (kcal)",
            min_value=500, max_value=6000,
            value=goal, step=50,
            key="sidebar_goal"
        )
        if st.button("Update Goal"):
            update_calorie_goal(user_id, new_goal, new_goal_type)
            st.success("Goal updated!")
            st.rerun()

        streak = get_streak(user_id)
        st.markdown("---")
        if streak > 0:
            st.markdown(f"🔥 **{streak}-day logging streak!**")
        else:
            st.markdown("Start logging meals to build your streak!")

        notes = get_trainer_notes(user_id)
        if notes:
            st.markdown("---")
            st.markdown("### 📌 Notes from your Trainer")
            for n in notes:
                st.markdown(
                    f"<div class='note-card'>{n['note']}"
                    f"<br><small style='color:#718096'>{n['created_at']}</small></div>",
                    unsafe_allow_html=True
                )

        st.markdown("---")
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.session_state.is_owner  = False
            st.session_state.user      = None
            st.session_state.history   = []
            st.rerun()

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown("<h1 class='header-title'>Gym Performance & Calories Predictor</h1>", unsafe_allow_html=True)
    st.markdown("<p class='header-sub'>Advanced Analytics Powered by Machine Learning</p>", unsafe_allow_html=True)

    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else ("Good afternoon" if hour < 17 else "Good evening")
    goal_msg = "Time to eat big and train hard 💪" if goal_type == "gain" else "Let's burn those calories 🔥"
    st.markdown(
        f"<div class='banner'>{greeting}, <b>{user['name']}</b>! {goal_msg}</div>",
        unsafe_allow_html=True
    )

    # Goal tip banner
    if goal_type == "gain":
        st.markdown(
            "<div class='banner' style='border-left-color:#3A86FF'>💡 <b>Muscle Gain Mode:</b> "
            "You should be eating <b>above</b> your calorie goal. "
            "Focus on protein-rich meals and strength/HIIT workouts.</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<div class='banner'>💡 <b>Weight Loss Mode:</b> "
            "Stay <b>below</b> your calorie goal. "
            "Cardio and HIIT workouts will help you burn the most calories.</div>",
            unsafe_allow_html=True
        )

    tab1, tab2, tab3 = st.tabs([
        "🚀 Predict Calories",
        "🍽️ Calorie Tracker",
        "📊 My History"
    ])

    # ── TAB 1: PREDICT ────────────────────────────────────────────────────────
    with tab1:
        st.markdown("### Athlete Profile & Workout Details")

        with st.form("prediction_form"):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**Personal Attributes**")
                age     = st.number_input("Age", min_value=15, max_value=100, value=user.get("age") or 25)
                gender  = st.selectbox("Gender", ["Male", "Female","Non-binary","Prefer not to say"])
                weight  = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=float(user.get("weight") or 70))
                height  = st.number_input("Height (m)", min_value=1.0, max_value=2.5, value=float(user.get("height") or 1.75))
                fat_pct = st.number_input("Body Fat Percentage (%)", min_value=3.0, max_value=50.0, value=15.0)

            with col2:
                st.markdown("**Heart Rate Metrics**")
                resting_bpm = st.number_input("Resting BPM", min_value=40, max_value=120, value=65)
                avg_bpm     = st.number_input("Average BPM", min_value=60, max_value=200, value=120)
                max_bpm     = st.number_input("Maximum BPM", min_value=80, max_value=220, value=160)

            with col3:
                st.markdown("**Workout Parameters**")
                workout_type     = st.selectbox("Workout Type", ["Cardio", "Strength", "Yoga", "HIIT"])
                session_duration = st.number_input("Session Duration (hours)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
                water_intake     = st.number_input("Water Intake (liters)", min_value=0.1, max_value=5.0, value=1.5, step=0.1)
                freq             = st.number_input("Workout Frequency (days/week)", min_value=1, max_value=7, value=3)
                exp_level        = st.selectbox(
                    "Experience Level", [1, 2, 3],
                    format_func=lambda x: {1: "1 - Beginner", 2: "2 - Intermediate", 3: "3 - Expert"}[x]
                )

            submit_btn = st.form_submit_button("🔥 Predict Calories Burned")

        if submit_btn:
            bmi = weight / (height ** 2)
            payload = {
                "Age": age, "Gender": gender, "Weight": weight, "Height": height,
                "Max_BPM": max_bpm, "Avg_BPM": avg_bpm, "Resting_BPM": resting_bpm,
                "Session_Duration": session_duration, "Workout_Type": workout_type,
                "Fat_Percentage": fat_pct, "Water_Intake": water_intake,
                "Workout_Frequency": freq, "Experience_Level": exp_level, "BMI": bmi
            }

            try:
                with st.spinner("Analyzing biometric data..."):
                    res = requests.post("http://localhost:8002/predict", json=payload)

                if res.status_code == 200:
                    prediction = res.json().get("predicted_calories_burned", 0)
                    save_prediction(user_id, payload, prediction)
                    st.success("Prediction generated successfully!")

                    st.markdown("### 🏆 Result")
                    res_col1, res_col2, res_col3 = st.columns(3)
                    with res_col1:
                        st.metric("Estimated Calories Burned", f"{prediction:.1f} kcal", delta="🔥")
                    with res_col2:
                        st.metric("Computed BMI", f"{bmi:.1f}",
                                  delta="normal" if 18.5 <= bmi <= 24.9 else "check status",
                                  delta_color="off")
                    with res_col3:
                        st.metric("Workout Intensity", f"{avg_bpm} BPM avg")

                    # Smart advice based on goal
                    km_equiv = round(prediction / 60, 1)
                    if goal_type == "gain":
                        st.markdown(
                            f"<div class='banner'>💪 You burned <b>{prediction:.0f} kcal</b>. "
                            f"Make sure to eat enough to stay in a surplus — your goal is <b>{goal} kcal/day</b>. "
                            f"That's equivalent to running {km_equiv} km!</div>",
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f"<div class='banner'>🔥 You burned <b>{prediction:.0f} kcal</b>. "
                            f"That's roughly like running <b>{km_equiv} km</b>! "
                            f"Stay under your <b>{goal} kcal</b> goal today.</div>",
                            unsafe_allow_html=True
                        )

                    # Save to session history too
                    record = payload.copy()
                    record["Predicted_Calories"] = prediction
                    record["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.history.append(record)

                else:
                    st.error(f"Error from backend: {res.text}")

            except Exception as e:
                st.error(f"Could not connect to backend API: {e}")

    # ── TAB 2: CALORIE TRACKER ────────────────────────────────────────────────
    with tab2:
        st.markdown("### 🍽️ Daily Calorie Tracker")
        goal, goal_type = get_calorie_goal(user_id)

        selected_date = st.date_input("Select Date", value=date.today())
        log_date_str  = selected_date.strftime("%Y-%m-%d")

        with st.expander("➕ Log a Meal", expanded=True):
            mc1, mc2, mc3, mc4 = st.columns([2, 3, 2, 1])
            with mc1:
                meal_type = st.selectbox("Meal", ["Breakfast", "Lunch", "Dinner", "Snack"], key="meal_type")
            with mc2:
                food_name = st.text_input("What did you eat?", placeholder="e.g. Rice and dal", key="food_name")
            with mc3:
                meal_cals = st.number_input("Calories (kcal)", min_value=1, max_value=3000, value=300, key="meal_cal")
            with mc4:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Add"):
                    if food_name.strip():
                        log_meal(user_id, meal_type, food_name.strip(), meal_cals, log_date_str)
                        st.success(f"Logged {food_name} — {meal_cals} kcal!")
                        st.rerun()
                    else:
                        st.warning("Please enter the food name.")

        meals       = get_meals_by_date(user_id, log_date_str)
        total_eaten = sum(m["calories"] for m in meals)

        st.markdown(f"#### Meals on {selected_date.strftime('%d %b %Y')}")
        if meals:
            for m in meals:
                mc1, mc2, mc3 = st.columns([6, 2, 1])
                with mc1:
                    st.markdown(f"🍴 **{m['meal_type']}** — {m['food_name']}")
                with mc2:
                    st.markdown(f"`{m['calories']} kcal`")
                with mc3:
                    if st.button("✕", key=f"del_meal_{m['id']}"):
                        delete_meal(m["id"])
                        st.rerun()
        else:
            st.caption("No meals logged for this date yet.")

        st.markdown("---")

        preds_today  = [p for p in get_user_predictions(user_id) if p["created_at"][:10] == log_date_str]
        burned_today = sum(p["predicted_calories"] for p in preds_today)
        net          = total_eaten - burned_today
        remaining    = goal - total_eaten

        st.markdown("#### Today's Calorie Summary")
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Eaten",             f"{total_eaten} kcal")
        s2.metric("Burned",            f"{burned_today:.0f} kcal")
        s3.metric("Net Balance",       f"{net:+.0f} kcal",
                  delta="Surplus" if net > 0 else "Deficit", delta_color="off")
        s4.metric("Goal",              f"{goal} kcal")

        # Smart status message based on goal
        if total_eaten == 0:
            st.info("Log your meals above to see your calorie balance.")
        elif goal_type == "gain":
            if total_eaten >= goal:
                st.success(f"Great job! You've hit your calorie goal for muscle gain — {total_eaten} kcal eaten 💪")
            else:
                still_needed = goal - total_eaten
                st.warning(f"You need {still_needed} more kcal to hit your muscle gain goal. Eat more! 🍗")
        else:
            if net < 0:
                st.success(f"You're in a calorie deficit of {abs(net):.0f} kcal — great work! 💪")
            elif net <= 200:
                st.info(f"You're close to balance. Net: {net:+.0f} kcal.")
            else:
                st.warning(f"You're {net:.0f} kcal over your goal. Consider a workout to burn it off!")

        # Weekly chart
        st.markdown("#### 📅 Last 7 Days — Calories Eaten")
        weekly = get_weekly_meals(user_id)
        if weekly:
            wdf = pd.DataFrame(weekly)
            wdf["log_date"] = pd.to_datetime(wdf["log_date"])
            wdf = wdf.sort_values("log_date")

            fig, ax = plt.subplots(figsize=(9, 3.5))
            bar_color = "#3A86FF" if goal_type == "gain" else "#FF4B2B"
            ax.bar(wdf["log_date"].dt.strftime("%d %b"), wdf["total_calories"],
                   color=bar_color, alpha=0.85, edgecolor="none", width=0.5)
            ax.axhline(goal, color="#FFB703", linewidth=1.8, linestyle="--",
                       label=f"{'Gain' if goal_type == 'gain' else 'Loss'} Goal: {goal} kcal")
            ax.set_facecolor("#0E1117"); fig.patch.set_facecolor("#0E1117")
            ax.tick_params(colors="white")
            ax.yaxis.label.set_color("white")
            ax.set_ylabel("Calories (kcal)", color="white")
            ax.legend(facecolor="#0E1117", edgecolor="#2D3748", labelcolor="white")
            for spine in ax.spines.values():
                spine.set_edgecolor("#2D3748")
            st.pyplot(fig)
            plt.close()
        else:
            st.caption("Log meals for a few days to see your weekly chart.")

    # ── TAB 3: HISTORY ────────────────────────────────────────────────────────
    with tab3:
        st.markdown("### 📈 Comprehensive Prediction History")

        if len(st.session_state.history) > 0:
            history_df = pd.DataFrame(st.session_state.history)

            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric("Total Sessions Simulated", len(history_df))
            with col_m2:
                st.metric("Average Calories Burned", f"{history_df['Predicted_Calories'].mean():.1f} kcal")
            with col_m3:
                st.metric("Highest Calorie Burn", f"{history_df['Predicted_Calories'].max():.1f} kcal")

            st.markdown("#### Trends & Distribution")
            chart_col1, chart_col2 = st.columns(2)

            with chart_col1:
                st.markdown("**Calories vs Session Duration**")
                fig, ax = plt.subplots(figsize=(6, 4))
                sns.scatterplot(data=history_df, x='Session_Duration', y='Predicted_Calories',
                                hue='Workout_Type', palette='YlOrRd', ax=ax, s=100)
                ax.set_facecolor('#0E1117'); fig.patch.set_facecolor('#0E1117')
                ax.tick_params(colors='white')
                ax.xaxis.label.set_color('white'); ax.yaxis.label.set_color('white')
                st.pyplot(fig)
                plt.close()

            with chart_col2:
                st.markdown("**Calorie Burn Distribution**")
                fig2, ax2 = plt.subplots(figsize=(6, 4))
                sns.histplot(data=history_df, x='Predicted_Calories', bins=10, kde=True,
                             color='#FF4B2B', ax=ax2)
                ax2.set_facecolor('#0E1117'); fig2.patch.set_facecolor('#0E1117')
                ax2.tick_params(colors='white')
                ax2.xaxis.label.set_color('white'); ax2.yaxis.label.set_color('white')
                st.pyplot(fig2)
                plt.close()

            st.markdown("#### Detailed Log")
            st.dataframe(
                history_df[['Timestamp', 'Workout_Type', 'Session_Duration', 'Avg_BPM', 'BMI', 'Predicted_Calories']]
                .style.format({'Predicted_Calories': '{:.1f}', 'BMI': '{:.1f}'}),
                use_container_width=True
            )

            if st.button("Clear History"):
                st.session_state.history = []
                st.rerun()
        else:
            st.info("No prediction history available yet. Go to the 'Predict Calories' tab to run some simulations!")


# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    show_auth()
elif st.session_state.is_owner:
    show_owner()
else:
    show_app()
