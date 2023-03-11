import { query } from './utils.js';

const registerBtn = document.getElementById('register-btn');
registerBtn.addEventListener('click', async event => {
    event.preventDefault();

    try {
        const response = await window.fetch('/register', {
            headers: {
                "Content-type":"application/x-www-form-urlencoded",
            },
            method: "POST",
            body: 'username=' + document.getElementById('username').value
                  + '&' +
                  'password=' + document.getElementById('password1').value
                  + '&' +
                  'email=' + document.getElementById('email').value
        });
        const data = await response.json();
        console.log(data);
    } catch (error) {
        console.log(error);
    }
});

let inputValid = 0;
query('input').forEach((input, index) => {
    input.addEventListener('input', function() {
        const power = Math.pow(2, index);
        inputValid = this.value ? inputValid | power : inputValid ^ power;
        registerBtn.disabled = inputValid !== 15; // 1111
    });
});
