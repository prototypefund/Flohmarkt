import { fetchJSON } from "./utils.js";
import { createItem } from "./create/item.js";
import { createElement } from "./create/element.js";
import { createImg } from "./create/img.js";

const [item, users, log] = await Promise.all([
    fetchJSON('item'),
    fetchJSON('users'),
    fetchJSON('log')
]);

const itemFragment = document.createDocumentFragment();
const element = createItem(item);
element.appendChild(createElement('p', null, item.description));
itemFragment.appendChild(element);

const usersFragment = document.createDocumentFragment();
const usersContainer = createElement('div', 'd-flex');
users.forEach(user => {
    usersContainer.appendChild(createImg(user.src, user.alt));
});
usersFragment.appendChild(usersContainer);

const logFragment = document.createDocumentFragment();
const logContainer = document.createElement('div');
log.forEach(element =>{
    logContainer.appendChild(createElement('p', null, element.from.name || 'Me' + ': ' + element.message));
});
logFragment.appendChild(logContainer);

window.requestAnimationFrame(() => {
    document.querySelector('.col__item').appendChild(itemFragment);
    document.querySelector('.col__chat').appendChild(usersFragment);
    document.querySelector('.col__chat').appendChild(logFragment);
});
