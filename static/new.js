import { query } from './utils.js';

const createBtn = document.getElementById('create-btn');
createBtn.addEventListener('click', async event => {
    event.preventDefault();

    try {
        const response = await window.fetch('/', {
            headers: {
                "Content-type":"multipart/form-data",
            },
            method: "POST",
            body: 'title=' + document.getElementById('title').value
                  + '&' +
                  'price=' + document.getElementById('price').value
                  + '&' +
                  'description=' + document.getElementById('description').value
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
