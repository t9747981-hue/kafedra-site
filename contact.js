document.addEventListener('DOMContentLoaded', function() {
    
    // ===== 1. ВАЛИДАЦИЯ ФОРМЫ =====
    const form = document.getElementById('contact-form');
    const successMsg = document.getElementById('contact-success');

    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            let isValid = true;

            // Очищаем старые ошибки
            document.querySelectorAll('.error-message').forEach(el => el.textContent = '');
            document.querySelectorAll('.contact-form input, .contact-form textarea').forEach(el => el.classList.remove('invalid'));

            // Проверка имени
            const name = document.getElementById('contact-name');
            if (name.value.trim() === '') {
                document.getElementById('error-name').textContent = 'Пожалуйста, введите имя';
                name.classList.add('invalid');
                isValid = false;
            }

            // Проверка email
            const email = document.getElementById('contact-email');
            const emailPattern = /^[^ ]+@[^ ]+\.[a-z]{2,3}$/;
            if (email.value.trim() === '') {
                document.getElementById('error-email').textContent = 'Пожалуйста, введите email';
                email.classList.add('invalid');
                isValid = false;
            } else if (!emailPattern.test(email.value)) {
                document.getElementById('error-email').textContent = 'Введите корректный email (пример: name@mail.ru)';
                email.classList.add('invalid');
                isValid = false;
            }

            // Проверка текста
            const text = document.getElementById('contact-text');
            if (text.value.trim() === '') {
                document.getElementById('error-text').textContent = 'Напишите ваш вопрос';
                text.classList.add('invalid');
                isValid = false;
            }

            // Если всё верно
            if (isValid) {
                successMsg.style.display = 'block';
                form.reset();
                setTimeout(() => { successMsg.style.display = 'none'; }, 5000);
            }
        });
    }

    // ===== 2. ЗАПРОС ПОГОДЫ ЧЕРЕЗ API =====
    const loadingEl = document.getElementById('weather-loading');
    const errorEl = document.getElementById('weather-error');
    const resultEl = document.getElementById('weather-result');

    // Координаты (например, Москва)
    const lat = 55.75; 
    const lon = 37.61; 

    fetch(`https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true`)
        .then(response => {
            if (!response.ok) throw new Error('Ошибка сети');
            return response.json();
        })
        .then(data => {
            loadingEl.style.display = 'none';
            resultEl.style.display = 'block';
            document.getElementById('weather-temp').textContent = data.current_weather.temperature;
            document.getElementById('weather-wind').textContent = data.current_weather.windspeed;
        })
        .catch(error => {
            loadingEl.style.display = 'none';
            errorEl.style.display = 'block';
            console.error('Ошибка загрузки погоды:', error);
        });
});