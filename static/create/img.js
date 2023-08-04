import { createElement } from "./element.js";

export function createImg(src, alt=null, className=null) {
    const image = createElement('img', className);
    image.src = src;
    if (alt) {
        image.alt = alt;
    }

    return image;
}
