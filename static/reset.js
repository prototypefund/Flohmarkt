document.getElementById('reset-btn').addEventListener('click', async event => {
    event.preventDefault();

    try {
        const response = await window.fetch('/password_reset', {
            headers: {
                "Content-type":"application/x-www-form-urlencoded",
            },
            method: "POST",
            body: 'email=' + document.getElementById('email').value
        });
        const data = await response.json();
        console.log(data);
    } catch (error) {
        console.log(error);
    }
});
