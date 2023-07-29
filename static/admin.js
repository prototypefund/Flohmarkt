import { fetchJSON, postJSON, deleteCall } from "./utils.js";
import { initTabs } from "./tabs.js";
import { createElement } from "./create/element.js";
import { createSmallAvatar } from "./create/avatar.js";

initTabs();

const users = await fetchJSON('user/');

const instance_settings = await fetchJSON('admin/');

const userTable = document.getElementById('userTable');

const usersPerPage = 25;
var userPage = 0;
const nextButton = document.getElementById('user_next_button');
const prevButton = document.getElementById('user_prev_button');

const renderUserList = async user => {
    if (user.name == "instance") {
        return;
    }
    const row = createElement('tr', '');
    const nameCell = createElement('td', '');
    nameCell.appendChild(createSmallAvatar(user));
    nameCell.appendChild(createElement('span', null, user.name));
    row.appendChild(nameCell);
    
    const adminCell = createElement('td', '');
    const adminInput = createElement('input');
    adminInput.type = 'checkbox';
    adminInput.checked = user.admin;
    adminInput.addEventListener("change", async e => {
        const response = (await fetchJSON("admin/toggle_admin/"+user.id));
        adminInput.checked = response.admin;
    });
    adminCell.appendChild(adminInput);
    row.appendChild(adminCell);

    const modCell = createElement('td', '');
    const modInput = createElement('input');
    modInput.type = 'checkbox';
    modInput.checked = user.moderator;
    modInput.addEventListener("change", async e => {
        const response = (await fetchJSON("admin/toggle_moderator/"+user.id));
        modInput.checked = response.moderator;
    });
    modCell.appendChild(modInput);
    row.appendChild(modCell);
    
    const ctrlCell = createElement('td', '');
    const controlsContainer = createElement('div', 'd-flex');

    const banButton = createElement('button', null, user.banned ? 'Unban': 'Ban');
    banButton.addEventListener('click', async e => {
        if (banButton.innerHTML == "Ban") {
            if (confirm("Do you really want to ban " + user.name + "?")){
                const res = await fetchJSON('user/'+user.id+'/ban');
                if (res.banned === true) {
                    banButton.innerHTML = "Unban";
                }
            }
        } else if (banButton.innerHTML == "Unban") {
            const res = await fetchJSON('user/'+user.id+'/unban');
            if (res.banned === false) {
                banButton.innerHTML = "Ban";
            }
        }
    });
    controlsContainer.appendChild(banButton);

    const deleteButton = createElement('button', null, 'Delete');
    deleteButton.addEventListener('click', async e => {
        if (confirm("Do you really want to delete " + user.name + "?")) {
            const res = await deleteCall('api/v1/user/'+ user.id);
            window.location = window.location;
        }
    });
    controlsContainer.appendChild(deleteButton);

    ctrlCell.appendChild(controlsContainer);
    row.appendChild(ctrlCell);

    row.classList.add("user_row");

    userTable.appendChild(row);
};

users.forEach(renderUserList);

if (users.length == 10) {
    nextButton.style.display="inline-block";
}

nextButton.addEventListener('click', async e=>{
    userPage++;
    const users = await fetchJSON('user/?skip='+userPage*usersPerPage);
    userTable.querySelectorAll('.user_row').forEach(e=>e.remove());
    users.forEach(renderUserList);
    if (userPage > 0) {
        prevButton.style.display="inline-block";
    }
    if (users.length < 10) {
        nextButton.style.display="none";
    }
});

prevButton.addEventListener('click', async e=>{
    userPage--;
    const users = await fetchJSON('user/?skip='+userPage*usersPerPage);
    userTable.querySelectorAll('.user_row').forEach(e=>e.remove());
    users.forEach(renderUserList);
    if (userPage == 0) {
        prevButton.style.display="none";
    }
    if (users.length == 10) {
        nextButton.style.display="inline-block";
    }
});

var map_coords = instance_settings.coordinates;

const instanceForm = document.getElementById('settings_form');
const instanceRulesTextArea = document.getElementById('instance_rules');
instanceRulesTextArea.value = instance_settings.rules;
const instanceAboutTextArea = document.getElementById('instance_about');
instanceAboutTextArea.value = instance_settings.about;
const instanceImprintTextArea = document.getElementById('instance_imprint');
instanceImprintTextArea.value = instance_settings.imprint;
const instancePrivacyTextArea = document.getElementById('instance_privacy');
instancePrivacyTextArea.value = instance_settings.privacy;
const instanceRangeInput = document.getElementById('instance_perimeter');
instanceRangeInput.value = instance_settings.perimeter;

const instanceSaveButton = document.getElementById('save_settings');
instanceSaveButton.addEventListener('click', event => {
    event.preventDefault();

    const formData = new FormData(instanceForm);
    postJSON("/api/v1/admin/", {
        coordinates: map_coords,
        perimeter: formData.get('instance_perimeter'),
        rules: formData.get('instance_rules'),
        about: formData.get('instance_about'),
        imprint: formData.get('instance_imprint'),
        privacy: formData.get('instance_privacy'),
        registrations: formData.get('registrations'),
        admin: formData.get('displayed_admin'),
    })
    .then(async data => {
	// reload
    });
});

const map = L.map('map').setView(instance_settings.coordinates, 9);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);
const map_circle = L.circle(instance_settings.coordinates, {
    color: 'red',
    fillColor: '#f03',
    fillOpacity: 0.5,
    radius: instance_settings.perimeter*1000
}).addTo(map);
instanceRangeInput.addEventListener('change', e=> {
    map_circle.setRadius(instanceRangeInput.value * 1000);
});
const setCoordinates = e => {
    map_coords = e.latlng;
    map_circle.setLatLng(e.latlng);
}
map.on('click', setCoordinates);



const followingTable = document.getElementById('followingTable');
const followerTable = document.getElementById('followerTable');

instance_settings.following.forEach(e => {
    const row = createElement('tr','');
    const nameCell = createElement('td', null, e);
    const commandCell = createElement('td', null, '');
    const unfollowButton = createElement('button', null, 'Unfollow');
    unfollowButton.addEventListener('click', async ve => {
        const response = await fetchJSON("admin/unfollow_instance/?url="+e).catch(error=>console.error(error));
        row.remove();
    });
    commandCell.appendChild(unfollowButton);
    row.appendChild(nameCell);
    row.appendChild(commandCell);
    followingTable.appendChild(row);
});

instance_settings.pending_following.forEach(e => {
    const row = createElement('tr','');
    const nameCell = createElement('td', null, e);
    const commandCell = createElement('td', null, '');
    const withdrawButton = createElement('button', null, 'Withdraw');
    withdrawButton.addEventListener('click', async ve => {
        const response = await fetchJSON("admin/unfollow_instance/?url="+e).catch(error=>console.error(error));
        row.remove();
    });
    commandCell.appendChild(withdrawButton);
    row.appendChild(nameCell);
    row.appendChild(commandCell);
    followingTable.appendChild(row);
});
const followingInput = document.getElementById('followingInput');
const followingButton = document.getElementById('followingButton');
followingButton.addEventListener('click', async e =>  {
    const inp = encodeURIComponent(followingInput.value);
    const response = await fetchJSON("admin/follow_instance/?url="+inp).catch(error=>console.error(error));
    const row = createElement('tr','');
    const nameCell = createElement('td', null, followingInput.value);
    const commandCell = createElement('td', null, '');
    const unfollowButton = createElement('button', null, 'Withdraw');
    unfollowButton.addEventListener('click', async e => {
        const response = await fetchJSON("admin/unfollow_instance/?url="+inp).catch(error=>console.error(error));
        row.remove();
    });
    commandCell.appendChild(unfollowButton);
    row.appendChild(nameCell);
    row.appendChild(commandCell);
    followingTable.appendChild(row);
});

instance_settings.followers.forEach(e => {
    const row = createElement('tr','');
    const nameCell = createElement('td', null, e);
    const commandCell = createElement('td', null, '');

    const removeButton = createElement('button', null, 'Remove');
    removeButton.addEventListener('click', async ve => {
        const response = await fetchJSON("admin/remove_instance/?url="+e).catch(error=>console.error(error));
        row.remove();
    });
    commandCell.appendChild(removeButton);
    row.appendChild(nameCell);
    row.appendChild(commandCell);
    followerTable.appendChild(row);
});
instance_settings.pending_followers.forEach(e => {
    const row = createElement('tr','');
    const nameCell = createElement('td', null, e);
    const commandCell = createElement('td', null, '');
    const acceptButton = createElement('button', null, 'Accept');
    acceptButton.addEventListener('click', async ve => {
        const response = await fetchJSON("admin/accept_instance/?url="+e).catch(error=>console.error(error));
    });
    const rejectButton = createElement('button', null, 'Reject');
    rejectButton.addEventListener('click', async ve => {
        const response = await fetchJSON("admin/reject_instance/?url="+e).catch(error=>console.error(error));
        row.remove();
    });
    commandCell.appendChild(acceptButton);
    commandCell.appendChild(rejectButton);
    row.appendChild(nameCell);
    row.appendChild(commandCell);
    followerTable.appendChild(row);
});


const blockInstanceInput = document.getElementById('blockInstanceInput');
const blockInstanceButton = document.getElementById('blockInstanceButton');
const blockInstanceTable = document.getElementById('blockInstanceTable');

blockInstanceButton.addEventListener('click', async e => {
    const inp = encodeURIComponent(blockInstanceInput.value);
    const response = await fetchJSON("admin/block_instance?block=true&url="+inp).catch(error=>console.error(error));
    const row = createElement('tr','');
    const nameCell = createElement('td', null, blockInstanceInput.value);
    const commandCell = createElement('td', null, '');
    const unfollowButton = createElement('button', null, 'Unblock');
    unfollowButton.addEventListener('click', async e => {
        const response = await fetchJSON("admin/block_instance?block=false&url="+inp).catch(error=>console.error(error));
        row.remove();
    });
    commandCell.appendChild(unfollowButton);
    row.appendChild(nameCell);
    row.appendChild(commandCell);
    blockInstanceTable.appendChild(row);
});

(instance_settings.blocked_instances ?? []).forEach(e => {
    const row = createElement('tr','');
    const nameCell = createElement('td', null, e);
    const commandCell = createElement('td', null, '');
    const unblockButton = createElement('button', null, 'Unblock');
    unblockButton.addEventListener('click', async f => {
        const response = await fetchJSON("admin/block_instance?block=false&url="+e).catch(error=>console.error(error));
        row.remove();
    });
    commandCell.appendChild(unblockButton);
    row.appendChild(nameCell);
    row.appendChild(commandCell);
    blockInstanceTable.appendChild(row);
});

const blockUsersInput = document.getElementById('blockUsersInput');
const blockUsersButton = document.getElementById('blockUsersButton');
const blockUsersTable = document.getElementById('blockUsersTable');

blockUsersButton.addEventListener('click', async e => {
    const inp = encodeURIComponent(blockUsersInput.value);
    const response = await fetchJSON("admin/block_user?block=true&user="+inp).catch(error=>console.error(error));
    const row = createElement('tr','');
    const nameCell = createElement('td', null, blockUsersInput.value);
    const commandCell = createElement('td', null, '');
    const unfollowButton = createElement('button', null, 'Unblock');
    unfollowButton.addEventListener('click', async e => {
        const response = await fetchJSON("admin/block_user?block=false&user="+inp).catch(error=>console.error(error));
        row.remove();
    });
    commandCell.appendChild(unfollowButton);
    row.appendChild(nameCell);
    row.appendChild(commandCell);
    blockUsersTable.appendChild(row);
});

(instance_settings.blocked_users ?? []).forEach(e => {
    const row = createElement('tr','');
    const nameCell = createElement('td', null, e);
    const commandCell = createElement('td', null, '');
    const unblockButton = createElement('button', null, 'Unblock');
    unblockButton.addEventListener('click', async f => {
        const response = await fetchJSON("admin/block_user?block=false&user="+e).catch(error=>console.error(error));
        row.remove();
    });
    commandCell.appendChild(unblockButton);
    row.appendChild(nameCell);
    row.appendChild(commandCell);
    blockUsersTable.appendChild(row);
});
