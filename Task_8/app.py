from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/weather', methods=['GET'])
def get_weather():
    city = request.args.get('city')
    if not city:
        return jsonify({'error': 'City is required'}), 400


    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
    try:
        geo_response = requests.get(geo_url)
        geo_data = geo_response.json()
        
        if not geo_data.get('results'):
            return jsonify({'error': 'City not found'}), 404
            
        location = geo_data['results'][0]
        lat = location['latitude']
        lon = location['longitude']
        city_name = location['name']
        country = location.get('country', '')

        # 2. Weather Data
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=auto"
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()

        return jsonify({
            'city': city_name,
            'country': country,
            'current': weather_data['current_weather'],
            'daily': weather_data.get('daily', {})
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
