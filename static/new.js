import { fetchJSON, postJSON } from './utils.js';

const createBtn = document.getElementById('create-btn');
createBtn.addEventListener('click', event => {
    event.preventDefault();

    const formData = new FormData(createForm);
    postJSON({
        name: formData.get('title'),
        description: formData.get('description'),
        price: formData.get('price')
    })
    .then(async data => {
        const user = await fetchJSON('user/' + data.user);
        window.location.pathname = '/~' + user.name + '/' + data.id;
    });
});

const createForm = document.getElementById('create-form');
let inputValid = 0;
createForm.querySelectorAll('input, textarea').forEach((input, index) => {
    input.addEventListener('input', function() {
        let valid;
        switch (this.id) {
            case 'title':
            case 'price':
            case 'description':
                valid = this.value !== '';
                break;
        }
        const mask = 1 << index;
        inputValid = valid ? inputValid | mask : inputValid & ~mask;
        createBtn.disabled = inputValid !== 7; // 111
    });
});
