export function updateAvatar(avatar) {
    const token = window.sessionStorage.getItem('token');
    if (token != undefined && token != "null" && typeof(token) === 'string') {
        const parsedToken = JSON.parse(window.sessionStorage.getItem('parsedToken'));
        parsedToken.avatar = avatar;
        const new_token = JSON.stringify(parsedToken);
        window.sessionStorage.setItem('parsedToken', new_token);
    }
}
