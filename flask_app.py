from flask import Flask, render_template, jsonify, redirect, url_for
import json
from datetime import datetime, timezone, timedelta

from tester.runner import run_all_tests
from storage import save_run, get_latest_run, list_runs, get_stats

app = Flask(__name__)

LAST_RUN_TIME = None
MIN_INTERVAL_SECONDS = 30
PARIS_TZ = timezone(timedelta(hours=1))

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/consignes')
def consignes():
    return render_template('consignes.html')

@app.route('/dashboard')
def dashboard():
    latest = get_latest_run()
    runs = list_runs(limit=10)
    tests = []
    if latest and latest.get('tests_json'):
        tests = json.loads(latest['tests_json'])
    return render_template('dashboard.html', latest=latest, tests=tests, runs=runs)

@app.route('/run')
def run_tests():
    global LAST_RUN_TIME
    now = datetime.now(PARIS_TZ)
    if LAST_RUN_TIME:
        elapsed = (now - LAST_RUN_TIME).total_seconds()
        if elapsed < MIN_INTERVAL_SECONDS:
            return jsonify({
                "error": f"Veuillez attendre {int(MIN_INTERVAL_SECONDS - elapsed)}s",
                "retry_after": int(MIN_INTERVAL_SECONDS - elapsed)
            }), 429
    LAST_RUN_TIME = now
    report = run_all_tests()
    save_run(report)
    return redirect(url_for('dashboard'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)