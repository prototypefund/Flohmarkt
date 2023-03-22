import { fetchJSON, postJSON } from './utils.js';

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

const uploadInput = document.getElementById('upload');
uploadInput.addEventListener('change', () => {
    const gridImages = document.querySelector('.grid__images');
    for (const file of uploadInput.files) {
        const fileReader = new FileReader();
        fileReader.onload = event => {
            let srcData = event.target.result;
            const image = new Image();
            image.src = srcData
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
            window.requestAnimationFrame(() => {
                gridImages.appendChild(image);
            });
        }
        fileReader.readAsDataURL(file);
    };
});
