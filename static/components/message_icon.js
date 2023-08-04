import { getCurrentUser } from "../current_user.js";
import { getIncoming } from "../globals/incoming.js";
import { fetchJSON } from "../utils.js";
import { updateSVG } from "../update/svg.js";

const user = await getCurrentUser;

const messageIcon = document.createElement('template');
messageIcon.innerHTML = `
<link rel="stylesheet" href="/static/css/utils.css">
<link rel="stylesheet" href="/static/css/icon.css">
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
        console.log(this.messageicon);
        const incoming = getIncoming();
        incoming.addEventListener('conversation', this.processIncoming.bind(this));
        incoming.addEventListener('message', this.processIncoming.bind(this));

        if (user["has_unread"] ?? false) {
            this.processIncoming();
        }
    }

    processIncoming() {
        updateSVG(this.messageicon, 'mail', 'mail-filled');
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
