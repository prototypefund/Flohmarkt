import { fetchJSON } from "./utils.js";
import { createItem } from "./create/item.js";

const gridResults = document.querySelector('.grid__results');

const itemsResults = await fetchJSON('item/search/' + gridResults.dataset.searchterm);

itemsResults.forEach(async item => {
    window.requestAnimationFrame(() => {
        gridResults.appendChild(createItem(item, false));
    });
});
