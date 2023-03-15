import { createImage } from "./image.js";
import { createLink } from "./link.js";
import { createElement } from "./element.js";

export function createItem(item) {
    const element = createElement('aside', 'position-relative');
    element.appendChild(createImage(item.image.src, item.image.alt, 'card-img-top w-100'));
    const wrapper = createElement('div', 'p-2');
    wrapper.appendChild(createLink('/~' + item.user + '/' + item.id, 'stretched-link', item.name));
    wrapper.appendChild(createElement('p', null, item.price + item.currency));
    wrapper.appendChild(createElement('p', null, item.description));
    element.appendChild(wrapper);

    return element;
}
