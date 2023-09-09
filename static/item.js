import { fetchJSON, postJSON, deleteCall } from "./utils.js";
import { createItem } from "./create/item.js";
import { createElement } from "./create/element.js";
import { createImage } from "./create/image.js";
import { createSVG, replaceSVG } from "./create/svg.js";
import { createMessage, createConversation, getUser } from "./create/message.js";
import { createAvatar, createSmallAvatar } from "./create/avatar.js";
import { getCurrentUser } from "./current_user.js";
import { createReportForm } from "./create/reportform.js";
import { createEditItemForm } from "./create/edititemform.js";
import { incoming } from "./app.js";

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

if (token != undefined && token != "null") {
    conversations = await fetchJSON('conversation/by_item/' + window.location.pathname.replace(/^.+?[/]/, ''));
}
const user = await fetchJSON('user/' + item.user);

const heading = document.getElementById('heading');
const avalink = createElement('a');
avalink.href="/~"+user.name;
avalink.append(createAvatar(user));
heading.prepend(avalink);

const itemFragment = document.createDocumentFragment();

const controls_container = createElement('div','card-toolbar','');
itemFragment.appendChild(controls_container);

const watch_button = createSVG('eye' + (watching.includes(item.id) ? '-off' : ''));
watch_button.style.zIndex = "22";
watch_button.classList.add('toolbar_button');
watch_button.classList.add('eye' + (watching.includes(item.id) ? '-off' : ''));
watch_button.addEventListener('click', async e => {
    if (watch_button.classList.contains('eye')) {
        await fetchJSON('item/'+item.id+'/watch');
        replaceSVG(watch_button, 'eye', 'eye-off');
    } else {
        await fetchJSON('item/'+item.id+'/unwatch');
        replaceSVG(watch_button, 'eye-off', 'eye');
    }
});
const report_button = createSVG('message-report');
report_button.classList.add('toolbar_button');
const delete_button = createSVG('trash');
delete_button.classList.add('toolbar_button');
delete_button.addEventListener('click', async event=> {
    if (confirm("Do you really want to delete " + item.name + "?")) {
        await deleteCall('/api/v1/item/' + item.id);
        window.location.pathname = '/~' + user.name;
    }
});
const edit_button = createSVG('edit');
edit_button.classList.add('toolbar_button');
if (typeof(currentUser) != "function") {
    controls_container.appendChild(watch_button);
    controls_container.appendChild(report_button);
}
if (item.user == currentUser.id || currentUser.admin == true) {
    controls_container.appendChild(delete_button);
}
if (item.user == currentUser.id) {
    controls_container.appendChild(edit_button);
}

const reportForm = createReportForm(item);
reportForm.style.display = "none";

const editItemForm = createEditItemForm(item);
editItemForm.style.display = "none";


const textbox_container = createElement('div','card-toolbar','');
textbox_container.style.display="none";
textbox_container.appendChild(reportForm);
textbox_container.appendChild(editItemForm);
itemFragment.appendChild(textbox_container);

report_button.addEventListener('click', e => {
    reportForm.style.display = reportForm.style.display == "none" ? "block" : "none";
    textbox_container.style.display = textbox_container.style.display == "none" ? "block" : "none";
});

edit_button.addEventListener('click', e => {
    editItemForm.style.display = editItemForm.style.display == "none" ? "block" : "none";
    textbox_container.style.display = textbox_container.style.display == "none" ? "block" : "none";
});

itemFragment.appendChild(createItem(item, true, watching));
const itemOperationContainer = createElement('div',null, '');

const conversationsFragment = document.createDocumentFragment();
const conversationIndicatorContainer = createElement('div','conv_indicator', '');

const conversationContainers = {};

const conversationLoginHintContainer = createElement('div',null, '');
const conversationLoginHintText = createElement('p',null, '');
conversationLoginHintText.innerHTML = `

To answer this offer please <a href="/login">log in</a> or <a href="/registerform">create an account</a>.

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

incoming.addEventListener('conversation', async msg=>{
    console.log(msg);
    let found = false;
    if (item.id != msg.item_id) {
        return;
    };
    for (const id in  conversationContainers) {
        if (id == msg.id) {
            found = true;
            break;
        }
    }
    if ( found ) {
        return;
    }
    const container = await createConversation(msg);
    conversationContainers[msg.id] = container;
    const indicator = createSmallAvatar(await getUser(msg.remote_user));
    indicator.name = msg.id;
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


if (token == undefined && token != "null") {
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
