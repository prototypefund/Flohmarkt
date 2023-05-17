import { fetchJSON, postJSON } from "./utils.js";
import { createItem } from "./create/item.js";
import { createElement } from "./create/element.js";
import { createImage } from "./create/image.js";

const item = await fetchJSON('item/' + window.location.pathname.replace(/^.+?[/]/, ''));
const token = JSON.parse(window.sessionStorage.getItem('parsedToken'));
var conversations = [];
console.log(token);
if (token !== null) {
    conversations = await fetchJSON('conversation/by_item/' + window.location.pathname.replace(/^.+?[/]/, ''));
}
const user = await fetchJSON('user/' + item.user);

const itemFragment = document.createDocumentFragment();
itemFragment.appendChild(createItem(item, user.name));
const itemOperationContainer = createElement('div',null, '');
const deleteButton = createElement('button', null, 'Delete');
const reportButton = createElement('button', null, 'Report');
itemOperationContainer.appendChild(deleteButton);
itemOperationContainer.appendChild(reportButton);
itemFragment.appendChild(itemOperationContainer);

const conversationsFragment = document.createDocumentFragment();
const conversationIndicatorContainer = createElement('div',null, '');
const conversationFormContainer = createElement('form',null, '');
const sendButton = createElement('button', null, '');
var current_conversation = "";
sendButton.innerHTML="Send";
sendButton.addEventListener('click', event => {
    event.preventDefault();

    const formData = new FormData(conversationFormContainer);
    postJSON("/api/v1/conversation/to_item/"+item.id, {
        text: formData.get('content'),
	conversation_id :  current_conversation,
	item_id :  item.id
    })
    .then(async data => {
	//console.log(data);
    });
});
const textArea = createElement('textarea', null, '');
textArea.name="content";
conversationFormContainer.appendChild(textArea);
conversationFormContainer.appendChild(sendButton);

const isCurrentUser = message => {
    const token = JSON.parse(window.sessionStorage.getItem('parsedToken'));
    const actor_url = new URL(message.attributedTo);
    const own_url = new URL(window.location);
    if (actor_url.host !=  own_url.host) {
        return false;
    }
    return message.attributedTo.endsWith("/"+token.username);
};

const conversationLoginHintContainer = createElement('div',null, '');
const conversationLoginHintText = createElement('p',null, '');
conversationLoginHintText.innerHTML = 'To participate in this conversation please <a href="/login">log in</a> or <a href="/register">create an account</a>.';
conversationLoginHintContainer.appendChild(conversationLoginHintText);

const conversationContainer = createElement('div',null, '');
conversations.forEach(conversation => {
    const indicator = createElement('a', null, conversation.remote_user);
    indicator.name = conversation.id;
    indicator.onclick = (t) => {
        const mcs = document.getElementsByClassName('message_container');
	for (const mc of mcs) {
	    const is_current = mc.id == t.srcElement.name;
	    mc.style.display = is_current ? "block" : "none";
	    if (is_current) {
		current_conversation = mc.id
	    }
	}
    };
    const conversationMessagesContainer = createElement('div', null, "");
    conversationIndicatorContainer.appendChild(indicator);
    const messages = "messages" in conversation ? conversation.messages : [];
    const token = JSON.parse(window.sessionStorage.getItem('parsedToken'));
    messages.forEach(message=> {
        const messageElement = createElement('p', null, '');
        messageElement.innerHTML = message.content;
        messageElement.classList.add("message");
        const cssclass = isCurrentUser(message) ? "message_me" : "message_you";
        messageElement.classList.add(cssclass);
        conversationMessagesContainer.appendChild(messageElement);
    });
    conversationMessagesContainer.id = conversation.id;
    conversationMessagesContainer.style.display = "none";
    conversationMessagesContainer.classList.add('message_container');
    conversationContainer.appendChild(conversationMessagesContainer);
});
conversationsFragment.appendChild(conversationIndicatorContainer);
conversationsFragment.appendChild(conversationContainer);
if (token !== null) {
    conversationsFragment.appendChild(conversationFormContainer);
} else {
    conversationsFragment.appendChild(conversationLoginHintContainer);
}

const colItem = document.querySelector('.col__item'),
      colChat = document.querySelector('.col__chat');
window.requestAnimationFrame(() => {
    colItem.appendChild(itemFragment);
    colChat.appendChild(conversationsFragment);
});
