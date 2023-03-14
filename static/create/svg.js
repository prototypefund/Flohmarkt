export function createSVG(src) {
    const icon = src.slice(0, -4); // remove .svg
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.classList.add('icon');
    svg.classList.add('icon--' + icon);
    svg.role = 'img';
    svg.setAttribute('aria-hidden', 'true');
    const use = document.createElementNS('http://www.w3.org/2000/svg', 'use');
    use.setAttribute(
      'href', 
      '/static/sprite.svg#' + icon);
    svg.appendChild(use);
    
    return svg;
}
