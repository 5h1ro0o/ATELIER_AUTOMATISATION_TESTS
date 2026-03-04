import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'test_runs.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            api TEXT NOT NULL,
            total INTEGER NOT NULL,
            passed INTEGER NOT NULL,
            failed INTEGER NOT NULL,
            errors INTEGER NOT NULL,
            error_rate REAL NOT NULL,
            availability_pct REAL NOT NULL,
            latency_avg REAL NOT NULL,
            latency_p95 REAL NOT NULL,
            tests_json TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def save_run(report):
    init_db()
    conn = get_db()
    summary = report['summary']
    cursor = conn.execute('''
        INSERT INTO runs (timestamp, api, total, passed, failed, errors, 
                         error_rate, availability_pct, latency_avg, latency_p95, tests_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        report['timestamp'],
        report['api'],
        summary['total'],
        summary['passed'],
        summary['failed'],
        summary['errors'],
        summary['error_rate'],
        summary['availability_pct'],
        summary['latency_ms_avg'],
        summary['latency_ms_p95'],
        json.dumps(report['tests'])
    ))
    run_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return run_id

def get_latest_run():
    init_db()
    conn = get_db()
    row = conn.execute('SELECT * FROM runs ORDER BY id DESC LIMIT 1').fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def list_runs(limit=20):
    init_db()
    conn = get_db()
    rows = conn.execute('''
        SELECT id, timestamp, api, total, passed, failed, errors,
               error_rate, availability_pct, latency_avg, latency_p95
        FROM runs ORDER BY id DESC LIMIT ?
    ''', (limit,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_stats():
    init_db()
    conn = get_db()
    stats = conn.execute('''
        SELECT 
            COUNT(*) as total_runs,
            AVG(availability_pct) as avg_availability,
            AVG(latency_avg) as avg_latency
        FROM runs
    ''').fetchone()
    conn.close()
    return dict(stats) if stats else {}
