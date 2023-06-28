import { fetchJSON } from "./utils.js";
import { getCurrentUser } from "./current_user.js";
import { createItem } from "./create/item.js";

const gridResults = document.querySelector('.grid__results');

const [items, user] = await Promise.all([
    fetchJSON('item/search/' + gridResults.dataset.searchterm),
    getCurrentUser
]);

var watching = [];
if (user != null && 'watching' in user) {
    watching = user["watching"];
}

items.forEach(async item => {
    window.requestAnimationFrame(() => {
        gridResults.appendChild(createItem(item, false, watching));
    });
});
