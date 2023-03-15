import { fetchJSON } from "./utils.js";
import { createItem } from "./create/item.js";

const items = await fetchJSON('items.json');

const itemsFragment = document.createDocumentFragment();
items.forEach(item => {
    itemsFragment.appendChild(createItem(item));
});

const secondFragment = itemsFragment.cloneNode(true);

const gridNewest = document.querySelector('.grid__newest'),
      gridContested = document.querySelector('.grid__contested');
window.requestAnimationFrame(() => {
    gridNewest.appendChild(itemsFragment);
    gridContested.appendChild(secondFragment);
});
