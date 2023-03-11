import { fetchJSON } from "./utils.js";
import { createItem } from "./create/item.js";

const items = await fetchJSON('items');

const itemsFragment = document.createDocumentFragment();
items.forEach(item => {
    itemsFragment.appendChild(createItem(item));
});

const secondFragment = itemsFragment.cloneNode(true);

window.requestAnimationFrame(() => {
    document.querySelector('.grid__newest').appendChild(itemsFragment);
    document.querySelector('.grid__contested').appendChild(secondFragment);
});
