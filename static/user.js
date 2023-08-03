import { fetchJSON, putJSON, deleteCall } from "./utils.js";
import { createImg } from "./create/img.js";
import { createSVG } from "./create/svg.js";
import { createItem } from "./create/item.js";
import { createElement } from "./create/element.js";
import { updateAvatar } from "./app.js";
import { getCurrentUser } from "./current_user.js"
import "./create/image_uploader.js";

const [items, user, currentUser] = await Promise.all([
    fetchJSON('item/by_user/' + window.USER_ID),
    fetchJSON('user/' + window.USER_ID),
    getCurrentUser
]);

var watching = [];
if (currentUser != null && 'watching' in currentUser) {
    watching = currentUser["watching"];
}

const imageUploader = document.getElementById('image_uploader');

const itemsFragment = document.createDocumentFragment();
items.forEach(async item => {
    itemsFragment.appendChild(createItem(item, false, watching));
});

const userFragment = document.createDocumentFragment();

const token = JSON.parse(window.sessionStorage.getItem('parsedToken'));
var watched_items = [];
const watchedFragment = document.createDocumentFragment();
if (token != null  && token != "null" && token.username == user.name) {
    document.getElementById('profile-form').style.display="block";
    watched_items = await fetchJSON('item/get_watched');
    watched_items.forEach(async item => {
        watchedFragment.appendChild(createItem(item, false, watching));
    });
} else {
    document.getElementById('profile').style.display="block";
}

const gridUserItems = document.querySelector('.grid__user-items'),
      colAbout = document.querySelector('.col__about');
window.requestAnimationFrame(() => {
    gridUserItems.appendChild(itemsFragment);
    gridUserItems.appendChild(watchedFragment);
    colAbout.appendChild(userFragment);
});

const createBtn = document.getElementById('create-btn');
createBtn.addEventListener('click', event => {
    event.preventDefault();

    const formData = new FormData(createForm);

    const sendData = {
        bio: formData.get('bio')
    };

    const imagedata = imageUploader.getData();
    console.log(imagedata);
    if (imagedata.length == 1) {
        sendData.avatar = imagedata[0].image_id;
    }

    putJSON("/api/v1/user/"+user.id, sendData)
    .then(async data => {
        const new_user = await fetchJSON('user/' + user.id);
	updateAvatar(new_user.avatar);
	window.location.pathname = '/~' + new_user.name;
    });
});

const deleteButton = document.getElementById('delete-btn');
deleteButton.addEventListener('click', async e => {
    if (prompt("Please enter your username to confirm account deletion!") == user.name) {
        const res = await deleteCall('/api/v1/user/'+user.id);
        if (res == true) {
            window.sessionStorage.setItem('token',null);
            window.sessionStorage.setItem('parsedToken',null);
            window.location = "/";
        }
    } else {
        alert("Wrong usename. Aborting account deletion");
    }
});

const notificationButton = document.getElementById('notification-btn');
notificationButton.addEventListener('click', ()=>{
    if (!("Notification" in window)) {
        return;
    }
    if (Notification.permission !== "granted") {
        Notification.requestPermission();
    }
});


const createForm = document.getElementById('create-form');
let inputValid = 0;
createForm.querySelectorAll('input, textarea').forEach((input, index) => {
    input.addEventListener('change', function() {
        createBtn.disabled = false; // 1111
    });
});
