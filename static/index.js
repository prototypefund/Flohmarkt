import { fetchJSON } from "./utils.js";
import { createItem } from "./create/item.js";

const [itemsNewest, itemsContested] = await Promise.all([
    fetchJSON('item/newest'),
    fetchJSON('item/most_contested')
]);

const gridNewest = document.querySelector('.grid__newest'),
      gridContested = document.querySelector('.grid__contested');

itemsNewest.forEach(async item => {
    window.requestAnimationFrame(() => {
        gridNewest.appendChild(createItem(item, false));
    });
});

itemsContested.forEach(async item => {
    window.requestAnimationFrame(() => {
        gridContested.appendChild(createItem(item, false));
    });
});
