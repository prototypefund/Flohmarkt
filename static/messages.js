import { fetchJSON, postJSON } from "./utils.js";
import { createSmallAvatar } from "./create/avatar.js";
import { getCurrentUser, isCurrentUser } from "./current_user.js";
import { createElement } from "./create/element.js";

const [conversations, currentUser] = await Promise.all([
    fetchJSON('conversation/own'),
    getCurrentUser
]);

const items = {};
if (conversations.length > 0 ) {
    var itemIds = "?";
    conversations.forEach(async convo => {
        itemIds += "item="+convo["item_id"]+"&";
    });
    itemIds = itemIds.slice(0,-1);

    const items_res =await fetchJSON('item/many'+itemIds)
    items_res.forEach(item => {
        items[item["id"]] = item;
    });
}

var skip = 0;

const moreButton = document.getElementById("more-button");
if (conversations.length == 10) {
    moreButton.style.display="block";
    moreButton.addEventListener('click', async e => {
        skip+=10;
        const newConversations = await fetchJSON('conversation/own?skip='+skip);
        newConversations.forEach(renderConversationButton);
    });
}

var current_conversation = null;

const convDisplay = document.getElementById('conversation-display');

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

const renderConversation = convo => {
    convDisplay.innerHTML = "";
    convo.messages.forEach( m=> {
        createMessage(convDisplay, m);
    });

    const conversationFormContainer = createElement('form',null, '');
    const sendButton = createElement('button', null, 'Send');
    //const assignButton = createElement('button', null, 'Assign');
    const textArea = createElement('textarea', null, '');
    textArea.name="content";
    conversationFormContainer.appendChild(textArea);
    conversationFormContainer.appendChild(sendButton);
    //conversationFormContainer.appendChild(assignButton);
    sendButton.addEventListener('click', event => {
        event.preventDefault();

        const formData = new FormData(conversationFormContainer);
        postJSON("/api/v1/conversation/to_item/"+convo.item_id, {
            text: formData.get('content'),
            conversation_id :  current_conversation.id,
            item_id :  convo.item_id
        })
        .then(async data => {
            const messagesContainer = renderConversation(data);
        });
    });
    convDisplay.append(conversationFormContainer);
}

const convSelector = document.getElementById('conversation-selector');

const DIR_IN = 0;
const DIR_OUT = 1;

const renderConversationButton = async convo => {
    var direction = null;
    if (convo.remote_url == currentUser.remote_url) {
        direction = DIR_OUT;
    }
    if (convo.user_id == currentUser.id) {
        direction = DIR_IN;
    }


    const row = createElement('tr', 'convo_row', '');
    const cell = createElement('td', 'convo_cell', '');
    cell.style.width="99%";
    const img = createElement('img', '','');
    img.src = "/api/v1/image/"+items[convo.item_id].images[0];
    img.style.display = "inline-block";
    img.style.height="50px";
    img.style.width="50px";
    img.style.verticalAlign="middle";
    cell.appendChild(img)
    if (direction == DIR_IN) {
        cell.appendChild(createElement('span','',' 📧 '));
    } else {
        cell.appendChild(createElement('span','',' 📨 '));
    }
    cell.appendChild(createSmallAvatar(currentUser));
    cell.appendChild(createElement('span','', items[convo.item_id].name));
    row.appendChild(cell);
    row.addEventListener('click', e=>  {
        current_conversation = convo;
        renderConversation(convo)
    });
    convSelector.appendChild(row);
}

conversations.forEach(renderConversationButton);
