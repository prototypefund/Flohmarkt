import { fetchJSON } from "./utils.js";
import { createItem } from "./create/item.js";
import { createElement } from "./create/element.js";

const [itemsNewest, itemsContested, itemsOldest] = await Promise.all([
    fetchJSON('item/newest'),
    fetchJSON('item/most_contested'),
    fetchJSON('item/oldest')
]);

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
        item["reason"] = key;
    });
}

itemsNewest.push(...itemsContested);
itemsNewest.push(...itemsOldest);


const shuffled = itemsNewest
    .map(value => ({ value, sort: Math.random() }))
    .sort((a, b) => a.sort - b.sort)
    .map(({ value }) => value)

const gridResults = document.querySelector('.grid__results');

shuffled.forEach(async item => {
    window.requestAnimationFrame(() => {
	const htmlItem = createItem(item, false);
	htmlItem.appendChild(createElement("div", 'circle badge badge_'+item.reason, label_mapping[item.reason]));
        gridResults.appendChild(htmlItem);
    });
});
