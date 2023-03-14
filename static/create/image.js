import { createImg } from "./img.js";
import { createSVG } from "./svg.js";

export function createImage(src, alt, className=null) {
    return src.endsWith('.svg') ? createSVG(src) : createImg(src, alt, className);
}
