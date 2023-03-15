import { createElement } from "./element.js";

export function createImg(src, alt, className=null) {
    const image = createElement('img', className);
    image.src = src.endsWith('.svg') ? '/static/' + src : src;
    image.alt = alt;

    return image;
}
