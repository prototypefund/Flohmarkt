import { putJSON } from "./../utils.js";
import { createElement } from "./element.js";
import { getCurrentUser, isCurrentUser } from "./../current_user.js";

const current_user = await getCurrentUser;

export const createEditItemForm = (item) => {
    if (current_user !== null) {
        const editItemForm = createElement('form',null, '');
        const sendButton = createElement('button', null, 'Save');
        const textArea = createElement('textarea', null, '');
        textArea.name="content";
        textArea.innerHTML = item.description;
        editItemForm.appendChild(textArea);
        editItemForm.appendChild(sendButton);
        sendButton.addEventListener('click', async event => {
            event.preventDefault();

            const formData = new FormData(editItemForm);
            putJSON("/api/v1/item/"+item.id, {
                description: formData.get('content'),
            })
            .then(async data => {
                alert("Applied changes");
            });
        });

        return (editItemForm);
    } else {
        return createElement('span','','');
    }
}
