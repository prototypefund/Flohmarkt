import { createSmallAvatar } from "./create/avatar.js";
import "./notification.js";

const token = window.sessionStorage.getItem('token');

const notifications = document.createElement('notification-container');
document.body.appendChild(notifications)

const notify = (msg) => {
    if (!("Notification" in window)) {
        return;
    }
    if (Notification.permission === "granted") {
        const notification = new Notification(msg["head"], {body:msg["msg"]});
    }
}

export class Incoming {
    constructor() {
        this.websocket = new WebSocket(
          "wss://"+window.location.host+"/ws"
        );
        this.websocket.addEventListener("open", e => {
          this.websocket.send(token);
        });
        this.websocket.addEventListener('message', e=> {
            const msg = JSON.parse(e.data);
            if (msg["type"] == "Note") {
                this.#triggerEvent("message", msg);
                notify({
                    "head": "Flohmarkt - New message",
                    "msg": "On: "+ msg["url"]
                });
            } else if (msg["type"] == "conversation"){
                this.#triggerEvent("conversation", msg);
            } else {
                notify(msg);
            }
        });
        this.events = {
            message: [],
            conversation: []
        }
    }

    addEventListener(e, callable) {
        this.events[e].push(callable);
    }

    #triggerEvent(e, data) {
        this.events[e].forEach(async e=>{
            let r = e(data);
            if (r.constructor.name == "Promise") {
                r = await r;
            }
            return r
        });
    }
}

export const incoming = new Incoming();

const token_expiry_check = () => {
    if (token != undefined && token != "null" && typeof(token) === 'string') {
        const parsedToken = JSON.parse(window.sessionStorage.getItem('parsedToken'));
        const cmptime = Date.now() / 1000; // js yields milliseconds
        if (parsedToken.exp < cmptime) {
            window.sessionStorage.setItem('parsedToken', "null");
            window.sessionStorage.setItem('token', "null");
            window.location = window.location;
        }
    }
    window.setTimeout(token_expiry_check, 10000);
};
window.setTimeout(token_expiry_check, 100);

const showElements = [];
if (token != undefined && token != "null" && typeof(token) === 'string') {
    const parsedToken = JSON.parse(window.sessionStorage.getItem('parsedToken'));
    const username = parsedToken.username;
    const detailsListItem = document.getElementById('details-list-item');
    detailsListItem.querySelector('.details-menu span').append(username);
    detailsListItem.querySelector('.details-menu .l-profile').href = '/~' + username;
    detailsListItem.querySelector('.details-menu .l-messaging').href = '/messages';
    if (parsedToken.admin === true || parsedToken.moderator === true) {
        detailsListItem.querySelector('.details-menu .l-site-moderation').href = '/moderation';
    } else {
        detailsListItem.querySelector('.details-menu .s-site-moderation').style.display = 'none';
    }
    if (parsedToken.admin === true) {
        detailsListItem.querySelector('.details-menu .l-site-admin').href = '/admin';
    } else {
        detailsListItem.querySelector('.details-menu .s-site-admin').style.display = 'none';
    }
    headerAvatar();

    showElements.push(detailsListItem);
    showElements.push(document.getElementById('new-list-item'));
} else {
    showElements.push(document.getElementById('register-list-item'));
    showElements.push(document.getElementById('login-list-item'));
}

export function updateAvatar(avatar) {
    const token = window.sessionStorage.getItem('token');
    if (token != undefined && token != "null" && typeof(token) === 'string') {
        const parsedToken = JSON.parse(window.sessionStorage.getItem('parsedToken'));
        parsedToken.avatar = avatar;
        const new_token = JSON.stringify(parsedToken);
        window.sessionStorage.setItem('parsedToken', new_token);
        headerAvatar();
    }
}

function headerAvatar() {
    const token = window.sessionStorage.getItem('token');
    if (token != undefined && token != "null" && typeof(token) === 'string') {
        const avatarslot = document.getElementById('avatar-slot');
        avatarslot.innerHTML = '';
        const parsedToken = JSON.parse(window.sessionStorage.getItem('parsedToken'));
        avatarslot.appendChild(createSmallAvatar(parsedToken));
    }
}

window.requestAnimationFrame(() => {
    showElements.forEach(element => element.classList.remove('invisible') )
});
