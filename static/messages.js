import { fetchJSON, postJSON } from "./utils.js";
import { createSmallAvatar } from "./create/avatar.js";
import { getCurrentUser, isCurrentUser } from "./current_user.js";
import { createElement } from "./create/element.js";
import { createMessage, createConversation, getUser } from "./create/message.js";
import { incoming } from "./app.js";

const [conversations, currentUser] = await Promise.all([
    fetchJSON('conversation/own'),
    getCurrentUser
]);

const items = {};

const loadItems = async conversations => {
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
}

await loadItems(conversations);

var skip = 0;

const moreButton = document.getElementById("more-button");
if (conversations.length == 10) {
    moreButton.style.display="block";
    moreButton.addEventListener('click', async e => {
        skip+=10;
        const newConversations = await fetchJSON('conversation/own?skip='+skip);
        await loadItems(newConversations);
        newConversations.forEach(renderConversationButton);
    });
}

const convDisplay = document.getElementById('conversation-display');

const convSelector = document.getElementById('conversation-selector');

const DIR_IN = 0;
const DIR_OUT = 1;

var currentConversationButton = null;

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
    if (convo.item_id in items && items[convo.item_id].images.length > 0) {
        img.src = "/api/v1/image/"+items[convo.item_id].images[0].image_id;
    } else {
        img.src = "/static/nopic.webp";
    }
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
    if (direction == DIR_IN) {
        cell.appendChild(createSmallAvatar(await getUser(convo.remote_user)));
    } else {
        cell.appendChild(createSmallAvatar(await getUser(convo.user_id)));
    }
    if (convo.item_id in items ) {
        cell.appendChild(createElement('span','', items[convo.item_id].name));
    } else {
        cell.appendChild(createElement('span','', 'Deleted Item'));
    }
    row.appendChild(cell);
    row.addEventListener('click', async e=>  {
        const c = await createConversation(convo);
        convDisplay.innerHTML = "";
        convDisplay.appendChild(c);
        cell.classList.add("active_convo_selector");
        if (currentConversationButton !== null) {
            currentConversationButton.classList.remove("active_convo_selector");
        }
        currentConversationButton = cell;
    });
    if (conversations.indexOf(convo) == 0) {
        cell.classList.add("active_convo_selector");
        currentConversationButton = cell;
    }
    convSelector.prepend(row);
    row.convo = convo;
}

conversations.reverse();
await conversations.forEach(renderConversationButton);

incoming.addEventListener('conversation', async msg=>{
    const item = await fetchJSON('item/'+msg["item_id"]);
    items[item["id"]] = item;
    await renderConversationButton(msg);
});

incoming.addEventListener('message', async msg=>{
    convSelector.childNodes.forEach(r=>{
        if (r.convo ?? null != null) {
            let belongs_here = false;
            if (msg["inReplyTo"].indexOf(r.convo.item_id) != -1) {
                belongs_here = true;   
            }
            r.convo.messages.forEach(m=>{
                if (m.id == msg["inReplyTo"]) {
                    belongs_here = true;   
                }
            });
            if (belongs_here) {
                r.convo.messages.push(msg);
                const x = r;
                r.remove();
                convSelector.prepend(x);
            }
        }
    });
});

// Select the first conversation
const c = await createConversation(conversations[0]);
convDisplay.appendChild(c);

