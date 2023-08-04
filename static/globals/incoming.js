import { Incoming } from "../classes/incoming.js";

export function getIncoming() {
    if (window.incoming) {
        return window.incoming;
    }
    else {
        return window.incoming = new Incoming();
    }
}
