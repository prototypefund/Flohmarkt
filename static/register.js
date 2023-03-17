import { postForm } from './utils.js';

const registerForm = document.getElementById('register-form');
const registerBtn = registerForm.querySelector('button');
registerBtn.addEventListener('click', async event => {
    event.preventDefault();

    var data = await postForm(registerForm);
    console.log(data);
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
        }
        const mask = 1 << index;
        inputValid = valid ? inputValid | mask : inputValid & ~mask;
        registerBtn.disabled = inputValid !== 15; // 1111
    });
});
