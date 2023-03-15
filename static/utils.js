export async function fetchJSON(path) {
    const response = await window.fetch(path.endsWith('.json') ? '/static/' + path : '/api/v1/' + path, {
        "headers": {
            "Authorization" : "Bearer " + window.sessionStorage.getItem('token')
        }
    });
    return await response.json();
}

export function query(selector) {
    return Array.from(document.querySelectorAll(selector));
}
