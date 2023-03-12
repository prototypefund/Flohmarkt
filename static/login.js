document.getElementById('login-btn').addEventListener('click', async event => {
    event.preventDefault();

    const username = document.getElementById('username').value,
          password = document.getElementById('password').value;

    try {
        fetch('/token', {
            headers: {
                "Content-type":"application/x-www-form-urlencoded",
            },
            method: "POST",
            body: 'username=' + username
                  + '&' +
                  'password=' + password
        }).then(response => { return response.json();
        }).then(data=> {
            console.log(typeof(data));
            if (typeof(data) !== "string" ) {console.log("no valid login"); return;}
            window.sessionStorage.setItem('token', data);
            window.location.pathname = '/~' + username;
        }).catch(()=>{});
    } catch (error) {
        console.log(error);
    }
});
