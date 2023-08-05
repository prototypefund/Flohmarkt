import { createSmallAvatar } from "./create/avatar.js";
import "./notification.js";

const token = window.sessionStorage.getItem('token');

const showElements = [];
const hideElements = [];
if (token != undefined && token != "null" && typeof(token) === 'string') {
    const parsedToken = JSON.parse(window.sessionStorage.getItem('parsedToken'));
    
    // headerAvatar
    const avatarslot = document.getElementById('avatar-slot');
    avatarslot.innerHTML = '';
    avatarslot.appendChild(createSmallAvatar(parsedToken));

    // Token expiry check
    window.setInterval(function() {
        const cmptime = Date.now() / 1000; // js yields milliseconds
        if (parsedToken.exp < cmptime) {
            window.sessionStorage.setItem('parsedToken', "null");
            window.sessionStorage.setItem('token', "null");
            window.location = window.location;
        }
    }, 10000);
    // Menu button visibility
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
    showElements.push(detailsListItem);
    showElements.push(document.getElementById('new-list-item'));
    hideElements.push(document.getElementById('register-list-item'));
    hideElements.push(document.getElementById('login-list-item'));
} else {
    showElements.push(document.getElementById('register-list-item'));
    showElements.push(document.getElementById('login-list-item'));
}

window.requestAnimationFrame(() => {
    showElements.forEach(element => {
        element.hidden = false;
        element.classList.remove('invisible');
    });
    hideElements.forEach(element => element.hidden = true );
});
// Notifications
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
// WebSocket
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
