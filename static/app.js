import { createSmallAvatar } from "./create/avatar.js";

const token = window.sessionStorage.getItem('token');

const token_expiry_check = () => {
    console.log("check token expiry");
    if (token != undefined && token != null && typeof(token) === 'string') {
        const parsedToken = JSON.parse(window.sessionStorage.getItem('parsedToken'));
        if (parsedToken.exp < Date.now()) {
            window.sessionStorage.setItem('parseToken', null);
            window.sessionStorage.setItem('token', null);
            window.location = window.location;
        }
    }
    window.setTimeout(token_expiry_check, 1000);
};

document.addEventListener('load', token_expiry_check);

const showElements = [];
if (token != undefined && token != null && typeof(token) === 'string') {
    const parsedToken = JSON.parse(window.sessionStorage.getItem('parsedToken'));
    const username = parsedToken.username;
    const detailsListItem = document.getElementById('details-list-item');
    detailsListItem.querySelector('.details-menu span').append(username);
    detailsListItem.querySelector('.details-menu .l-profile').href = '/~' + username;
    detailsListItem.querySelector('.details-menu .l-messaging').href = '/messages';
    if (parsedToken.admin === true || parsedToken.moderator === true) {
        detailsListItem.querySelector('.details-menu .l-site-moderation').href = '/moderation';
    } else {
        detailsListItem.querySelector('.details-menu .s-site-moderation').style.display = 'none';
    }
    if (parsedToken.admin === true) {
        detailsListItem.querySelector('.details-menu .l-site-admin').href = '/admin';
    } else {
        detailsListItem.querySelector('.details-menu .s-site-admin').style.display = 'none';
    }
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
