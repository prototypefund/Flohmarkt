import { createElement } from "./element.js";

export function createImg(src, alt, className=null) {
    const image = createElement('img', className);
    image.src = '/static/' + src;
    image.alt = alt;

    return image;
}
