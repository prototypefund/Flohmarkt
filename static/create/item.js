import { createImg } from "./img.js";
import { createLink } from "./link.js";
import { createElement } from "./element.js";

export function createItem(item) {
    const element = createElement('div', 'item');
    element.appendChild(createImg(item.image.src, item.image.alt));
    element.appendChild(createLink('d-block stretched-link', '/~' + item.user + '/' + item.id, item.name));
    element.appendChild(createElement('p', null, item.price + item.currency));

    return element;
}
