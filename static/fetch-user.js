import { fetchJSON } from "./utils.js";

const itemsFragment = document.createDocumentFragment();
const userFragment = document.createDocumentFragment();

const items = await fetchJSON('/items.json');
items.forEach(item => {
    const element = document.createElement('div');
    element.className = 'item';
    
    const image = document.createElement('img');
    image.src = item.image.src;
    image.alt = item.image.alt;
    element.appendChild(image);

    const link = document.createElement('a');
    link.className = 'stretched-link';
    link.href = '/' + item.user + '@' + item.instance + '/' + item.id;
    link.textContent = item.name;
    element.appendChild(link);

    const price = document.createElement('div');
    price.textContent = item.price + item.currency;
    element.appendChild(price);

    itemsFragment.appendChild(element);
});

const user = await fetchJSON('/user.json');
const joined = document.createElement('p');
joined.textContent = user.joined;
userFragment.appendChild(joined);

window.requestAnimationFrame(() => {
    document.querySelector('.grid__my-articles').appendChild(itemsFragment);
    document.querySelector('.grid__about').appendChild(userFragment);
});
