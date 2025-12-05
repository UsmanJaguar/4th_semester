document.addEventListener('DOMContentLoaded', () => {
    const cityInput = document.getElementById('city-input');
    const searchBtn = document.getElementById('search-btn');
    const weatherContainer = document.getElementById('weather-container');
    const errorMessage = document.getElementById('error-message');
    const loading = document.getElementById('loading');

    // Elements to update
    const cityNameEl = document.getElementById('city-name');
    const tempEl = document.getElementById('temperature');
    const conditionEl = document.getElementById('condition');
    const windEl = document.getElementById('wind-speed');

    // Weather codes mapping (WMO Weather interpretation codes (WW))
    const weatherCodes = {
        0: 'Clear sky',
        1: 'Mainly clear', 2: 'Partly cloudy', 3: 'Overcast',
        45: 'Fog', 48: 'Depositing rime fog',
        51: 'Light drizzle', 53: 'Moderate drizzle', 55: 'Dense drizzle',
        61: 'Slight rain', 63: 'Moderate rain', 65: 'Heavy rain',
        71: 'Slight snow', 73: 'Moderate snow', 75: 'Heavy snow',
        77: 'Snow grains',
        80: 'Slight rain showers', 81: 'Moderate rain showers', 82: 'Violent rain showers',
        85: 'Slight snow showers', 86: 'Heavy snow showers',
        95: 'Thunderstorm', 96: 'Thunderstorm with slight hail', 99: 'Thunderstorm with heavy hail'
    };

    searchBtn.addEventListener('click', () => {
        const city = cityInput.value.trim();
        if (city) {
            fetchWeather(city);
        }
    });

    cityInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const city = cityInput.value.trim();
            if (city) {
                fetchWeather(city);
            }
        }
    });

    async function fetchWeather(city) {
        // Reset UI
        weatherContainer.classList.add('hidden');
        errorMessage.classList.add('hidden');
        loading.classList.remove('hidden');

        try {
            const response = await fetch(`/api/weather?city=${encodeURIComponent(city)}`);
            const data = await response.json();

            loading.classList.add('hidden');

            if (response.ok) {
                updateUI(data);
            } else {
                showError(data.error || 'Failed to fetch weather data');
            }
        } catch (error) {
            loading.classList.add('hidden');
            showError('Network error. Please try again.');
        }
    }

    function updateUI(data) {
        cityNameEl.textContent = `${data.city}, ${data.country}`;
        tempEl.textContent = Math.round(data.current.temperature);

        const code = data.current.weathercode;
        conditionEl.textContent = weatherCodes[code] || 'Unknown';

        windEl.textContent = data.current.windspeed;

        weatherContainer.classList.remove('hidden');

        // Dynamic background update could go here based on weather code
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove('hidden');
    }
});
