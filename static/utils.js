export async function fetchJSON(name) {
    const response = await window.fetch('/static/' + name + '.json');
    return await response.json();
}

export function query(selector) {
    return Array.from(document.querySelectorAll(selector));
}
