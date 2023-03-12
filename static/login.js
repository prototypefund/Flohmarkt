document.getElementById('login-btn').addEventListener('click', async event => {
    event.preventDefault();

    const username = document.getElementById('username').value,
          password = document.getElementById('password').value;

    try {
        const response = await window.fetch('/token', {
            headers: {
                "Content-type":"application/x-www-form-urlencoded",
            },
            method: "POST",
            body: 'username=' + username
                  + '&' +
                  'password=' + password
        });
        const data = await response.json();
        window.sessionStorage.setItem('token', data);
        window.location.pathname = '/~' + username;
    } catch (error) {
        console.log(error);
    }
});
