import { postForm } from './utils.js';

const setupForm = document.getElementById('setup-form');
const setupBtn = setupForm.querySelector('button');
setupBtn.addEventListener('click', async event => {
    event.preventDefault();

    var data = await postForm(setupForm);
    console.log(data);
    if (data["ok"]) {
        window.location.pathname = '/';
    }
});

const map = L.map('map').setView(instance_settings.coordinates, 9);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);
const map_circle = L.circle(instance_settings.coordinates, {
    color: 'red',
    fillColor: '#f03',
    fillOpacity: 0.5,
    radius: instance_settings.perimeter*1000
}).addTo(map);
instanceRangeInput.addEventListener('change', e=> {
    map_circle.setRadius(instanceRangeInput.value * 1000);
});
const setCoordinates = e => {
    map_coords = e.latlng;
    map_circle.setLatLng(e.latlng);
}
map.on('click', setCoordinates);

/*let inputValid = 0,
    password;

setupForm.querySelectorAll('input').forEach((input, index) => {
    input.addEventListener('input', function() {
        let valid;
        switch (this.name) {
            case 'username':
                valid = this.value !== '';
                break;
            case 'email':
                // https://stackoverflow.com/a/9204568/5764676
                valid = /^\S+@\S+\.\S+$/.test(this.value);
                break;
            case 'password':
                valid = this.value !== '';
                password = this.value;
                break;
            case 'password-repeat':
                valid = this.value === password;
                break;
        }
        const mask = 1 << index;
        inputValid = valid ? inputValid | mask : inputValid & ~mask;
        setupBtn.disabled = inputValid !== 15; // 1111
    });
});*/
