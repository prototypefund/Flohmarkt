import { createImage } from "./image.js";

export function createAvatar(user) {
    if (user.avatar == null) {
        return createImage("/static/img/user.svg", user.name, 'avatar circle');
    } else if (user.avatar.startsWith("http")) {
        return createImage(user.avatar, user.name, 'avatar circle');
    } else {
        return createImage("/api/v1/image/"+user.avatar, user.name, 'avatar circle');
    }
}
export function createSmallAvatar(user) {
    if (user.avatar == null) {
        return createImage("/static/img/user.svg", user.name, 'small_avatar circle');
    } else if (user.avatar.startsWith("http")) {
        return createImage(user.avatar, user.name, 'small_avatar circle');
    } else {
        return createImage("/api/v1/image/"+user.avatar, user.name, 'small_avatar circle');
    }
}


