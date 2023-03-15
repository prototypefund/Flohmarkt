import { fetchJSON } from "./utils.js";
import { createItem } from "./create/item.js";

const [itemsNewest, itemsContested] = await Promise.all([
    fetchJSON('item/newest'),
    fetchJSON('item/most_contested')
]);

const fragmentNewest = document.createDocumentFragment();
itemsNewest.forEach(async item => {
    const user = await fetchJSON('user/' + item.user);
    fragmentNewest.appendChild(createItem(item, user.name));
});

const fragmentContested = document.createDocumentFragment();
itemsContested.forEach(async item => {
    const user = await fetchJSON('user/' + item.user);
    fragmentContested.appendChild(createItem(item, user.name));
});

const gridNewest = document.querySelector('.grid__newest'),
      gridContested = document.querySelector('.grid__contested');
window.requestAnimationFrame(() => {
    gridNewest.appendChild(fragmentNewest);
    gridContested.appendChild(fragmentContested);
});
