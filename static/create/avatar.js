import { createImage } from "./image.js";
import { createElement } from "./element.js";

function createNoAvatarCircle(small) {
    const av = createElement('div', '', '');
    av.style.height=small?"32px":"48px";		
    av.style.width=small?"32px":"48px";	
    av.classList = [small?"small_avatar":"avatar"];	
    av.style.display="inline-block";		
    av.style.backgroundColor="crimson";
    return av;
}

export function createAvatar(user) {
    if (user.avatar == null) {
        return createNoAvatarCircle(false);
    } else if (user.avatar.startsWith("http")) {
        return createImage(user.avatar, user.name, 'avatar circle');
    } else {
        return createImage("/api/v1/image/"+user.avatar, user.name, 'avatar circle');
    }
}
export function createSmallAvatar(user) {
    if (user.avatar == null) {
        return createNoAvatarCircle(true);
    } else if (user.avatar.startsWith("http")) {
        return createImage(user.avatar, user.name, 'small_avatar circle');
    } else {
        return createImage("/api/v1/image/"+user.avatar, user.name, 'small_avatar circle');
    }
}


