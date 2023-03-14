import { createImage } from "./create/image.js";

function parse_jwt (token) {
    var base64Url = token.split('.')[1];
    var base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    var jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    return JSON.parse(jsonPayload);
}

const showElements = [];
const token = window.sessionStorage.getItem('token');
if (token != undefined && token != null && typeof(token) === 'string') {
    const parsedToken = parse_jwt(token);
    const username = parsedToken.username;
    const detailsListItem = document.getElementById('details-list-item');
    detailsListItem.querySelector('.details-menu span').append(username);
    detailsListItem.querySelector('.details-menu a').href = '/~' + username;
    const summaryElement = detailsListItem.querySelector('summary');
    summaryElement.prepend(createImage(parsedToken.avatar, username, 'avatar circle'));

    showElements.push(detailsListItem);
}
else {
    showElements.push(document.getElementById('register-list-item'));
    showElements.push(document.getElementById('login-list-item'));
}

window.requestAnimationFrame(() => {
    showElements.forEach(element => element.hidden = false )
});
