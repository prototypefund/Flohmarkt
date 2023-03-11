
function getToken() {
    var pw = document.querySelector('#password').value;
    var user = document.querySelector('#username').value;
    fetch ('/token', {
        headers: {
            "Content-type":"application/x-www-form-urlencoded",
        },
        method: "POST",
        body: 'username='+user+'&password='+pw
    })
    .then(response=>{return response.json();})
    .then(data=>{sessionStorage.token = data;})
    .catch(function(res){console.log(res)});
}

document.querySelector('.login_button').addEventListener("click", getToken);
