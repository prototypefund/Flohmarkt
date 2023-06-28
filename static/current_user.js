import { fetchJSON } from "./utils.js";

const nop = async () => null;

const token = JSON.parse(window.sessionStorage.getItem('parsedToken'));
var get_user_func = nop;
if (token != null) {
    get_user_func = fetchJSON('user/' + token.user_id);
}

export const getCurrentUser = get_user_func;
