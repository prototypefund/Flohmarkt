import { fetchJSON } from "./utils.js";
import { createItem } from "./create/item.js";
import { createElement } from "./create/element.js";

const [items, users] = await Promise.all([
    fetchJSON('items.json'),
    fetchJSON('user')
]);

const itemsFragment = document.createDocumentFragment();
items.forEach(item => {
    itemsFragment.appendChild(createItem(item));
});

const userFragment = document.createDocumentFragment();
userFragment.appendChild(createElement('p', null, 'id: ' + users[0].id/*user.joined*/));

const gridUserItems = document.querySelector('.grid__user-items'),
      colAbout = document.querySelector('.col__about');
window.requestAnimationFrame(() => {
    gridUserItems.appendChild(itemsFragment);
    colAbout.appendChild(userFragment);
});
