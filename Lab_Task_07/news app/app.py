from flask import Flask, render_template, request
import requests
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    url = "https://newsapi.org/v2/everything?q=tesla&from=2025-02-18&sortBy=publishedAt&apiKey=ee31c50e71c04d4fa703da4f3b53b62e"
    
    try:
        response = requests.get(url)
        news_data = response.json()
        
        if news_data.get("status") == "ok":
            articles = news_data.get("articles", [])
        else:
            articles = []
        
        # Format the publish date for each article
        for article in articles:
            if article.get("publishedAt"):
                date_obj = datetime.strptime(article["publishedAt"], "%Y-%m-%dT%H:%M:%SZ")
                article["formatted_date"] = date_obj.strftime("%B %d, %Y")
            else:
                article["formatted_date"] = "Unknown date"
                
    except Exception as e:
        print(f"Error fetching news: {e}")
        articles = []

    return render_template('index.html', articles=articles)

if __name__ == '__main__':
    app.run(debug=True)
