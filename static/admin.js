import { fetchJSON, postJSON } from "./utils.js";
import { createElement } from "./create/element.js";
import { createImage } from "./create/image.js";

const users = await fetchJSON('user/');

const instance_settings = await fetchJSON('admin/');

const usersFragment = document.createDocumentFragment();

const menuUsername = createElement('div', null, 'Username');
usersFragment.appendChild(menuUsername);
const menuAdmin = createElement('div', null, 'Admin');
usersFragment.appendChild(menuAdmin);
const menuMod = createElement('div', null, 'Mod');
usersFragment.appendChild(menuMod);
const menuControls = createElement('div', null, 'Controls');
usersFragment.appendChild(menuControls);

users.forEach(user => {
    const userContainer = createElement('div', 'd-flex');
    userContainer.appendChild(createImage(user.avatar || 'user.svg', user.name, 'avatar circle'));
    userContainer.appendChild(createElement('div', null, user.name));
    usersFragment.appendChild(userContainer);
    
    const adminInput = createElement('input');
    adminInput.type = 'checkbox';
    adminInput.checked = user.admin;
    adminInput.addEventListener("change", async e => {
        const response = (await fetchJSON("admin/toggle_admin/"+user.id));
        adminInput.checked = response.admin;
    });
    usersFragment.appendChild(adminInput);

    const modInput = createElement('input');
    modInput.type = 'checkbox';
    modInput.checked = user.moderator;
    modInput.addEventListener("change", async e => {
        const response = (await fetchJSON("admin/toggle_moderator/"+user.id));
        modInput.checked = response.moderator;
    });
    usersFragment.appendChild(modInput);
    
    const controlsContainer = createElement('div', 'd-flex');
    controlsContainer.appendChild(createElement('button', null, 'Ban'));
    controlsContainer.appendChild(createElement('button', null, 'Delete'));
    usersFragment.appendChild(controlsContainer);
});

const instanceFragment = document.createDocumentFragment();

const instanceHeading = createElement('h2', null, 'Site Settings');
instanceFragment.appendChild(instanceHeading);
const instanceForm = createElement('form', null, '');
const instanceRulesTextArea = createElement('textarea');
instanceRulesTextArea.name = "instance_rules";
const instanceAboutTextArea = createElement('textarea');
instanceAboutTextArea.name = "instance_about";
const instanceRulesLabel = createElement('label', null, 'Rules');
const instanceAboutLabel = createElement('label', null, 'About');
instanceRulesLabel.for = "instance_rules";
instanceAboutLabel.for = "instance_about";
const instanceSaveButton = createElement('button', null, 'Save');
instanceSaveButton.addEventListener('click', event => {
    event.preventDefault();

    const formData = new FormData(instanceForm);
    console.log(formData);
    postJSON("/api/v1/admin/", {
        coordinates: formData.get('instance_coordinates'),
        perimeter: formData.get('instance_perimeter'),
        rules: formData.get('instance_rules'),
        about: formData.get('instance_about'),
    })
    .then(async data => {
	// reload
    });
});
const instanceCoordinatesInput = createElement('input');
instanceCoordinatesInput.name = "instance_coordinates";
const instanceRangeInput = createElement('input');
instanceRangeInput.name = "instance_perimeter";
const instanceCoordinatesLabel = createElement('label', null, 'Location of your Site (lat:lon e.g. 51.213:23.24)');
const instanceRangeLabel = createElement('label', null, 'Range for your Site in km'
);
instanceCoordinatesLabel.for = "instance_coordinates";
instanceRangeLabel.for = "instance_perimeter";

instanceForm.appendChild(instanceCoordinatesLabel);
instanceForm.appendChild(instanceCoordinatesInput);
instanceForm.appendChild(instanceRangeLabel);
instanceForm.appendChild(instanceRangeInput);
instanceForm.appendChild(instanceRulesLabel);
instanceForm.appendChild(instanceRulesTextArea);
instanceForm.appendChild(instanceAboutLabel);
instanceForm.appendChild(instanceAboutTextArea);
instanceForm.appendChild(instanceSaveButton);
instanceFragment.appendChild(instanceForm);

const followFragment = document.createDocumentFragment();

const followHeading = createElement('h2', null, 'Instance Federation');

const followingHeading = createElement('h3', null, 'Following');
const followingList = createElement('ul');
instance_settings.following.forEach(e => {
    const listElement = createElement('li', null, e);
    const unfollowButton = createElement('button', null, 'Unfollow');
    unfollowButton.addEventListener('click', async ve => {
        const response = await fetchJSON("admin/unfollow_instance/?url="+e).catch(error=>console.error(error));
	listElement.remove();
    });
    listElement.appendChild(unfollowButton);
    followingList.appendChild(listElement);
});
const followingInput = createElement('input');
const followingButton = createElement('button', null, 'Follow');
followingButton.addEventListener('click', async e =>  {
    const inp = encodeURIComponent(followingInput.value);
    const response = await fetchJSON("admin/follow_instance/?url="+inp).catch(error=>console.error(error));
    const listElement = createElement('li', null, followingInput.value);
    const unfollowButton = createElement('button', null, 'Unfollow');
    unfollowButton.addEventListener('click', async e => {
        const response = await fetchJSON("admin/unfollow_instance/?url="+inp).catch(error=>console.error(error));
	listElement.remove();
    });
    listElement.appendChild(unfollowButton);
    followingList.appendChild(listElement);
});
followFragment.append(followingHeading);
followFragment.append(followingList);
followFragment.append(followingInput);
followFragment.append(followingButton);

const followersHeading = createElement('h3', null, 'Followers');
const followersList = createElement('ul');
instance_settings.followers.forEach(e => {
    followersList.appendChild(createElement('li', null, e));
});
followFragment.append(followersHeading);
followFragment.append(followersList);

const gridAdmin = document.querySelector('.grid__admin');
window.requestAnimationFrame(() => {
    gridAdmin.appendChild(usersFragment);
    gridAdmin.appendChild(instanceFragment);
    gridAdmin.appendChild(followFragment);
});
