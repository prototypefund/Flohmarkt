import { fetchJSON } from "./utils.js";
import { getCurrentUser } from "./current_user.js";
import { createItem } from "./create/item.js";

const gridResults = document.querySelector('.grid__results');

const [items, user] = await Promise.all([
    fetchJSON('item/any'),
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

const moreButton = document.getElementById("more_button");

if (items.length == 50) {
    moreButton.style.display='block';
}

var skip = 50;

moreButton.addEventListener("click", async e => {
    const items = await fetchJSON('item/any?skip=' + skip);
    skip += 50;
    items.forEach(async item => {
        window.requestAnimationFrame(() => {
            gridResults.appendChild(createItem(item, false, watching));
        });
    });
    if (items.length < 50) {
        moreButton.style.display='none';
    }
});
