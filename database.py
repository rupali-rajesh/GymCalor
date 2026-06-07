import sqlite3
import bcrypt
from datetime import datetime, date, timedelta

DB_PATH = "gymcalor.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    # Users table — goal_type: "lose" or "gain"
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            age INTEGER,
            weight REAL,
            height REAL,
            calorie_goal INTEGER DEFAULT 2000,
            goal_type TEXT DEFAULT 'lose',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Predictions
    c.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            age INTEGER,
            gender TEXT,
            weight REAL,
            height REAL,
            bmi REAL,
            max_bpm REAL,
            avg_bpm REAL,
            resting_bpm REAL,
            session_duration REAL,
            workout_type TEXT,
            fat_percentage REAL,
            water_intake REAL,
            workout_frequency INTEGER,
            experience_level INTEGER,
            predicted_calories REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Meal logs
    c.execute("""
        CREATE TABLE IF NOT EXISTS meal_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            meal_type TEXT,
            food_name TEXT,
            calories INTEGER,
            log_date TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Trainer notes
    c.execute("""
        CREATE TABLE IF NOT EXISTS trainer_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            note TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# ── Auth ──────────────────────────────────────────────────────────────────────

def register_user(name, email, password, age=None, weight=None, height=None,
                  calorie_goal=2000, goal_type="lose"):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE email = ?", (email,))
    if c.fetchone():
        conn.close()
        return False, "An account with this email already exists."
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    c.execute(
        """INSERT INTO users
           (name, email, password, age, weight, height, calorie_goal, goal_type)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (name, email, hashed, age, weight, height, calorie_goal, goal_type)
    )
    conn.commit()
    user_id = c.lastrowid
    conn.close()
    return True, user_id


def login_user(email, password):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    if not user:
        return False, None, "No account found with this email."
    if bcrypt.checkpw(password.encode(), user["password"].encode()):
        return True, dict(user), "Welcome back!"
    return False, None, "Incorrect password."


# ── Predictions ───────────────────────────────────────────────────────────────

def save_prediction(user_id, data, predicted_calories):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO predictions
        (user_id, age, gender, weight, height, bmi, max_bpm, avg_bpm, resting_bpm,
         session_duration, workout_type, fat_percentage, water_intake,
         workout_frequency, experience_level, predicted_calories, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, data["Age"], data["Gender"], data["Weight"], data["Height"],
        data["BMI"], data["Max_BPM"], data["Avg_BPM"], data["Resting_BPM"],
        data["Session_Duration"], data["Workout_Type"], data["Fat_Percentage"],
        data["Water_Intake"], data["Workout_Frequency"], data["Experience_Level"],
        predicted_calories, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()


def get_user_predictions(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM predictions WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


# ── Meal logs ─────────────────────────────────────────────────────────────────

def log_meal(user_id, meal_type, food_name, calories, log_date):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO meal_logs (user_id, meal_type, food_name, calories, log_date) VALUES (?, ?, ?, ?, ?)",
        (user_id, meal_type, food_name, calories, log_date)
    )
    conn.commit()
    conn.close()


def get_meals_by_date(user_id, log_date):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM meal_logs WHERE user_id = ? AND log_date = ? ORDER BY created_at",
        (user_id, log_date)
    )
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_weekly_meals(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT log_date, SUM(calories) as total_calories
        FROM meal_logs WHERE user_id = ?
        GROUP BY log_date ORDER BY log_date DESC LIMIT 7
    """, (user_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def delete_meal(meal_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM meal_logs WHERE id = ?", (meal_id,))
    conn.commit()
    conn.close()


def get_streak(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT DISTINCT log_date FROM meal_logs WHERE user_id = ? ORDER BY log_date DESC",
        (user_id,)
    )
    dates = [r["log_date"] for r in c.fetchall()]
    conn.close()
    if not dates:
        return 0
    streak = 0
    check = date.today()
    for d in dates:
        logged = datetime.strptime(d, "%Y-%m-%d").date()
        if logged == check or logged == check - timedelta(days=streak):
            streak += 1
            check = logged - timedelta(days=1)
        else:
            break
    return streak


# ── Calorie goal ──────────────────────────────────────────────────────────────

def update_calorie_goal(user_id, goal, goal_type):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "UPDATE users SET calorie_goal = ?, goal_type = ? WHERE id = ?",
        (goal, goal_type, user_id)
    )
    conn.commit()
    conn.close()


def get_calorie_goal(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT calorie_goal, goal_type FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return row["calorie_goal"], row["goal_type"]
    return 2000, "lose"


# ── Admin ─────────────────────────────────────────────────────────────────────

def get_all_users():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT id, name, email, age, weight, height, calorie_goal, goal_type, created_at
        FROM users ORDER BY created_at DESC
    """)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_user_stats(user_id):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        SELECT AVG(predicted_calories) as avg_calories,
               MAX(predicted_calories) as max_calories,
               COUNT(*) as total_sessions
        FROM predictions WHERE user_id = ?
    """, (user_id,))
    stats = dict(c.fetchone())

    c.execute("""
        SELECT bmi, weight, height, age
        FROM predictions WHERE user_id = ?
        ORDER BY created_at DESC LIMIT 1
    """, (user_id,))
    latest = c.fetchone()
    if latest:
        stats.update(dict(latest))

    c.execute(
        "SELECT MAX(created_at) as last_active FROM predictions WHERE user_id = ?",
        (user_id,)
    )
    last = c.fetchone()
    stats["last_active"] = last["last_active"] if last else None

    today = datetime.now().strftime("%Y-%m-%d")
    c.execute(
        "SELECT SUM(calories) as meals_today FROM meal_logs WHERE user_id = ? AND log_date = ?",
        (user_id, today)
    )
    m = c.fetchone()
    stats["meals_today"] = m["meals_today"] if m and m["meals_today"] else 0

    c.execute("""
        SELECT log_date, food_name, meal_type, calories FROM meal_logs
        WHERE user_id = ? ORDER BY log_date DESC LIMIT 20
    """, (user_id,))
    stats["recent_meals"] = [dict(r) for r in c.fetchall()]

    conn.close()
    return stats


def get_inactive_users(days=3):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT u.id, u.name, u.email, MAX(p.created_at) as last_active
        FROM users u
        LEFT JOIN predictions p ON u.id = p.user_id
        GROUP BY u.id
        HAVING last_active IS NULL OR last_active < datetime('now', ?)
    """, (f"-{days} days",))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


# ── Trainer notes ─────────────────────────────────────────────────────────────

def add_trainer_note(user_id, note):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO trainer_notes (user_id, note, created_at) VALUES (?, ?, ?)",
        (user_id, note, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()


def get_trainer_notes(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM trainer_notes WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    )
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def delete_trainer_note(note_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM trainer_notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()
