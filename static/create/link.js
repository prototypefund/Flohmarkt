import { createElement } from "./element.js";

export function createLink(className, href, textContent) {
    const link = createElement('a', className, textContent);
    link.href = href;

    return link;
}
