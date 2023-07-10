import { fetchJSON, postJSON, deleteCall } from "./utils.js";
import { createItem } from "./create/item.js";
import { createElement } from "./create/element.js";
import { createImage } from "./create/image.js";
import { createMessage, createConversation, getUser } from "./create/message.js";
import { createAvatar, createSmallAvatar } from "./create/avatar.js";
import { getCurrentUser } from "./current_user.js";

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
heading.prepend(createAvatar(user));

const itemFragment = document.createDocumentFragment();
itemFragment.appendChild(createItem(item, true, watching));
const itemOperationContainer = createElement('div',null, '');
const deleteButton = createElement('button', null, 'Delete');
deleteButton.addEventListener('click', async event=> {
    await deleteCall('/api/v1/item/' + item.id);
    window.location.pathname = '/~' + user.name;
});
const reportButton = createElement('button', null, 'Report');
itemOperationContainer.appendChild(deleteButton);
itemOperationContainer.appendChild(reportButton);
itemFragment.appendChild(itemOperationContainer);

const conversationsFragment = document.createDocumentFragment();
const conversationIndicatorContainer = createElement('div',null, '');

const conversationContainers = {};

const conversationLoginHintContainer = createElement('div',null, '');
const conversationLoginHintText = createElement('p',null, '');
conversationLoginHintText.innerHTML = 'To participate in this conversation please <a href="/login">log in</a> or <a href="/register">create an account</a>.';
conversationLoginHintContainer.appendChild(conversationLoginHintText);

const conversationContainer = createElement('div',null, '');
conversations.forEach(async conversation => {
    const container = await createConversation(conversation);
    conversationContainers[conversation.id] = container;
    console.log(conversation.remote_user);
    const indicator = createSmallAvatar(await getUser(conversation.remote_user));
    indicator.name = conversation.id;
    indicator.onclick = (t) => {
        conversationContainer.innerHTML = "";
        const c = conversationContainers[t.srcElement.name];
        conversationContainer.appendChild(c);
    };
    conversationIndicatorContainer.appendChild(indicator);
});
if (conversations.length == 0 && item.user != currentUser.id) {
    const container = await createConversation({"item_id": item.id, "id": null, "messages":[]});
    conversationContainer.appendChild(container);
    
}

conversationsFragment.appendChild(conversationIndicatorContainer);
conversationsFragment.appendChild(conversationContainer);

if (token === null) {
    conversationsFragment.appendChild(conversationLoginHintContainer);
}

const colItem = document.querySelector('.col__item'),
      colChat = document.querySelector('.col__chat');
window.requestAnimationFrame(() => {
    colItem.appendChild(itemFragment);
    colChat.appendChild(conversationsFragment);
});
