import { fetchJSON, postJSON } from "./../utils.js";
import { createElement } from "./element.js";
import { getCurrentUser, isCurrentUser } from "./../current_user.js";
import { createSmallAvatar } from "./avatar.js";

const current_user = await getCurrentUser;

const conversation_users = {};

export const getUser = async user_url => {
    if (user_url in conversation_users) {
        return conversation_users[user_url];
    } else {
        const u = await fetchJSON('avatar/by_remote?url='+encodeURIComponent(user_url));
        conversation_users[user_url] = u;
        return u;
    }
}

const makedate = ds => {
    const d = new Date(Date.parse(ds.replace("Z","+0000")));
    return d.toLocaleString();
}

export const createMessage = async message => {
    const messageElement = createElement('div', null, '');
    const dateElement = createElement('div', 'messagedate', makedate(message.published));
    const textElement = createElement('p', null, '');
    textElement.innerHTML = message.content;
    messageElement.classList.add("message");
    const cssclass = isCurrentUser(message) ? "message_me" : "message_you";
    messageElement.classList.add(cssclass);
    if ("overridden" in message) {
        messageElement.classList.add("message_overridden");
    }
    const user = await getUser(message.attributedTo);
    const nameElement = createElement('span', 'messagedate', user.name);
    const ava = createSmallAvatar(user);
    ava.classList.add("message_ava");
    ava.classList.add(isCurrentUser(message) ? "message_ava_me" : "message_ava_you");
    messageElement.appendChild(ava);
    messageElement.appendChild(dateElement);
    messageElement.appendChild(nameElement);
    messageElement.appendChild(textElement);
    return messageElement;
}

export const createConversation = async conversation => {
    const conversationAllContainer = createElement('div', null, "");
    const conversationMessagesContainer = createElement('div', null, "");
    conversationMessagesContainer.id = conversation.id;
    conversationMessagesContainer.classList.add('message_container');
    const messages = "messages" in conversation ? conversation.messages : [];
   
    const messageElements= await Promise.all(messages.map(createMessage));
    messageElements.forEach( e=> {
	    conversationMessagesContainer.appendChild(e);
    });
    conversationAllContainer.appendChild(conversationMessagesContainer);

    if (current_user !== null) {
        const conversationFormContainer = createElement('form',null, '');
        const sendButton = createElement('button', null, 'Send');
        const assignButton = createElement('button', null, 'Assign');
        assignButton.style.display="none";
        if (current_user.id == conversation.user_id) {
            assignButton.style.display="inline";
        }
        const textArea = createElement('textarea', null, '');
        textArea.name="content";
        conversationFormContainer.appendChild(textArea);
        conversationFormContainer.appendChild(sendButton);
        conversationFormContainer.appendChild(assignButton);
        sendButton.addEventListener('click', async event => {
            event.preventDefault();

            const formData = new FormData(conversationFormContainer);
            postJSON("/api/v1/conversation/to_item/"+conversation.item_id, {
                text: formData.get('content'),
                conversation_id :  conversation.id,
                item_id :  conversation.item_id
            })
            .then(async data => {
                const m = await createMessage(data["messages"].at(-1));
                conversationMessagesContainer.appendChild(m);
            });
        });
        assignButton.addEventListener('click', async event=> {
            event.preventDefault();

            const formData = new FormData(conversationFormContainer);
            postJSON("/api/v1/item/"+conversation.item_id+"/give", {
                text: formData.get('content'),
                conversation_id :  conversation.id,
                item_id :  conversation.item_id
            })
            .then(async data => {
                const m = await createMessage(data["messages"].at(-1));
                conversationMessagesContainer.appendChild(m);
            });
        });

        conversationAllContainer.appendChild(conversationFormContainer);
    }

    return conversationAllContainer;
}
