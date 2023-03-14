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
                  'password=' + document.getElementById('password').value
                  + '&' +
                  'email=' + document.getElementById('email').value
        });
        const data = await response.json();
        console.log(data);
        window.location.pathname = '/registered';
    } catch (error) {
        console.log(error);
    }
});

let inputValid = 0,
    password;
query('.register input').forEach((input, index) => {
    input.addEventListener('input', function() {
        let valid;
        switch (this.id) {
            case 'username':
                valid = this.value !== '';
                break;
            case 'email':
                valid = /^\S+@\S+\.\S+$/.test(this.value); // https://stackoverflow.com/a/9204568/5764676
                break;
            case 'password':
                valid = this.value !== '';
                password = this.value;
                break;
            case 'password-repeat':
                valid = this.value === password;
                break;
        }
        const mask = 1 << index;
        inputValid = valid ? inputValid | mask : inputValid & ~mask;
        registerBtn.disabled = inputValid !== 15; // 1111
    });
});
