import { fetchJSON, postJSON } from "./utils.js";
import { createSmallAvatar } from "./create/avatar.js";
import { getCurrentUser, isCurrentUser } from "./current_user.js";
import { createElement } from "./create/element.js";
import { createMessage, createConversation } from "./create/message.js";

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

const convDisplay = document.getElementById('conversation-display');

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
    row.addEventListener('click', async e=>  {
        const c = await createConversation(convo);
        convDisplay.innerHTML = "";
        convDisplay.appendChild(c);
    });
    convSelector.appendChild(row);
}

conversations.forEach(renderConversationButton);
