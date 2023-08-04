import { spritePath } from '../globals/path.js';

export function updateSVG(svg, oldIcon, newIcon) {
    svg.classList.replace(oldIcon, newIcon);
    svg.firstElementChild.href.baseVal = spritePath + newIcon;
}
