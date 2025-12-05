from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '').lower()
    
    if 'appointment' in user_message or 'book' in user_message:
        response = "To book an appointment, please call us at 555-0123 or visit our online portal."
    elif 'department' in user_message:
        response = "We have the following departments: Cardiology, Neurology, Pediatrics, and Orthopedics."
    elif 'doctor' in user_message:
        response = "Our top doctors are Dr. Smith (Cardiology), Dr. Jones (Neurology), and Dr. Brown (Pediatrics)."
    elif 'hour' in user_message or 'time' in user_message:
        response = "We are open 24/7 for emergencies. Outpatient clinics are open 8 AM to 5 PM, Monday to Friday."
    elif 'hello' in user_message or 'hi' in user_message:
        response = "Hello! I am the Medical Center Bot. How can I assist you today?"
    else:
        response = "I'm sorry, I didn't understand that. You can ask about appointments, departments, or doctors."
    
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
