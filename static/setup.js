import { postForm } from './utils.js';

const setupForm = document.getElementById('setup-form');
const setupBtn = setupForm.querySelector('button');
setupBtn.addEventListener('click', async event => {
    event.preventDefault();

    var data = await postForm(setupForm);
    console.log(data);
    if (data["ok"]) {
        window.location.pathname = '/';
    }
});

/*let inputValid = 0,
    password;

setupForm.querySelectorAll('input').forEach((input, index) => {
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
        setupBtn.disabled = inputValid !== 15; // 1111
    });
});*/
