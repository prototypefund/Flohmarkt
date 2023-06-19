import { fetchJSON, postJSON, deleteCall } from "./utils.js";
import { createItem } from "./create/item.js";
import { createElement } from "./create/element.js";
import { createImage } from "./create/image.js";
import { createAvatar,createSmallAvatar } from "./create/avatar.js";

const item = await fetchJSON('item/' + window.location.pathname.replace(/^.+?[/]/, ''));
const token = JSON.parse(window.sessionStorage.getItem('parsedToken'));
var conversations = [];
if (token !== null) {
    conversations = await fetchJSON('conversation/by_item/' + window.location.pathname.replace(/^.+?[/]/, ''));
}
const user = await fetchJSON('user/' + item.user);
const conversation_users = {};

for (const conversation in conversations) {
    const c = conversations[conversation];
    const conv_user = await fetchJSON('user/by_remote/?url='+c.remote_user);
    if ("avatar" in user) {
	conversation_users[c.remote_user] = conv_user;
    }
}

const heading = document.getElementById('heading');
heading.prepend(createAvatar(user));

const itemFragment = document.createDocumentFragment();
itemFragment.appendChild(createItem(item, true));
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
const conversationFormContainer = createElement('form',null, '');
const sendButton = createElement('button', null, 'Send');
const assignButton = createElement('button', null, 'Assign');
var current_conversation = "";
sendButton.addEventListener('click', event => {
    event.preventDefault();

    const formData = new FormData(conversationFormContainer);
    postJSON("/api/v1/conversation/to_item/"+item.id, {
        text: formData.get('content'),
	conversation_id :  current_conversation,
	item_id :  item.id
    })
    .then(async data => {
        const messagesContainer = createConversation(data);
	createMessage(messagesContainer, data["messages"].at(-1));
    });
});
assignButton.addEventListener('click', event=> {
    event.preventDefault();
    const formData = new FormData(conversationFormContainer);
    postJSON("/api/v1/item/"+item.id+"/give", {
        text: formData.get('content'),
	conversation_id :  current_conversation,
	item_id :  item.id
    })
    .then(async data => {
	console.log(data);
    });
});
const textArea = createElement('textarea', null, '');
textArea.name="content";
conversationFormContainer.appendChild(textArea);
conversationFormContainer.appendChild(sendButton);
conversationFormContainer.appendChild(assignButton);

const isCurrentUser = message => {
    const token = JSON.parse(window.sessionStorage.getItem('parsedToken'));
    const actor_url = new URL(message.attributedTo);
    const own_url = new URL(window.location);
    if (actor_url.host !=  own_url.host) {
        return false;
    }
    return message.attributedTo.endsWith("/"+token.username);
};

const conversationContainers = {};

const conversationLoginHintContainer = createElement('div',null, '');
const conversationLoginHintText = createElement('p',null, '');
conversationLoginHintText.innerHTML = 'To participate in this conversation please <a href="/login">log in</a> or <a href="/register">create an account</a>.';
conversationLoginHintContainer.appendChild(conversationLoginHintText);

const createConversation = function(conversation) {
    if (conversation.id in conversationContainers) {
        return conversationContainers[conversation.id];
    }
    const indicator = createElement('a', null, '');
    if (conversation.remote_user in conversation_users) {
	const av = createSmallAvatar(conversation_users[conversation.remote_user]);
	indicator.appendChild(av);
    } else {
	const av = createElement('div', null, '');
	av.style.height="100px";		
	av.style.width="100px";		
	av.style.display="inline-block";		
	av.style.backgroundColor="crimson";		
	indicator.appendChild(av);
    }

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
    conversationMessagesContainer.id = conversation.id;
    conversationMessagesContainer.style.display = "none";
    conversationMessagesContainer.classList.add('message_container');
    conversationContainer.appendChild(conversationMessagesContainer);
    conversationContainers[conversation.id] = conversationMessagesContainer;
    return conversationMessagesContainer;
}

const createMessage = function(container, message) {
    const messageElement = createElement('p', null, '');
    messageElement.innerHTML = message.content;
    messageElement.classList.add("message");
    const cssclass = isCurrentUser(message) ? "message_me" : "message_you";
    messageElement.classList.add(cssclass);
    if ("overridden" in message) {
	messageElement.classList.add("message_overridden");
    }
    container.appendChild(messageElement);
}

const conversationContainer = createElement('div',null, '');
conversations.forEach(conversation => {
    const container = createConversation(conversation);
    const messages = "messages" in conversation ? conversation.messages : [];
    messages.forEach(message=> {
	    createMessage(container, message);
    });
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
