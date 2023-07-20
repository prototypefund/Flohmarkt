import { fetchJSON } from "./utils.js";
import { createItem } from "./create/item.js";
import { createElement } from "./create/element.js";
import { getCurrentUser } from "./current_user.js";

const instanceInfo = document.getElementById("instance-info");
const currentUser = await getCurrentUser;
console.log(currentUser);
if (!("id" in currentUser)) {
    instanceInfo.style.display="block";
}

const [itemsNewest, itemsContested, itemsOldest, user] = await Promise.all([
    fetchJSON('item/newest'),
    fetchJSON('item/most_contested'),
    fetchJSON('item/oldest'),
    getCurrentUser
]);

var watching = [];
if (user != null && 'watching' in user) {
    watching = user["watching"];
}

const reason_mapping = {
    "newest": itemsNewest,
    "most_contested": itemsContested,
    "oldest": itemsOldest
}

const label_mapping = {
    "newest": "NEW!",
    "most_contested": "POPULAR",
    "oldest": "OLD!",
    "zufall": "RANDOM!",
}

for (let key in reason_mapping) {
    reason_mapping[key].forEach(async item=> {
        if (item != null) 
            item["reason"] = key;
    });
}

itemsNewest.push(...itemsContested);
itemsNewest.push(...itemsOldest);

const keys = {};
const to_display = [];

itemsNewest.forEach(async item=> {
    if (item == null) return;
    if (!(item.id in keys)) {
        to_display.push(item);
        keys[item.id] = 1;
    }
});


const shuffled = to_display
    .map(value => ({ value, sort: Math.random() }))
    .sort((a, b) => a.sort - b.sort)
    .map(({ value }) => value)

const gridResults = document.querySelector('.grid__results');

shuffled.forEach(item => {
    window.requestAnimationFrame(() => {
	const htmlItem = createItem(item, false, watching);
	htmlItem.appendChild(createElement("div", 'circle badge badge_'+item.reason, label_mapping[item.reason]));
        gridResults.appendChild(htmlItem);
    });
});
