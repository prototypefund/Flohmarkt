import { createImage } from "./image.js";
import { createLink } from "./link.js";
import { createElement } from "./element.js";

export function createItem(item, username) {
    const element = createElement('aside', 'position-relative');
    element.appendChild(createImage('https://http.cat/200' /*item.image.src*/, item.name/*item.image.alt*/, 'card-img-top w-100'));
    const wrapper = createElement('div', 'p-2');
    const container = createElement('div', 'd-flex justify-content-between');
    container.appendChild(createLink('/~' + username + '/' + item.id, 'stretched-link', item.name));
    container.appendChild(createElement('span', null, item.price /*+ item.currency*/));
    wrapper.appendChild(container);
    wrapper.appendChild(createElement('p', null, item.description));
    element.appendChild(wrapper);

    return element;
}
