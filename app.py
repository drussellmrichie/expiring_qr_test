import os
import qrcode
import time
from flask import Flask, render_template, request, redirect, url_for
from io import BytesIO
from PIL import Image
import base64

app = Flask(__name__)

# Store the current URL
current_url = None
last_generation_time = 0

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
        return redirect(url_for('admin'))  # Refresh the page after submission
    return render_template('admin.html')

@app.route('/')
def index():
    global current_url, last_generation_time

    if current_url is None:
        return "No URL has been set by the administrator."

    # Generate a new QR code if 15 seconds have passed
    current_time = time.time()
    if current_time - last_generation_time >= 15:
        last_generation_time = current_time
        qr_code = generate_qr_code(current_url)
    else:
        qr_code = generate_qr_code(current_url)  # Keep the same code for 15 seconds

    return render_template('index.html', qr_code=qr_code)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
