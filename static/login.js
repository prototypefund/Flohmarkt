document.getElementById('login-btn').addEventListener('click', async event => {
    event.preventDefault();

    try {
        const response = await window.fetch ('/token', {
            headers: {
                "Content-type":"application/x-www-form-urlencoded",
            },
            method: "POST",
            body: 'username=' + document.getElementById('password').value
                  + '&' +
                  'password=' + document.getElementById('username').value
        });
        const data = await response.json();
        window.sessionStorage.token = data;
    } catch(error) {
        console.log(error);
    }
});
