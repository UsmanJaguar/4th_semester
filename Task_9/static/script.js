document.addEventListener('DOMContentLoaded', () => {
    const checkBtn = document.getElementById('checkBtn');
    const sentence1Input = document.getElementById('sentence1');
    const sentence2Input = document.getElementById('sentence2');
    const resultCard = document.getElementById('result');
    const verdictText = document.getElementById('verdict');
    const scoreText = document.getElementById('score-text');
    const scoreCirclePath = document.getElementById('score-circle-path');
    const loader = document.getElementById('loader');
    const btnText = checkBtn.querySelector('span');

    checkBtn.addEventListener('click', async () => {
        const s1 = sentence1Input.value.trim();
        const s2 = sentence2Input.value.trim();

        if (!s1 || !s2) {
            alert('Please enter both sentences.');
            return;
        }

        // UI Loading State
        setLoading(true);
        resultCard.classList.add('hidden');
        resultCard.style.display = 'none';

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ sentence1: s1, sentence2: s2 }),
            });

            const data = await response.json();

            if (response.ok) {
                displayResult(data);
            } else {
                alert('Error: ' + (data.error || 'Something went wrong'));
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to connect to the server.');
        } finally {
            setLoading(false);
        }
    });

    function setLoading(isLoading) {
        if (isLoading) {
            checkBtn.disabled = true;
            loader.style.display = 'block';
            btnText.style.display = 'none';
        } else {
            checkBtn.disabled = false;
            loader.style.display = 'none';
            btnText.style.display = 'block';
        }
    }

    function displayResult(data) {
        resultCard.style.display = 'flex';
        // Small delay to allow display:flex to apply before removing hidden class for transition
        setTimeout(() => {
            resultCard.classList.remove('hidden');
        }, 10);

        const score = data.similarity_score;
        const percentage = Math.round(score * 100);
        const isParaphrase = data.is_paraphrase;

        // Update Text
        verdictText.textContent = data.verdict;
        scoreText.textContent = `${percentage}%`;

        // Update Colors based on result
        if (isParaphrase) {
            verdictText.style.color = 'var(--success-color)';
            scoreCirclePath.style.stroke = 'var(--success-color)';
        } else {
            verdictText.style.color = 'var(--error-color)';
            scoreCirclePath.style.stroke = 'var(--error-color)';
        }

        // Update Circle Progress
        // stroke-dasharray="current, total" where total is 100 for this viewBox setup logic (approx)
        // actually for this specific SVG path logic:
        // circumference = 2 * pi * r = 2 * 3.14159 * 15.9155 ≈ 100
        scoreCirclePath.style.strokeDasharray = `${percentage}, 100`;
    }
});
