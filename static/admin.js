import { fetchJSON } from "./utils.js";
import { createElement } from "./create/element.js";
import { createImg } from "./create/img.js";

const users = await fetchJSON('users');

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
    userContainer.appendChild(createImg(user.src, user.name, 'avatar circle'));
    userContainer.appendChild(createElement('div', null, user.name));
    usersFragment.appendChild(userContainer);
    
    const adminInput = createElement('input');
    adminInput.type = 'checkbox';
    adminInput.checked = user.role.admin;
    usersFragment.appendChild(adminInput);

    const modInput = createElement('input');
    modInput.type = 'checkbox';
    modInput.checked = user.role.mod;
    usersFragment.appendChild(modInput);
    
    const controlsContainer = createElement('div', 'd-flex');
    controlsContainer.appendChild(createElement('button', null, 'Ban'));
    controlsContainer.appendChild(createElement('button', null, 'Delete'));
    usersFragment.appendChild(controlsContainer);
});

const gridAdmin = document.querySelector('.grid__admin');
window.requestAnimationFrame(() => {
    gridAdmin.appendChild(usersFragment);
});
