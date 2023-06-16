import { createSmallAvatar } from "./create/avatar.js";

const showElements = [];
const token = window.sessionStorage.getItem('token');
if (token != undefined && token != null && typeof(token) === 'string') {
    const parsedToken = JSON.parse(window.sessionStorage.getItem('parsedToken'));
    const username = parsedToken.username;
    const detailsListItem = document.getElementById('details-list-item');
    detailsListItem.querySelector('.details-menu span').append(username);
    detailsListItem.querySelector('.details-menu .l-profile').href = '/~' + username;
    detailsListItem.querySelector('.details-menu .l-site-admin').href = '/admin';
    headerAvatar();

    showElements.push(detailsListItem);
    showElements.push(document.getElementById('new-list-item'));
} else {
    showElements.push(document.getElementById('register-list-item'));
    showElements.push(document.getElementById('login-list-item'));
}

export function updateAvatar(avatar) {
    const token = window.sessionStorage.getItem('token');
    if (token != undefined && token != null && typeof(token) === 'string') {
        const parsedToken = JSON.parse(window.sessionStorage.getItem('parsedToken'));
	parsedToken.avatar = avatar;
	const new_token = JSON.stringify(parsedToken);
	window.sessionStorage.setItem('parsedToken', new_token);
	headerAvatar();
    }
}

function headerAvatar() {
    const token = window.sessionStorage.getItem('token');
    if (token != undefined && token != null && typeof(token) === 'string') {
        const avatarslot = document.getElementById('avatar-slot');
        avatarslot.innerHTML = '';
        const parsedToken = JSON.parse(window.sessionStorage.getItem('parsedToken'));
        avatarslot.appendChild(createSmallAvatar(parsedToken));
    }
}

window.requestAnimationFrame(() => {
    showElements.forEach(element => element.hidden = false )
});
