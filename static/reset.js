import { postForm } from "./utils.js";

document.getElementById('reset-btn').addEventListener('click', event => {
    event.preventDefault();

    const resetForm = document.getElementById('reset-form');
    postForm(resetForm).then(data=>{
	if (data["result"] == true) {
	    window.location.pathname = '/reset_initiated';
	}
    });
});
