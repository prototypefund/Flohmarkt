import { postJSON } from "./../utils.js";
import { createElement } from "./element.js";
import { getCurrentUser, isCurrentUser } from "./../current_user.js";

const current_user = await getCurrentUser;

export const createReportForm = (item) => {
    if (current_user !== null) {
        const reportForm = createElement('form',null, '');
        const sendButton = createElement('button', null, 'Send Report');
        const textArea = createElement('textarea', null, '');
        textArea.name="content";
        reportForm.appendChild(textArea);
        reportForm.appendChild(sendButton);
        sendButton.addEventListener('click', async event => {
            event.preventDefault();

            const formData = new FormData(reportForm);
            postJSON("/api/v1/report/", {
                reason: formData.get('content'),
                user_id :  current_user.id,
                item_id :  item.id
            })
            .then(async data => {
                alert("Your report has been submitted");
                textArea.value = "";
                reportForm.style.display = 'none';
            });
        });

        return (reportForm);
    } else {
        return createElement('span','','');
    }
}
