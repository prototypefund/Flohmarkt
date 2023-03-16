import { postForm } from "./utils.js";

document.getElementById('login-btn').addEventListener('click', async event => {
    event.preventDefault();

    const loginForm = document.getElementById('login-form');
    postForm(loginForm)
    .then(data => {
        if (typeof(data) === 'string') {
            window.sessionStorage.setItem('token', data);
            window.location.pathname = '/~' + loginForm.querySelector('input').value;
        }
        else {
            window.alert('no valid login');
        }
    });
});
