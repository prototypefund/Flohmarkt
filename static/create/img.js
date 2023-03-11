import { createElement } from "./element.js";

export function createImg(src, alt) {
    const image = createElement('img');
    image.src = '/static/' + src;
    image.alt = alt;

    return image;
}
