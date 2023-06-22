import { fetchJSON, putJSON } from "./utils.js";
import { createImg } from "./create/img.js";
import { createSVG } from "./create/svg.js";
import { createItem } from "./create/item.js";
import { createElement } from "./create/element.js";
import { updateAvatar } from "./app.js";

const MAX_WIDTH = 128,
      MAX_HEIGHT = 128;

const [items, user] = await Promise.all([
    fetchJSON('item/by_user/' + window.USER_ID),
    fetchJSON('user/' + window.USER_ID)
]);

const itemsFragment = document.createDocumentFragment();
items.forEach(item => {
    itemsFragment.appendChild(createItem(item, false));
});

const userFragment = document.createDocumentFragment();

const token = JSON.parse(window.sessionStorage.getItem('parsedToken'));
console.log(token.username);
console.log(user.name);
if (token.username == user.name) {
    document.getElementById('profile').style.display="none";
} else {
    document.getElementById('profile-form').style.display="none";
}

const gridUserItems = document.querySelector('.grid__user-items'),
      colAbout = document.querySelector('.col__about');
window.requestAnimationFrame(() => {
    gridUserItems.appendChild(itemsFragment);
    colAbout.appendChild(userFragment);
});

const createBtn = document.getElementById('create-btn');
createBtn.addEventListener('click', event => {
    event.preventDefault();

    const formData = new FormData(createForm);
    putJSON("/api/v1/user/"+user.id, {
        bio: formData.get('bio'),
        avatar: formData.get('avatar'),
    })
    .then(async data => {
        const new_user = await fetchJSON('user/' + user.id);
	updateAvatar(new_user.avatar);
	window.location.pathname = '/~' + new_user.name;
    });
});

const createForm = document.getElementById('create-form');
let inputValid = 0;
createForm.querySelectorAll('input, textarea').forEach((input, index) => {
    input.addEventListener('change', function() {
        createBtn.disabled = false; // 1111
    });
});

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
                    srcData = canvas.toDataURL('image/jpeg')
                }
                window.fetch('/api/v1/image/', {
                        method: "post",
                        headers: {
                            "Authorization": "Bearer "+window.sessionStorage.getItem("token")
                        },
                        body: srcData
                    }
                ).then(data=>data.json()
                ).then(id=>{
                    const avatar_input = document.getElementById('avatar');
                    avatar_input.value = id;
                });
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
