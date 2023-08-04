export function createNotification(msg) {
    if (!("Notification" in window)) {
        return;
    }
    if (Notification.permission === "granted") {
        const notification = new Notification(msg["head"], {body:msg["msg"]});
    }
}
