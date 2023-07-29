import { fetchJSON, postJSON, deleteCall } from "./utils.js";
import { createItem } from "./create/item.js";
import { createElement } from "./create/element.js";
import { createImage } from "./create/image.js";
import { createMessage, createConversation, getUser } from "./create/message.js";
import { createAvatar, createSmallAvatar } from "./create/avatar.js";
import { getCurrentUser } from "./current_user.js";
import { createReportForm } from "./create/reportform.js";
import { createEditItemForm } from "./create/edititemform.js";

const [item, currentUser] = await Promise.all([
    fetchJSON('item/' + window.location.pathname.replace(/^.+?[/]/, '')),
    getCurrentUser
]);

var watching = [];
if (currentUser != null && 'watching' in currentUser) {
    watching = currentUser["watching"];
}

const token = JSON.parse(window.sessionStorage.getItem('parsedToken'));
var conversations = [];
if (token !== null) {
    conversations = await fetchJSON('conversation/by_item/' + window.location.pathname.replace(/^.+?[/]/, ''));
}
const user = await fetchJSON('user/' + item.user);

const heading = document.getElementById('heading');
const avalink = createElement('a');
avalink.href="/~"+user.name;
avalink.append(createAvatar(user));
heading.prepend(avalink);

const itemFragment = document.createDocumentFragment();
itemFragment.appendChild(createItem(item, true, watching));
const itemOperationContainer = createElement('div',null, '');
const deleteButton = createElement('button', null, 'Delete');
deleteButton.addEventListener('click', async event=> {
    if (confirm("Do you really want to delete " + item.name + "?")) {
        await deleteCall('/api/v1/item/' + item.id);
        window.location.pathname = '/~' + user.name;
    }
});
const reportForm = createReportForm(item);
reportForm.style.display = "none";
const reportButton = createElement('button', null, 'Report');
reportButton.addEventListener('click', e => {
    reportForm.style.display = reportForm.style.display == "none" ? "block" : "none";
});
const editItemForm = createEditItemForm(item);
editItemForm.style.display = "none";
const editItemButton = createElement('button', null, 'Edit');
editItemButton.addEventListener('click', e => {
    editItemForm.style.display = editItemForm.style.display == "none" ? "block" : "none";
});
if (item.user == currentUser.id) {
    itemOperationContainer.appendChild(editItemButton);
}
itemOperationContainer.appendChild(deleteButton);
itemOperationContainer.appendChild(reportButton);
itemFragment.appendChild(itemOperationContainer);
itemFragment.appendChild(reportForm);
itemFragment.appendChild(editItemForm);

const conversationsFragment = document.createDocumentFragment();
const conversationIndicatorContainer = createElement('div','conv_indicator', '');

const conversationContainers = {};

const conversationLoginHintContainer = createElement('div',null, '');
const conversationLoginHintText = createElement('p',null, '');
conversationLoginHintText.innerHTML = `

To participate in this conversation please <a href="/login">log in</a> or <a href="/register">create an account</a>.

OR

use another fediverse-account:
`;
const remoteInteractField = createElement('input','','');
remoteInteractField.placeholder = "myaccount@some-fediverse-server.org";
const remoteInteractButton = createElement('button','','Go!');
remoteInteractButton.addEventListener('click', async e => {
    const name = remoteInteractField.value;
    const res = await fetch("/remote-interact?acc="+encodeURIComponent(name));
    const url = await res.json();
    window.location = url["url"].replace("{uri}",window.location);
});
conversationLoginHintContainer.appendChild(conversationLoginHintText);
conversationLoginHintContainer.appendChild(remoteInteractField);
conversationLoginHintContainer.appendChild(remoteInteractButton);

let firstSelected = false;
const selectFirst = async convCont => {
    if (firstSelected) return;
    conversationContainer.innerHTML = "";
    conversationContainer.appendChild(convCont);
    firstSelected = true;
}

const conversationContainer = createElement('div',null, '');
conversations.forEach(async conversation => {
    const container = await createConversation(conversation);
    conversationContainers[conversation.id] = container;
    const indicator = createSmallAvatar(await getUser(conversation.remote_user));
    indicator.name = conversation.id;
    indicator.onclick = (t) => {
        conversationContainer.innerHTML = "";
        const c = conversationContainers[t.srcElement.name];
        conversationContainer.appendChild(c);
    };
    conversationIndicatorContainer.appendChild(indicator);
    await selectFirst(container);
});
if (conversations.length == 0 && item.user != currentUser.id) {
    const container = await createConversation({"item_id": item.id, "id": null, "messages":[]});
    conversationContainer.appendChild(container);
    
}


if (token === null) {
    conversationsFragment.appendChild(conversationLoginHintContainer);
} else {
    conversationsFragment.appendChild(conversationIndicatorContainer);
    conversationsFragment.appendChild(conversationContainer);
    if (item.user != currentUser.id) {
        conversationIndicatorContainer.style.display="none";
    }
}

const colItem = document.querySelector('.col__item'),
      colChat = document.querySelector('.col__chat');
window.requestAnimationFrame(() => {
    colItem.appendChild(itemFragment);
    colChat.appendChild(conversationsFragment);
});
