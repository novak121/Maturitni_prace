let timeLeft = 10;
        const timerElement = document.getElementById('timer');
        const acceptButton = document.getElementById('accept-btn');

        const countdown = setInterval(() => {
            if (timeLeft <= 0) {
                clearInterval(countdown);
                window.location.href = "{{ url_for('login') }}"; // Přesměrování na login
            } else {
                timerElement.innerHTML = `${timeLeft} sekund`;
            }
            timeLeft -= 1;
        }, 1000);

        acceptButton.addEventListener('click', () => {
            clearInterval(countdown);
            window.location.href = "{{ url_for('home') }}"; // Přesměrování na home
        });

        // timer 10s na qualification, pokud 10s vyprchá tak redirect na login