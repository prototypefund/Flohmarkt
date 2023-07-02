import { postJSON } from './utils.js';

const setupForm = document.getElementById('setup-form');
const setupBtn = setupForm.querySelector('button');

var map_coords = null;

setupBtn.addEventListener('click', async event => {
    event.preventDefault();

    const key = document.getElementById('initkey').value;

    const formData = new FormData(setupForm);
    postJSON("/api/v1/admin/setup/"+key+"/", {
        username: formData.get('username'),
        email: formData.get('email'),
        password:formData.get('password'),
        instancename:formData.get('instancename'),
        coordinates: map_coords,
        perimeter: formData.get('perimeter'),
        
    })
    .then(async data => {
        window.location.pathname = '/';
    });
});

const instanceRangeInput = document.getElementById("perimeter");
const map = L.map('map').setView([52,13], 4);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);
var map_circle = null;
instanceRangeInput.addEventListener('change', e=> {
    map_circle.setRadius(instanceRangeInput.value * 1000);
});
const setCoordinates = e => {
    if (map_circle == null) {
        map_circle = L.circle(e.latlng, {
            color: 'red',
            fillColor: '#f03',
            fillOpacity: 0.5,
            radius: 10*1000
        }).addTo(map);
    } else {
        map_circle.setLatLng(e.latlng);
    }
    map_coords = e.latlng;
}
map.on('click', setCoordinates);

