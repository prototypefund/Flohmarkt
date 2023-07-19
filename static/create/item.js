import { createImage } from "./image.js";
import { createLink } from "./link.js";
import { createElement } from "./element.js";
import { fetchJSON } from "../utils.js";

export function createItem(item, details=false, watching=[]) {
    var element = null;
    if (details) {
        element = createElement('aside', 'position-relative card-item-big');
    } else {
        element = createElement('aside', 'position-relative card-item');
    }
    if (item.images && item.images.length > 0) {
        const image = createImage("/api/v1/image/"+item.images[0], item.name, 'card-img-top w-100');
        image["image_idx"] = 0;
        if (details) {
            const g_left = createElement("div", "galery_left", "");
            g_left.appendChild(createElement("span", null, "<"));
            g_left.addEventListener('click', e => {
                image.image_idx--;
            if (image.image_idx < 0) { image.image_idx = item.images.length-1; }
                image.src = "/api/v1/image/"+item.images[image.image_idx%item.images.length];
                return true;
            });
            element.appendChild(g_left);
            const g_right = createElement("div", "galery_right", "")
            g_right.appendChild(createElement("span",null,">"));
            g_right.addEventListener('click', e => {
                image.image_idx++;
                image.src = "/api/v1/image/"+item.images[image.image_idx%item.images.length];
                return true;
            });
            element.appendChild(g_right);
        } else {
            element.addEventListener('mouseenter', e => {
                var callback = null;
                const f = ()=>{
                    image.image_idx++;
                    image.src = "/api/v1/image/"+item.images[(image.image_idx+1)%item.images.length];
                    callback = window.setTimeout(f, 1000);
                };
                callback = window.setTimeout(f, 1000);
                element.addEventListener('mouseout', e=> {
                    window.clearTimeout(callback);   
                });
            });
        }
        element.appendChild(image);
    } else {
        const image = createImage("/static/nopic.webp" , "no image", 'card-img-top w-100');
        element.appendChild(image);
    }
    var wrapper = null;
    if (details) {
	wrapper = createElement('div', 'p-2 card-item-text-big');
    } else {
	wrapper = createElement('div', 'p-2 card-item-text');
    }
    const container = createElement('div', 'd-flex justify-content-between');
    if (details) {
        container.appendChild(createElement("span", 'stretched-link', item.name));
    } else {
        container.appendChild(createLink("#", 'stretched-link', item.name));
        element.addEventListener('click', e=> {
            window.location = item.url;
            return true;
        });
    }
    container.appendChild(createElement('span', null, item.price /*+ item.currency*/));
    wrapper.appendChild(container);
    wrapper.appendChild(createElement('p', null, item.description));
    element.appendChild(wrapper);
    
    const watch_button = createElement('span', 'watch_button', '👁');
    if (watching.includes(item.id)) {
        watch_button.classList.add("watch_button_active");
    }
    watch_button.addEventListener('click', async e => {
        if (watch_button.classList.contains("watch_button_active")) {
            await fetchJSON('item/'+item.id+'/unwatch');
            watch_button.classList.remove("watch_button_active");
        } else {
            await fetchJSON('item/'+item.id+'/watch');
            watch_button.classList.add("watch_button_active");
        }
    });
    container.appendChild(watch_button);

    return element;
}
