from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import date, datetime
import os, sqlite3

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "development-only-change-me")
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tourism.db")

# Illustrative baseline assumptions, NOT live or verified crowd measurements.
PLACES = {
    "Goa Beach": {"city":"Goa","image":"goa.jpg","description":"A coastal destination known for beaches and seasonal tourism.","baseline":34},
    "Taj Mahal": {"city":"Agra","image":"tajmahal.jpg","description":"A world-famous heritage monument in Agra.","baseline":78},
    "Gateway of India": {"city":"Mumbai","image":"gateway.jpg","description":"A landmark on Mumbai's waterfront.","baseline":61},
    "Lonavala": {"city":"Lonavala","image":"lonavala.jpg","description":"A hill station popular for viewpoints and weekend trips.","baseline":43},
    "Shaniwar Wada": {"city":"Pune","image":"shaniwarwada.jpg","description":"A historic fortification and heritage attraction in Pune.","baseline":52},
}
SLOTS = {
    "06:00":("6 AM – 8 AM",-18), "08:00":("8 AM – 10 AM",-12),
    "10:00":("10 AM – 12 PM",8), "12:00":("12 PM – 2 PM",15),
    "14:00":("2 PM – 4 PM",12), "16:00":("4 PM – 6 PM",-3),
    "18:00":("6 PM – 8 PM",4),
}

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, destination TEXT NOT NULL,
            visit_date TEXT NOT NULL, time_slot TEXT NOT NULL,
            crowd_percent INTEGER NOT NULL, crowd_level TEXT NOT NULL,
            created_at TEXT NOT NULL)""")

def category(p):
    return "Low Crowd" if p < 35 else "Medium Crowd" if p < 70 else "High Crowd"

def estimate(place, date_text, slot):
    day = datetime.strptime(date_text, "%Y-%m-%d").date()
    value = PLACES[place]["baseline"] + SLOTS[slot][1]
    if day.weekday() >= 5:
        value += 12
    if day.month in (4, 5, 10, 11, 12):
        value += 5
    # Deterministic adjustment; no random values.
    value += (sum(map(ord, place + date_text + slot)) % 7) - 3
    return max(5, min(98, value))

def day_estimates(place, date_text):
    return [(estimate(place, date_text, k), label, k) for k, (label, _) in SLOTS.items()]

@app.route("/")
def home():
    return render_template("index.html", places=PLACES, today=date.today().isoformat(), slots=SLOTS)

@app.route("/predict", methods=["POST"])
def predict():
    place = request.form.get("place", "").strip()
    visit_date = request.form.get("visit_date", "")
    slot = request.form.get("time_slot", "08:00")
    if place not in PLACES:
        flash("Please select a supported destination.", "error")
        return redirect(url_for("home"))
    try:
        chosen = datetime.strptime(visit_date, "%Y-%m-%d").date()
        if chosen < date.today():
            raise ValueError
    except ValueError:
        flash("Choose a valid date that is today or in the future.", "error")
        return redirect(url_for("home"))
    if slot not in SLOTS:
        slot = "08:00"
    pct = estimate(place, visit_date, slot)
    level = category(pct)
    options = sorted(day_estimates(place, visit_date))
    best_pct, best_label, _ = options[0]
    recommendation = (f"Selected slot: {pct}% estimated intensity. "
                      f"The lowest estimated slot on this date is {best_label} ({best_pct}%).")
    with db() as conn:
        conn.execute("""INSERT INTO predictions
          (destination, visit_date, time_slot, crowd_percent, crowd_level, created_at)
          VALUES (?, ?, ?, ?, ?, ?)""",
          (place, visit_date, slot, pct, level, datetime.now().isoformat(timespec="seconds")))
    estimates = day_estimates(place, visit_date)
    return render_template("result.html", place=place, info=PLACES[place],
        visit_date=visit_date, selected_time=SLOTS[slot][0], crowd=level,
        percentage=pct, recommendation=recommendation, best_time=best_label,
        best_percentage=best_pct, chart_labels=[x[1] for x in estimates],
        chart_values=[x[0] for x in estimates])

@app.route("/dashboard")
def dashboard():
    with db() as conn:
        rows = conn.execute("SELECT * FROM predictions ORDER BY id DESC LIMIT 100").fetchall()
        total = conn.execute("SELECT COUNT(*) n FROM predictions").fetchone()["n"]
        avg = conn.execute("SELECT AVG(crowd_percent) a FROM predictions").fetchone()["a"]
        destinations = conn.execute("SELECT destination, COUNT(*) n FROM predictions GROUP BY destination ORDER BY n DESC").fetchall()
    return render_template("dashboard.html", rows=rows, total=total, average=round(avg or 0), destinations=destinations)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/health")
def health():
    return {"status":"ok", "destinations":len(PLACES)}

init_db()
if __name__ == "__main__":
    app.run(debug=True)
