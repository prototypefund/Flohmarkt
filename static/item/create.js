export function createItem(item) {
    const element = document.createElement('div');
    element.className = 'item';

    const image = document.createElement('img');
    image.src = item.image.src;
    image.alt = item.image.alt;
    element.appendChild(image);

    const link = document.createElement('a');
    link.className = 'stretched-link';
    link.href = '/~' + item.user + '/' + item.id;
    link.textContent = item.name;
    element.appendChild(link);

    const price = document.createElement('div');
    price.textContent = item.price + item.currency;
    
    element.appendChild(price);

    return element;
}
