import { postForm } from './utils.js';

const registerForm = document.getElementById('register-form');
const registerBtn = registerForm.querySelector('button');
registerBtn.addEventListener('click', async event => {
    event.preventDefault();

    event.target.disabled = true;
    var data = await postForm(registerForm);
    window.location.pathname = '/registered';
});

let inputValid = 0,
    password;

registerForm.querySelectorAll('input').forEach((input, index) => {
    input.addEventListener('input', function() {
        let valid;
        switch (this.name) {
            case 'username':
                valid = this.value !== '';
                break;
            case 'email':
                // https://stackoverflow.com/a/9204568/5764676
                valid = /^\S+@\S+\.\S+$/.test(this.value);
                break;
            case 'password':
                valid = this.value !== '';
                password = this.value;
                break;
            case 'password-repeat':
                valid = this.value === password;
                break;
            case 'accept':
                valid = this.value;
                break;
        }
        const mask = 1 << index;
        inputValid = valid ? inputValid | mask : inputValid & ~mask;
        registerBtn.disabled = inputValid !== 31; // 1111
    });
});
