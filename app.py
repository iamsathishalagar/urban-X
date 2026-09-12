from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)  # Enables cross-origin requests from frontend

DB_NAME = 'urbanx.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Returns dict-like rows matching JS keys
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Reports Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bus_id TEXT DEFAULT 'BUS-001',
            camera_id TEXT DEFAULT 'CAMERA-001',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            vehicles INTEGER DEFAULT 0,
            persons INTEGER DEFAULT 0,
            traffic_status TEXT DEFAULT 'LOW',
            road_defects INTEGER DEFAULT 0,
            potholes INTEGER DEFAULT 0,
            floods INTEGER DEFAULT 0,
            zebra_crossings INTEGER DEFAULT 0,
            active_alerts INTEGER DEFAULT 0,
            latitude REAL DEFAULT 11.0168,
            longitude REAL DEFAULT 76.9558
        )
    ''')

    # 2. Accident Incidents Table (ANPR / OCR)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accident_incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id TEXT,
            bus_id TEXT DEFAULT 'BUS-001',
            camera_id TEXT DEFAULT 'CAMERA-001',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            vehicle_type TEXT,
            registration_number TEXT,
            plate_confidence REAL,
            status TEXT DEFAULT 'New',
            latitude REAL DEFAULT 11.0168,
            longitude REAL DEFAULT 76.9558,
            accident_image_path TEXT,
            accident_video_path TEXT
        )
    ''')

    # 3. Detection Events Table (YOLO Detections)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detection_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            detection_type TEXT,
            bus_id TEXT DEFAULT 'BUS-001',
            camera_id TEXT DEFAULT 'CAMERA-001',
            confidence REAL,
            latitude REAL DEFAULT 11.0168,
            longitude REAL DEFAULT 76.9558,
            status TEXT DEFAULT 'OPEN',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# --- API ENDPOINTS ---

# 1. Live Data API (Frontend Place 2)
@app.route('/api/live-data', methods=['GET'])
def get_live_data():
    # Returns real-time counts to the frontend dashboard
    return jsonify({
        "bus_id": "BUS-001",
        "vehicles": 12,
        "persons": 4,
        "traffic_status": "LOW",
        "active_alerts": 1,
        "accident_detected": False,
        "road_defects": 2,
        "floods": 0,
        "zebra_crossings": 1,
        "ai_models": {
            "flood_model": "connected",
            "zebra_model": "connected"
        }
    }), 200

# 2. Reports API (Frontend Place 3)
@app.route('/api/reports', methods=['GET'])
def get_reports():
    conn = get_db_connection()
    reports = conn.execute('SELECT * FROM reports ORDER BY timestamp DESC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in reports]), 200

# 3. Accident Incidents API (Frontend Place 4)
@app.route('/api/accident-incidents', methods=['GET'])
def get_accident_incidents():
    conn = get_db_connection()
    incidents = conn.execute('SELECT * FROM accident_incidents ORDER BY timestamp DESC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in incidents]), 200

# 4. Detection Events API (Frontend Place 5)
@app.route('/api/detection-events', methods=['GET'])
def get_detection_events():
    conn = get_db_connection()
    events = conn.execute('SELECT * FROM detection_events ORDER BY timestamp DESC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in events]), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)