document.addEventListener("DOMContentLoaded", () => {
    const logregBox = document.querySelector('.logreg-box');

    document.body.addEventListener('click', (e) => {
        if (e.target.classList.contains('register-link')) {
            e.preventDefault();
            logregBox.classList.add('active');
        }
        if (e.target.classList.contains('login-link')) {
            e.preventDefault();
            logregBox.classList.remove('active');
        }
    });
});
