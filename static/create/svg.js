const spritePath = '/static/sprite.svg#';

export function createSVG(icon) {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.classList.add('icon', 'icon--' + icon);
    svg.role = 'img';
    svg.setAttribute('aria-hidden', 'true');
    const use = document.createElementNS('http://www.w3.org/2000/svg', 'use');
    use.setAttribute(
      'href', 
      spritePath + icon);
    svg.appendChild(use);
    
    return svg;
}

export function replaceSVG(svg, oldIcon, newIcon) {
    svg.classList.remove(oldIcon);
    svg.classList.add(newIcon);
    svg.firstElementChild.href.baseVal = spritePath + newIcon;
}
