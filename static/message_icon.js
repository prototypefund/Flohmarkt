import { getCurrentUser } from "./current_user.js";
import { incoming } from "./app.js";
import { fetchJSON } from "./utils.js";
import { replaceSVG } from "./create/svg.js";

const user = await getCurrentUser;

const messageIcon = document.createElement('template');
messageIcon.innerHTML = `
<link rel="stylesheet" href="/static/utils.css">
<link rel="stylesheet" href="/static/icon.css">
<style>
    .message_icon {
        cursor: pointer;
    }
</style>
<span class="message_icon" aria-label="New messages">
<svg class="icon icon--mail" role="img">
    <use href="/static/sprite.svg#mail" class="usetag"></use>
</svg>
</span>
`;

class MessageIcon extends HTMLElement {
    constructor () {
        super();
        this._shadowRoot = this.attachShadow({mode:'open'});
        this._shadowRoot.appendChild(messageIcon.content.cloneNode(true));

        this.handler = null;
                
        this.outer = this._shadowRoot.querySelector('.message_icon');
        this.outer.addEventListener('click', this.openMessages.bind(this));
        this.messageicon = this._shadowRoot.querySelector('.icon');
        incoming.addEventListener('conversation', this.processIncoming.bind(this));
        incoming.addEventListener('message', this.processIncoming.bind(this));

        if (user["has_unread"] ?? false) {
            this.processIncoming();
        }
    }

    processIncoming() {
        replaceSVG(this.messageicon, 'mail', 'mail-filled');
        return true;
    }

    async openMessages () {
        let handler_successful = false;
        if (this.handler !== null) {
            handler_successful = this.handler();
        }
        if (!handler_successful) {
            await fetchJSON("user/"+user["id"]+"/mark_read");
            window.location = "/messages";
        }
    }

}

window.customElements.define('message-icon',MessageIcon);
