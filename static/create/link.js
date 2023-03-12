import { createElement } from "./element.js";

export function createLink(href, className=null, textContent=null) {
    const link = createElement('a', className, textContent);
    link.href = href;

    return link;
}
