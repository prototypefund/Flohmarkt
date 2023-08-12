import { fetchJSON, putJSON, deleteCall } from "./utils.js";
import { initTabs } from "./tabs.js";
import { getCurrentUser } from "./current_user.js";
import { updateAvatar } from "./app.js";
import { createElement } from "./create/element.js";
import "./create/image_uploader.js";

const imageUploader = document.getElementById('image_uploader');
initTabs();

const [currentUser] = await Promise.all([
    getCurrentUser
]);

const saveForm = document.getElementById('save-form');
const saveBtn = document.getElementById('save-btn');
saveBtn.addEventListener('click', event => {
    event.preventDefault();

    const formData = new FormData(saveForm);

    const sendData = {
        bio: formData.get('bio')
    };

    const imagedata = imageUploader.getData();
    console.log(imagedata);
    if (imagedata.length == 1) {
        sendData.avatar = imagedata[0].image_id;
    }

    putJSON("/api/v1/user/"+currentUser.id, sendData)
    .then(async data => {
        const new_user = await fetchJSON('user/' + currentUser.id);
	updateAvatar(new_user.avatar);
	window.location.pathname = '/~' + new_user.name;
    });
});
const bio_entry = document.getElementById('bio');
bio_entry.value = currentUser.bio;

const deleteButton = document.getElementById('delete-btn');
deleteButton.addEventListener('click', async e => {
    if (prompt("Please enter your username to confirm account deletion!") == user.name) {
        const res = await deleteCall('/api/v1/user/'+user.id);
        if (res == true) {
            window.sessionStorage.setItem('token',null);
            window.sessionStorage.setItem('parsedToken',null);
            window.location = "/";
        }
    } else {
        alert("Wrong usename. Aborting account deletion");
    }
});

const notificationButton = document.getElementById('notification-btn');
notificationButton.addEventListener('click', ()=>{
    if (!("Notification" in window)) {
        return;
    }
    if (Notification.permission !== "granted") {
        Notification.requestPermission();
    }
});

const blockUsersInput = document.getElementById('blockUserInput');
const blockUsersButton = document.getElementById('blockUserButton');
const blockUsersTable = document.getElementById('blockUserTable');

blockUsersButton.addEventListener('click', async e => {
    const inp = encodeURIComponent(blockUsersInput.value);
    const response = await fetchJSON("user/"+currentUser.id+"/block_user?block=true&user="+inp).catch(error=>console.error(error));
    const row = createElement('tr','');
    const nameCell = createElement('td', null, blockUsersInput.value);
    const commandCell = createElement('td', null, '');
    const unfollowButton = createElement('button', null, 'Unblock');
    unfollowButton.addEventListener('click', async e => {
        const response = await fetchJSON("user/"+currentUser.id+"/block_user?block=false&user="+inp).catch(error=>console.error(error));
        row.remove();
    });
    commandCell.appendChild(unfollowButton);
    row.appendChild(nameCell);
    row.appendChild(commandCell);
    blockUsersTable.appendChild(row);
});
console.log(currentUser);
(currentUser.blocked_users ?? []).forEach(e => {
    const row = createElement('tr','');
    const nameCell = createElement('td', null, e);
    const commandCell = createElement('td', null, '');
    const unblockButton = createElement('button', null, 'Unblock');
    unblockButton.addEventListener('click', async f => {
        const response = await fetchJSON("user/"+currentUser.id+"/block_user?block=false&user="+e).catch(error=>console.error(error));
        row.remove();
    });
    commandCell.appendChild(unblockButton);
    row.appendChild(nameCell);
    row.appendChild(commandCell);
    blockUsersTable.appendChild(row);
});
