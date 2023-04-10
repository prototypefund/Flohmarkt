export async function fetchJSON(path) {
    const response = await window.fetch(path.endsWith('.json') ? '/static/' + path : '/api/v1/' + path, {
        headers: {
            'Authorization' : 'Bearer ' + window.sessionStorage.getItem('token')
        }
    }).catch(error => console.error(error));
    return await response.json();
}

export async function postForm(form, authorization=false) {
    const options = {
        method: form.method,
        body: new FormData(form),
        ...(authorization && { headers: {
            'Authorization' : 'Bearer ' + window.sessionStorage.getItem('token')
        }})
    };
    const response = await window.fetch(form.action, options)
    .catch(error => console.error(error));
    
    return await response.json();
}

export async function postJSON(url, payload) {
    const response = await window.fetch(url, {
        headers: {
            'Content-type': 'application/json',
            'Authorization': 'Bearer ' + window.sessionStorage.getItem('token')
        },
        method: 'post',
        body: JSON.stringify(payload),
    })
    .catch(error => console.error(error));
    
    return await response.json();
}

export async function putJSON(url, payload) {
    const response = await window.fetch(url, {
        headers: {
            'Content-type': 'application/json',
            'Authorization': 'Bearer ' + window.sessionStorage.getItem('token')
        },
        method: 'put',
        body: JSON.stringify(payload),
    })
    .catch(error => console.error(error));
    
    return await response.json();
}
