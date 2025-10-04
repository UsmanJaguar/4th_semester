
from flask import Flask, render_template, request
import cv2

app = Flask(__name__)
UPLOAD_FOLDER = './images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

def analyze_face(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    traits = []

    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
        face_roi = gray[y:y+h, x:x+w]
        color_face_roi = image[y:y+h, x:x+w]
        
        eyes = eye_cascade.detectMultiScale(face_roi)
        eye_positions = [(ex, ey, ew, eh) for (ex, ey, ew, eh) in eyes]

        face_width = w
        forehead_height = int(h * 0.3)
        eye_size = sum([ew for _, _, ew, _ in eye_positions]) / len(eye_positions) if eye_positions else 0
        eye_distance = abs(eye_positions[0][0] - eye_positions[1][0]) if len(eye_positions) == 2 else 0

        personality = "Extroverted (Wide-set eyes)" if eye_distance > face_width * 0.3 else "Introverted (Close-set eyes)"

        traits.append({
            "face_width": face_width,
            "forehead_height": forehead_height,
            "eye_size": round(eye_size, 2),
            "eye_distance": eye_distance,
            "personality": personality
        })
    
    output_path = UPLOAD_FOLDER + 'processed_image.jpg'
    cv2.imwrite(output_path, image)
    return traits, output_path

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'image' not in request.files:
            return render_template('index.html', error='No file uploaded')
        file = request.files['image']
        if file.filename == '':
            return render_template('index.html', error='No file selected')
        filepath = UPLOAD_FOLDER + file.filename
        file.save(filepath)
        traits, processed_image = analyze_face(filepath)
        return render_template('index.html', traits=traits, processed_image=processed_image)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
