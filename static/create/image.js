import { createImg } from "./img.js";
import { createSVG } from "./svg.js";

export function createImage(src, alt=null, className=null) {
    return src.endsWith('.svg') ? createSVG(src.slice(0, -4)) : createImg(src, alt, className);
}
