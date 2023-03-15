import { query } from './utils.js';

const createBtn = document.getElementById('create-btn');
createBtn.addEventListener('click', async event => {
    event.preventDefault();

    try {
        const payload = {
            name: document.getElementById('title').value,
            description: document.getElementById('description').value,
            price: document.getElementById('price').value,
        };
        const response = await window.fetch('/api/v1/item/', {
            headers: {
                "Content-type":"application/json",
                "Authorization": "Bearer "+window.sessionStorage.getItem('token'),
            },
            method: "POST",
            body: JSON.stringify(payload),
        });
        const data = await response.json();
        console.log(data);
    } catch (error) {
        console.log(error);
    }
});

let inputValid = 0;
query('.create input, .create textarea').forEach((input, index) => {
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
