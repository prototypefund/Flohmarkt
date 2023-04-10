import { postForm } from "./utils.js";

function parse_jwt (token) {
    var base64Url = token.split('.')[1];
    var base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    var jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    return jsonPayload;
}

document.getElementById('login-btn').addEventListener('click', async event => {
    event.preventDefault();

    const loginForm = document.getElementById('login-form');
    postForm(loginForm)
    .then(data => {
        if (typeof(data) === 'string') {
            window.sessionStorage.setItem('token', data);
            window.sessionStorage.setItem('parsedToken', parse_jwt(data));
            window.sessionStorage.setItem('test', {"lol":"lal"});
            window.location.pathname = '/~' + loginForm.querySelector('input').value;
        }
        else {
            window.alert('no valid login');
        }
    });
});
