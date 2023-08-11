import { fetchJSON } from "./utils.js";
import { createImg } from "./create/img.js";
import { createItem } from "./create/item.js";
import { createElement } from "./create/element.js";
import { getCurrentUser } from "./current_user.js"

const [items, user, currentUser] = await Promise.all([
    fetchJSON('item/by_user/' + window.USER_ID),
    fetchJSON('user/' + window.USER_ID),
    getCurrentUser
]);

var watching = [];
if (currentUser != null && 'watching' in currentUser) {
    watching = currentUser["watching"];
}

const itemsFragment = document.createDocumentFragment();
items.forEach(async item => {
    itemsFragment.appendChild(createItem(item, false, watching));
});

const userFragment = document.createDocumentFragment();

var watched_items = [];
const watchedFragment = document.createDocumentFragment();

const gridUserItems = document.querySelector('.grid__user-items'),
      colAbout = document.querySelector('.col__about');
window.requestAnimationFrame(() => {
    gridUserItems.appendChild(itemsFragment);
    gridUserItems.appendChild(watchedFragment);
    colAbout.appendChild(userFragment);
});

