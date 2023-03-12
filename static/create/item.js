import { createImg } from "./img.js";
import { createLink } from "./link.js";
import { createElement } from "./element.js";

export function createItem(item) {
    const element = createElement('div', 'item');
    element.appendChild(createImg(item.image.src, item.image.alt));
    element.appendChild(createLink('/~' + item.user + '/' + item.id, 'd-block stretched-link', item.name));
    element.appendChild(createElement('p', null, item.price + item.currency));

    return element;
}
