import { fetchJSON } from "./utils.js";
import { createItem } from "./create/item.js";
import { createElement } from "./create/element.js";
import { createImage } from "./create/image.js";

const [item, users, log] = await Promise.all([
    fetchJSON('item.json'),
    fetchJSON('user'),
    fetchJSON('log.json')
]);

const itemFragment = document.createDocumentFragment();
itemFragment.appendChild(createItem(item));

const usersFragment = document.createDocumentFragment();
const usersContainer = createElement('div', 'd-flex');
users.forEach(user => {
    usersContainer.appendChild(createImage(user.avatar || 'user.svg', user.name, 'avatar circle'));
});
usersFragment.appendChild(usersContainer);

const logFragment = document.createDocumentFragment();
const logContainer = document.createElement('div');
log.forEach(element =>{
    logContainer.appendChild(createElement('p', null, (element.from.name || 'Me') + ': ' + element.message));
});
logFragment.appendChild(logContainer);


const colItem = document.querySelector('.col__item'),
      colChat = document.querySelector('.col__chat');
window.requestAnimationFrame(() => {
    colItem.appendChild(itemFragment);
    colChat.appendChild(usersFragment);
    colChat.appendChild(logFragment);
});
