import { createElement } from './create/element.js';
import { createLink } from './create/link.js';

const token = window.sessionStorage.getItem('token');
if (token) {
    const listItem = createElement('li', null, token);
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
