import { fetchJSON } from "./utils.js";

const results = document.getElementById('results');

const items = await fetchJSON('search/' + results.dataset.searchterm);
items.forEach(item => {
    console.log(item);
});
