export function createElement(tag, className=null, textContent=null) {
    const element = document.createElement(tag);
    if (className) {
        element.className = className;
    }
    if (textContent) {
        element.textContent = textContent;
    }

    return element;
}
