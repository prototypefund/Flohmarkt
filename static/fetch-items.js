import { fetchJSON } from "./utils.js";

const items = await fetchJSON('items');

const itemsFragment = document.createDocumentFragment();

items.forEach(item => {
    const element = document.createElement('div');
    element.className = 'item';

    const link = document.createElement('a');
    link.className = 'stretched-link';
    link.href = '/' + item.user + '@' + item.instance + '/' + item.id;
    link.textContent = item.name;

    const image = document.createElement('img');
    image.src = item.image.src;
    image.alt = item.image.alt;
    link.appendChild(image);

    const price = document.createElement('div');
    price.textContent = item.price + item.currency;
    link.appendChild(price);

    const user = document.createElement('div');
    user.textContent = item.user + '@' + item.instance;
    link.appendChild(user);

    element.appendChild(link);
    itemsFragment.appendChild(element);
});

const secondFragment = itemsFragment.cloneNode(true);

window.requestAnimationFrame(() => {
    document.querySelector('.grid__newest').appendChild(itemsFragment);
    document.querySelector('.grid__contested').appendChild(secondFragment);
});
