import { fetchJSON, postJSON } from './utils.js';
import { createElement } from "./create/element.js";
import { createImg } from "./create/img.js";
import { createSVG } from "./create/svg.js";

const MAX_WIDTH = 1920,
      MAX_HEIGHT = 1080;

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

let selected;
const uploadInput = document.getElementById('upload');
uploadInput.addEventListener('change', () => {
    const gridImages = document.querySelector('.grid__images');
    for (const file of uploadInput.files) {
        const fileReader = new FileReader();
        fileReader.onload = event => {
            let srcData = event.target.result;
            const image = createImg(srcData, file.name, 'd-block');
            image.onload = () => {
                let width = image.width,
                    height = image.height,
                    resize;
            
                if (width > height) {
                    if (width > MAX_WIDTH) {
                        height *= MAX_WIDTH / width;
                        width = MAX_WIDTH;
                        resize = true;
                    }
                }
                if (height > MAX_HEIGHT) {
                    width *= MAX_HEIGHT / height
                    height = MAX_HEIGHT
                    resize = true
                }
                if (resize) {
                    const canvas = document.createElement('canvas'),
                    context = canvas.getContext('2d')
                    
                    canvas.width = width
                    canvas.height = height
                    
                    context.drawImage(image, 0, 0, width, height)
                    //srcData = canvas.toDataURL('image/jpeg')
                }
            }
            function isBefore(el1, el2) {
                let cur;
                if (el2.parentNode === el1.parentNode) {
                  for (cur = el1.previousSibling; cur; cur = cur.previousSibling) {
                    if (cur === el2) return true;
                  }
                }

                return false;
            }
            const li = createElement('li');
            li.classList.add('position-relative');
            li.classList.add('p-0');
            li.draggable = false;
            li.addEventListener('dragend', () => {
                selected = null;
                li.draggable = false;
            });
            li.addEventListener('dragover', event => {
                const parent = event.target.parentNode;
                if (parent.tagName !== 'LI') return;
                if (event.target.closest('li').isEqualNode(selected)) return;
                if (isBefore(selected, parent)) {
                    gridImages.insertBefore(selected, parent);
                } else {
                    gridImages.insertBefore(selected, parent.nextSibling)
                }
            });
            li.addEventListener('dragstart', event => {
                event.dataTransfer.effectAllowed = 'move';
                event.dataTransfer.setData('text/plain', null); // still needed for Firefox?
                selected = event.target;
            });
            li.appendChild(image);
            const iconDelete = createSVG('x');
            iconDelete.addEventListener('click', () => {
                li.remove();
            });
            li.appendChild(iconDelete);
            const iconGrab = createSVG('hand-grab');
            iconGrab.addEventListener('pointerdown', () => {
                li.draggable = true;
            });
            iconGrab.addEventListener('pointerup', () => {
                li.draggable = false;
            });
            li.appendChild(iconGrab);
            window.requestAnimationFrame(() => {
                gridImages.appendChild(li);
            });
        }
        fileReader.readAsDataURL(file);
    };
});
