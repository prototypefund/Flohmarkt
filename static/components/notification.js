const notification = document.createElement('template');

notification.innerHTML = `
    <style>
        .notification {
            position: absolute;
            right: 10px;
            top: 10px;
            width:100%;
            background-color: #aaff00;
            min.height:40px;
            padding:10px;
            color:#000;
        }
    </style>
    <div class="notification">
        <h3 class="nhead"></h3>
        <p class="msgbody"></p>
    </div>
`;

class Notification extends HTMLElement {
    constructor() {
        super();
        this._shadowRoot = this.attachShadow({mode:'open'});
        this._shadowRoot.appendChild(notification.content.cloneNode(true));
        this.msg = {head:"", msg: ""};

        this.msgbody = this._shadowRoot.querySelector('.msgbody');
        this.heading = this._shadowRoot.querySelector('.nhead');
        window.setTimeout(()=>{this.remove()}, 5000);
        this.addEventListener('click', ()=>{this.remove()});
    }

    setMsg(msg) {
        this.msg = msg;
        this.render();
    }

    render() {
        this.heading.innerHTML = this.msg.head;
        this.msgbody.innerHTML = this.msg.msg;
    }

}

window.customElements.define('notification-entry', Notification);


const notificationContainer = document.createElement('template');

notificationContainer.innerHTML = `
    <style>
        .notifications {
            position: absolute;
            right: 10px;
            top: 10px;
            width: 400px;
        }
    </style>
    <div class="notifications">
    </div>
`;

class NotificationContainer extends HTMLElement {
    constructor() {
        super();
        this._shadowRoot = this.attachShadow({mode:'open'});
        this._shadowRoot.appendChild(notificationContainer.content.cloneNode(true));

        this.notifications = this._shadowRoot.querySelector('.notifications');

    }
    addNotification(msg) {
        const notification = document.createElement('notification-entry');
        notification.setMsg(msg);
        this.notifications.appendChild(notification);
    }
}

window.customElements.define('notification-container', NotificationContainer);
