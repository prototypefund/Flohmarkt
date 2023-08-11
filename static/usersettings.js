import { fetchJSON, postJSON, deleteCall } from "./utils.js";
import { initTabs } from "./tabs.js";
import "./create/image_uploader.js";

initTabs();

const [currentUser] = await Promise.all([
    getCurrentUser
]);

const deleteButton = document.getElementById('delete-btn');
deleteButton.addEventListener('click', async e => {
    if (prompt("Please enter your username to confirm account deletion!") == user.name) {
        const res = await deleteCall('/api/v1/user/'+user.id);
        if (res == true) {
            window.sessionStorage.setItem('token',null);
            window.sessionStorage.setItem('parsedToken',null);
            window.location = "/";
        }
    } else {
        alert("Wrong usename. Aborting account deletion");
    }
});

const notificationButton = document.getElementById('notification-btn');
notificationButton.addEventListener('click', ()=>{
    if (!("Notification" in window)) {
        return;
    }
    if (Notification.permission !== "granted") {
        Notification.requestPermission();
    }
});
