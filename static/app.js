import { createElement } from './create/element.js';
import { createLink } from './create/link.js';

function parse_jwt (token) {
    var base64Url = token.split('.')[1];
    var base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    var jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    return JSON.parse(jsonPayload);
}

const token = window.sessionStorage.getItem('token');
if (token != undefined && token != null && typeof(token) === "string" ) {
    var parsed_token = parse_jwt(token);
    const listItem = createElement('li', null, parsed_token.username);
    const dropDown = createElement('ul');
    const dropItem = createElement('li');
    const dropLink = createLink('/logout', null, 'Logout');

    dropItem.appendChild(dropLink);
    dropDown.appendChild(dropItem);
    listItem.appendChild(dropDown);

    const menu = document.querySelector('nav ul');
    window.requestAnimationFrame(() => {
        while (menu.firstChild) {
            menu.firstChild.remove();
        }                
        menu.appendChild(listItem);
    });
}
