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
    const summaryElement = detailsListItem.querySelector('summary');
    summaryElement.prepend(createSmallAvatar(parsedToken));

    showElements.push(detailsListItem);
    showElements.push(document.getElementById('new-list-item'));
}
else {
    showElements.push(document.getElementById('register-list-item'));
    showElements.push(document.getElementById('login-list-item'));
}

window.requestAnimationFrame(() => {
    showElements.forEach(element => element.hidden = false )
});
