document.addEventListener('DOMContentLoaded', function() {
    
    // 1. СОРТИРОВКА ПЕДАГОГОВ
    const select = document.getElementById("sort-teachers");
    const container = document.getElementById("teachers-list");
    if (select && container) {
        const originalCards = Array.from(container.querySelectorAll(".card"));
        select.addEventListener("change", function() {
            const sortBy = select.value;
            let sortedCards = [...originalCards];
            if (sortBy === "name") {
                sortedCards.sort((a, b) => a.getAttribute("data-name").localeCompare(b.getAttribute("data-name"), 'ru'));
            } else if (sortBy === "subject") {
                sortedCards.sort((a, b) => a.getAttribute("data-subject").localeCompare(b.getAttribute("data-subject"), 'ru'));
            }
            container.innerHTML = "";
            sortedCards.forEach(card => container.appendChild(card));
        });
    }

    // 2. ОТПРАВКА ФОРМЫ НА СЕРВЕР
    const form = document.querySelector('.zayav-form');
    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault(); 
            
            // Берем логин из памяти браузера
            const username = localStorage.getItem('username'); 
            
            if (!username) {
                alert('Пожалуйста, сначала войдите в личный кабинет!');
                window.location.href = 'register.html'; 
                return;
            }

            const fio = document.getElementById('fio').value;
            const email = document.getElementById('email').value;
            const napravlenie = document.getElementById('napravlenie').value;
            const message = document.getElementById('message').value;

            const fullMessage = `ФИО: ${fio}, Email: ${email}, Направление: ${napravlenie}. Сообщение: ${message}`;

            fetch('http://127.0.0.1:8000/applications', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    teacher_id: 1,
                    message: fullMessage,
                    username: username 
                })
            })
            .then(response => response.json())
            .then(data => {
                alert('Ура! ' + data.message);
                form.reset(); 
            })
            .catch(error => {
                alert('Ошибка: не удалось связаться с сервером. Проверьте, запущен ли main.py!');
            });
        });
    }
});

// 3. ВЫВОД СВОИХ ЗАЯВОК
function showMyApps() {
    const username = localStorage.getItem('username');
    if (!username) {
        alert("Пожалуйста, сначала войдите в систему!");
        window.location.href = 'register.html';
        return;
    }

    const list = document.getElementById('my-apps-list');
    list.innerHTML = 'Загрузка...';
    
    fetch(`http://127.0.0.1:8000/my-applications?username=${username}`)
        .then(res => res.json())
        .then(data => {
            list.innerHTML = '';
            if (data.length === 0) {
                list.innerHTML = '<p>У вас пока нет заявок.</p>';
                return;
            }
            data.forEach(app => {
                list.innerHTML += `
                    <div style="background: white; padding: 10px; margin-bottom: 10px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); color: #333;">
                        <strong>Заявка:</strong> ${app.message} <br>
                        <small style="color: #666;">Дата: ${app.date}</small>
                    </div>
                `;
            });
        })
        .catch(error => {
            list.innerHTML = '<p style="color: red;">Ошибка загрузки. Сервер выключен?</p>';
        });
}