import { postForm } from "./utils.js";

document.getElementById('reset-btn').addEventListener('click', event => {
    event.preventDefault();

    const resetForm = document.getElementById('reset-form');
    const data = postForm(resetForm);
    console.log(data);
});
