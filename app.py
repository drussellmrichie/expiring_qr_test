import os
import qrcode
import time
from flask import Flask, render_template, request, redirect, url_for
from io import BytesIO
import base64

app = Flask(__name__)

# Store the current URL and expiration details
current_url = None
qr_codes = []  # List to store generated QR codes with expiration times

def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{img_str}"

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    global current_url
    if request.method == 'POST':
        current_url = request.form['url']  # Admin submits a new URL
        generate_new_qr_code(current_url)  # Generate a new QR code immediately
        return redirect(url_for('admin'))  # Refresh the page after submission
    return render_template('admin.html')

def generate_new_qr_code(url):
    expiration_time = time.time() + 15  # Set expiration time for 15 seconds from now
    qr_code = generate_qr_code(url)
    qr_codes.append((qr_code, expiration_time))  # Store QR code and its expiration time

@app.route('/')
def index():
    global qr_codes

    # Remove expired QR codes
    current_time = time.time()
    qr_codes = [(code, exp) for code, exp in qr_codes if exp > current_time]

    # Generate a new QR code if no valid QR codes exist
    if not qr_codes:
        return "No valid QR code available. Please check back later."

    # Get the latest valid QR code
    latest_qr_code = qr_codes[-1][0]  # Get the last valid QR code

    return render_template('index.html', qr_code=latest_qr_code)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
