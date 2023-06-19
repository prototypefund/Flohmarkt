import { postForm } from "./utils.js";

const resetForm = document.getElementById('resetpw-form');
const resetBtn = document.getElementById('resetpw-btn');

document.getElementById('resetpw-btn').addEventListener('click', event => {
    event.preventDefault();

    postForm(resetForm).then(data=>{
	if (data["result"] == true) {
	    window.location.pathname = '/login';
	}
    });
});

var password="";

resetForm.querySelectorAll('input').forEach((input, index) => {
    input.addEventListener('input', function() {
        let valid;
        switch (this.name) {
            case 'password':
                password = this.value;
                break;
            case 'password-repeat':
                valid = this.value === password;
                break;
        }
        resetBtn.disabled = !valid
    });
});
