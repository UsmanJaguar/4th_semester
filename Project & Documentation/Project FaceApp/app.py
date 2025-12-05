from flask import Flask, render_template, request, jsonify, url_for
from werkzeug.utils import secure_filename
import os
import time
import traceback
import logging

from utils.face_utils import load_reference_encodings, process_image_file

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'processed')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

logging.basicConfig(level=logging.INFO)


# Load known face encodings from the `reference/` folder
known_encodings, known_names = load_reference_encodings(os.path.join(BASE_DIR, 'reference'))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    timestamp = int(time.time() * 1000)
    out_name = f"processed_{timestamp}_{filename}"
    out_path = os.path.join(app.config['UPLOAD_FOLDER'], out_name)

    try:
        # Process and annotate the image. Returns list of detected faces with names.
        faces = process_image_file(file, known_encodings, known_names, out_path)

        # Build URL for the processed image
        image_url = url_for('static', filename=f'processed/{out_name}')

        return jsonify({'image': image_url, 'faces': faces})
    except Exception as e:
        tb = traceback.format_exc()
        logging.error('Error processing upload: %s', tb)
        return jsonify({'error': 'Processing error', 'details': str(e), 'trace': tb}), 500


if __name__ == '__main__':
    # Run dev server
    app.run(host='0.0.0.0', port=5000, debug=True)
