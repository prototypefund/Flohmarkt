import { fetchJSON, postJSON } from './utils.js';
import { createElement } from "./create/element.js";
import { createImg } from "./create/img.js";
import { createSVG } from "./create/svg.js";
import { getCurrentUser } from "./current_user.js";
import "./create/image_uploader.js";

var uploaded_images = [];

const current_user = await getCurrentUser;
if (current_user !== null && current_user.banned) {
    const form = document.getElementById("create-form");
    form.innerHTML = "";
    form.appendChild(createElement('p',null,"You are banned. You can't create new items"));
    throw new Error("Aborting due to ban");
}

const imageUploader = document.getElementById('image_uploader');

const createBtn = document.getElementById('create-btn');
createBtn.addEventListener('click', event => {
    event.preventDefault();

    const formData = new FormData(createForm);

    const imagedata = imageUploader.getData();
    postJSON("/api/v1/item/", {
        name: formData.get('title'),
        description: formData.get('description'),
        price: formData.get('price'),
        images: imagedata,
    })
    .then(async data => {
        const user = await fetchJSON('user/' + data.user);
        window.location.pathname = '/~' + user.name + '/' + data.id;
    });
});

const createForm = document.getElementById('create-form');
let inputValid = 0;
createForm.querySelectorAll('input, textarea').forEach((input, index) => {
    input.addEventListener('keyup', function() {
        let valid;
        switch (this.id) {
            case 'title':
            case 'price':
            case 'description':
                valid = this.value !== '';
                break;
            case 'upload':
            case 'images':
                valid = true;
                break;
        }
        console.log("GIBE INFO");
        const mask = 1 << index;
        inputValid = valid ? inputValid | mask : inputValid & ~mask;
        console.log(inputValid);
        createBtn.disabled = inputValid !== 7; // 1111
    });
});


