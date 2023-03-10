import { fetchJSON } from "./utils.js";

const itemFragment = document.createDocumentFragment();
const usersFragment = document.createDocumentFragment();
const logFragment = document.createDocumentFragment();

const item = await fetchJSON('/static/item.json');
const image = document.createElement('img');
image.src = item.image.src;
image.alt = item.image.alt;
itemFragment.appendChild(image);

const price = document.createElement('div');
price.textContent = item.price + item.currency;
itemFragment.appendChild(price);

const description = document.createElement('p');
description.textContent = item.description;
itemFragment.appendChild(description);

const users = await fetchJSON('/static/users.json');
const usersContainer = document.createElement('div');
usersContainer.className = 'd-flex';
users.forEach(user => {
    const image = document.createElement('img');
    image.src = user.src;
    image.alt = user.name;
    usersContainer.appendChild(image);
});
usersFragment.appendChild(usersContainer);

const log = await fetchJSON('/static/log.json');
const logContainer = document.createElement('div');
log.forEach(element =>{
    const message = document.createElement('p');
    const from = element.from.name || 'Me'; 
    message.textContent = from + ': ' + element.message;
    logContainer.appendChild(message);
});
logFragment.appendChild(logContainer);

window.requestAnimationFrame(() => {
    document.querySelector('.col__item').appendChild(itemFragment);
    document.querySelector('.col__chat').appendChild(usersFragment);
    document.querySelector('.col__chat').appendChild(logFragment);
});
