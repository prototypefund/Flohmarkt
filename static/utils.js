export async function fetchJSON(path) {
    const response = await window.fetch(path);
    return response.json();
}

export function query(selector) {
    return Array.from(document.querySelectorAll(selector));
}
