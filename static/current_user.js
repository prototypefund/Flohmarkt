import { fetchJSON } from "./utils.js";

const nop = async () => null;

const token = JSON.parse(window.sessionStorage.getItem('parsedToken'));
var get_user_func = nop;
if (token != null && token != "null") {
    get_user_func = fetchJSON('user/' + token.user_id);
}

export const getCurrentUser = get_user_func;

export const isCurrentUser = message => {
    const actor_url = new URL(message.attributedTo);
    const own_url = new URL(window.location);
    if (actor_url.host !=  own_url.host) {
        return false;
    }
    return message.attributedTo.endsWith("/"+token.username);
};

