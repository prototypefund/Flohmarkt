import { createImage } from "./create/image.js";

const showElements = [];
const token = window.sessionStorage.getItem('token');
if (token != undefined && token != null && typeof(token) === 'string') {
    const parsedToken = JSON.parse(window.sessionStorage.getItem('parsedToken'));
    const username = parsedToken.username;
    const detailsListItem = document.getElementById('details-list-item');
    detailsListItem.querySelector('.details-menu span').append(username);
    detailsListItem.querySelector('.details-menu a').href = '/~' + username;
    const summaryElement = detailsListItem.querySelector('summary');
    summaryElement.prepend(createImage(parsedToken.avatar || 'user.svg', username, 'avatar circle'));

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
