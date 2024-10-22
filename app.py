from flask import Flask, render_template, send_file, jsonify
import qrcode
from io import BytesIO
import sqlite3
import time
import os

app = Flask(__name__)

# Create an SQLite database to store active links
def init_db():
    conn = sqlite3.connect('qrcodes.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS active_link (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            timestamp REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Function to update the active link in the database
def update_link(url):
    conn = sqlite3.connect('qrcodes.db')
    c = conn.cursor()
    timestamp = time.time()
    c.execute("DELETE FROM active_link")
    c.execute("INSERT INTO active_link (url, timestamp) VALUES (?, ?)", (url, timestamp))
    conn.commit()
    conn.close()

# Function to get the current active link and timestamp
def get_active_link():
    conn = sqlite3.connect('qrcodes.db')
    c = conn.cursor()
    c.execute("SELECT url, timestamp FROM active_link")
    row = c.fetchone()
    conn.close()
    if row:
        return row[0], row[1]
    return None, None

# Route to update the QR code with a new link
@app.route('/update_qr/<path:link>')
def update_qr(link):
    update_link(link)
    return jsonify({"message": "QR code updated!"})

# Route to generate and serve the QR code image, but only if it hasn't expired
@app.route('/get_qr')
def get_qr():
    url, timestamp = get_active_link()
    current_time = time.time()
    
    # Check if the QR code has expired
    if url and current_time - timestamp <= 15:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')
    
    # If the QR code has expired, return an error or a message
    return jsonify({"error": "QR code has expired!"})

# Route to handle expired QR codes
@app.route('/expired')
def expired():
    return "This QR code has expired!", 404

# Home route to render the page
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    init_db()
    # app.run(debug=True)
    
    # Get the port from the environment variable PORT
    port = int(os.environ.get('PORT', 5000))
    # Bind to '0.0.0.0' so the app is accessible externally
    app.run(host='0.0.0.0', port=port, debug=True)
