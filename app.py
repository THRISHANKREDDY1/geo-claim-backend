import os, sqlite3
import random
from datetime import datetime
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def init_db():
    conn = sqlite3.connect('claims.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, phone TEXT, crop TEXT,
            location TEXT, image_path TEXT,
            timestamp TEXT, verified TEXT
        )
    ''')
    conn.commit(); conn.close()

def verify_image(image_path):
    # Simulate ML: 70% chance valid
    return "valid" if random.random() < 0.7 else "invalid"

@app.route('/upload', methods=['POST'])
def upload_claim():
    name = request.form['name']
    phone = request.form['phone']
    crop = request.form['crop']
    location = request.form['location']
    image = request.files['image']

    filename = secure_filename(image.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(filepath)

    verified = verify_image(filepath)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect('claims.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO claims (name, phone, crop, location, image_path, timestamp, verified)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, phone, crop, location, filepath, timestamp, verified))
    conn.commit(); conn.close()

    return jsonify({"status":"success", "verified":verified})

@app.route('/claims', methods=['GET'])
def get_claims():
    conn = sqlite3.connect('claims.db')
    c = conn.cursor()
    c.execute('SELECT * FROM claims')
    rows = c.fetchall()
    conn.close()

    data = [{
        "id": r[0], "name": r[1], "phone": r[2], "crop": r[3],
        "location": r[4], "image_path": r[5], "timestamp": r[6],
        "verified": r[7]
    } for r in rows]
    return jsonify(data)
@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "Backend is working ✅"})
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
