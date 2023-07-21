import { fetchJSON } from "./utils.js";
import { getCurrentUser } from "./current_user.js";
import { createItem } from "./create/item.js";

const gridResults = document.querySelector('.grid__results');

const [items, user] = await Promise.all([
    fetchJSON('item/search?q=' + gridResults.dataset.searchterm),
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

const searchButton = document.getElementById("more_button");

if (items.length == 120) {
    searchButton.style.display='block';
}

var skip = 120;

searchButton.addEventListener("click", async e => {
    const items = await fetchJSON('item/search?q=' + gridResults.dataset.searchterm + "?skip=" + skip);
    skip += 120;
    items.forEach(async item => {
        window.requestAnimationFrame(() => {
            gridResults.appendChild(createItem(item, false, watching));
        });
    });
    if (items.length < 120) {
        searchButton.style.display='none';
    }
});
