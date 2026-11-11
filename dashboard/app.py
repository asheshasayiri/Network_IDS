import os
import csv
from flask import Flask, render_template, jsonify

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
FILE = os.path.join(BASE_DIR, "threat_log.csv")


# ─────────────────────────────────────────────
# LOAD CSV DATA
# ─────────────────────────────────────────────
def load_data():
    data = []

    if not os.path.exists(FILE):
        return data

    try:
        with open(FILE, "r") as f:
            reader = csv.DictReader(f)
            data = list(reader)
    except Exception as e:
        print("CSV ERROR:", e)

    return data[::-1]   # newest first


# ─────────────────────────────────────────────
# MAIN DASHBOARD
# ─────────────────────────────────────────────
@app.route("/")
def home():
    alerts = load_data()

    return render_template(
        "index.html",
        alerts=alerts,
        total=len(alerts)
    )


# ─────────────────────────────────────────────
# AUTO REFRESH API (USED BY JS FETCH)
# ─────────────────────────────────────────────
@app.route("/api/alerts")
def api_alerts():
    return jsonify(load_data())


# ─────────────────────────────────────────────
# RUN SERVER
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("🚀 IDS Dashboard running at http://127.0.0.1:5001")
    app.run(debug=True, port=5001, use_reloader=False)