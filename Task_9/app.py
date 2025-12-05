from flask import Flask, request, jsonify, render_template
from sentence_transformers import SentenceTransformer, util
import torch

app = Flask(__name__)


print("Loading model... this may take a while on first run.")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        sentence1 = data.get('sentence1', '')
        sentence2 = data.get('sentence2', '')

        if not sentence1 or not sentence2:
            return jsonify({'error': 'Both sentences are required.'}), 400


        embeddings1 = model.encode(sentence1, convert_to_tensor=True)
        embeddings2 = model.encode(sentence2, convert_to_tensor=True)


        cosine_scores = util.cos_sim(embeddings1, embeddings2)
        score = cosine_scores.item()


        threshold = 0.7
        is_paraphrase = score >= threshold

        return jsonify({
            'similarity_score': round(score, 4),
            'is_paraphrase': is_paraphrase,
            'verdict': "Paraphrase Detected" if is_paraphrase else "Not a Paraphrase"
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
