const response = await window.fetch('/blacklist_token', {
    headers: {
        'Authorization' : 'Bearer ' + window.sessionStorage.getItem('token')
    }
}).catch(error => console.error(error));
const res = await response.json();
if (res.success == true) {
    window.sessionStorage.removeItem('token');
    window.sessionStorage.removeItem('parsedToken');
    window.location.pathname = '/';
}


