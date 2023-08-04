import { createNotification } from "../create/notification.js";

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
                createNotification({
                    "head": "Flohmarkt - New message",
                    "msg": "On: "+ msg["url"]
                });
            } else if (msg["type"] == "conversation"){
                this.#triggerEvent("conversation", msg);
            } else {
                createNotification(msg);
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
