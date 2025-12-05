from flask import Flask, render_template, request, jsonify
from hadith_bot import get_similar_hadith

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query = data.get('query')
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    results = get_similar_hadith(query)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
