import { fetchJSON } from "./utils.js";
import { createItem } from "./item/create.js";

const [items, user] = await Promise.all([
    fetchJSON('items'),
    fetchJSON('user')
]);

const itemsFragment = document.createDocumentFragment();
const userFragment = document.createDocumentFragment();

items.forEach(item => {
    itemsFragment.appendChild(createItem(item));
});

const userJoined = document.createElement('p');
userJoined.textContent = user.joined;
userFragment.appendChild(userJoined);

window.requestAnimationFrame(() => {
    document.querySelector('.grid__my-items').appendChild(itemsFragment);
    document.querySelector('.col__about').appendChild(userFragment);
});
