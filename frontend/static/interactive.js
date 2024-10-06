import Globe from 'globe.gl';
import * as THREE from '//unpkg.com/three/build/three.module.js';

import {MTLLoader} from 'three/addons/loaders/MTLLoader.js';
import {OBJLoader} from 'three/addons/loaders/OBJLoader.js';

const globe = Globe({animateIn:false});
const markerSvg = `<svg viewBox="-4 0 36 36">
  <path fill="currentColor" d="M14,0 C21.732,0 28,5.641 28,12.6 C28,23.963 14,36 14,36 C14,36 0,24.064 0,12.6 C0,5.641 6.268,0 14,0 Z"></path>
  <circle fill="black" cx="14" cy="14" r="7"></circle>
</svg>`;


function dragElement(elmnt) {
  var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
  var startTop = 0;
  var startLeft = 0;
  if (document.getElementById(elmnt.id + "header")) {
    // if present, the header is where you move the DIV from:
    document.getElementById(elmnt.id + "header").onmousedown = dragMouseDown;
  } else {
    // otherwise, move the DIV from anywhere inside the DIV:
    elmnt.onmousedown = dragMouseDown;
  }

  function dragMouseDown(e) {
    e = e || window.event;
    e.preventDefault();
    // get the mouse cursor position at startup:
    pos3 = e.clientX;
    pos4 = e.clientY;
    
    document.onmouseup = closeDragElement;
    // call a function whenever the cursor moves:
    document.onmousemove = elementDrag;

    startTop = elmnt.style.top;
    startLeft = elmnt.style.left;
  }

  function elementDrag(e) {
    e = e || window.event;
    e.preventDefault();
    // calculate the new cursor position:
    pos1 = pos3 - e.clientX;
    pos2 = pos4 - e.clientY;
    pos3 = e.clientX;
    pos4 = e.clientY;
    // set the element's new position:
    elmnt.style.top = (elmnt.offsetTop - pos2) + "px";
    elmnt.style.left = (elmnt.offsetLeft - pos1) + "px";
  }

  function closeDragElement(e) {
    // stop moving when mouse button is released:
    document.onmouseup = null;
    document.onmousemove = null;
    elmnt.style.top = startTop;
    elmnt.style.left = startLeft;
   
    try {
      const { lat, lng } = globe.toGlobeCoords(e.clientX, e.clientY);
   pinSet[0].lat = lat;
    pinSet[0].lng = lng;
    globe.htmlElementsData(pinSet);

 
    } catch (e) {
      // Not on globe
      return;
    }
      }
}

let pinSet = [
  {
    lat: 0,
    lng: 0,
    alt: 0,
    color: 'red',
    size: 20,
  }
]

globe(document.getElementById('globe'), {})
  .globeImageUrl("https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg")
  .backgroundImageUrl('https://unpkg.com/three-globe/example/img/night-sky.png')
  .polygonCapColor(feat => 'rgba(200, 0, 0, 0.6)')
  .polygonSideColor(() => 'rgba(0, 100, 0, 0.05)')
  .polygonAltitude(5)
  .polygonStrokeColor(() => '#111')
  .lineHoverPrecision(0)
  .pointLng(d => d[0])
  .pointLat(d => d[1])
  .objectLat('lat')
  .objectLng('lng')
  .objectAltitude('alt')
  .objectFacesSurface(false)
  .objectLabel('name')
  .htmlElementsData(pinSet)
  .htmlElement(d => {
    const el = document.createElement('div');
    el.innerHTML = markerSvg;
    el.style.color = d.color;
    el.style.width = `${d.size}px`;

    el.style['pointer-events'] = 'auto';
    el.style.cursor = 'pointer';
    dragElement(el);
    return el;
  })
  .htmlTransitionDuration([0]);


// Apply custom globe material
const globeMaterial = globe.globeMaterial();
globeMaterial.bumpScale = 15;

new THREE.TextureLoader().load('https://unpkg.com/three-globe/example/img/earth-water.png', texture => {
  globeMaterial.specularMap = texture;
  globeMaterial.specular = new THREE.Color('grey');
  globeMaterial.shininess = 20;
});

// Manually add a directional light
const scene = globe.scene(); // Access globe's internal Three.js scene

const directionalLight = globe.lights().find(light => light.type === 'DirectionalLight');
directionalLight.position.set(1, 1, 1); // Adjust position as needed
scene.add(directionalLight);

// const ambientLight = new THREE.AmbientLight(0xffffff, 5); // Soft white light
// scene.add(ambientLight);
const addClouds = function (){
  const CLOUD_URL = "../images/clouds.png"
  const ALTITUDE = 0.004;
  const cloud_rotation_v = -0.006;

  new THREE.TextureLoader().load(CLOUD_URL, cloudsTexture => {
    const clouds = new THREE.Mesh(
      new THREE.SphereGeometry(globe.getGlobeRadius() * (1 + ALTITUDE), 75, 75),
      new THREE.MeshPhongMaterial({ map: cloudsTexture, transparent: true })

    );
    globe.scene().add(clouds);

    (function rotateClouds(){
      clouds.rotation.y += cloud_rotation_v * Math.PI /180;
      requestAnimationFrame(rotateClouds);
    })();
  });
}

addClouds();

const renderSatellite = function() {
  const mtlLoader = new MTLLoader();
  mtlLoader.load('/static/pleasedontsatellite.mtl', (mtl) => {
    mtl.preload();
    const objLoader = new OBJLoader();
    objLoader.setMaterials(mtl);
    objLoader.load('/static/pleasedontsatellite.obj', (obj) => {
      globe.objectThreeObject(obj);
      globe.objectsData([{
        lat: 0,
        lng: 0,
        alt: 1,
        lbl: 'Satellite',
      }]);
    }, undefined, function(error) {
      console.error(error);
    });
  });
}
renderSatellite();

const getPaths = function() {
  fetch("/static/paths.json")
    .then(response => response.json())
    .then(data => {
      console.log(data[1]);
      globe.pointsData(data[1]);
    });
}

getPaths();



const rotate = function(){
  globe.controls().autoRotate = true;
  globe.controls().autoRotateSpeed = 0.4;

}

rotate();

window.onresize = function(event) {
  globe.width(window.innerWidth);
  globe.height(window.innerHeight);
};

const coordinates = document.getElementById('coordinates');
coordinates.addEventListener('change', function() {
  const [lat, lng] = coordinates.value.split(',').map(parseFloat);
  pinSet[0].lat = lat;
  pinSet[0].lng = lng;
  globe.htmlElementsData(pinSet);
  globe.pointOfView({ lat, lng, altitude: 2.5 }, 500);
});

// Get references to the autocomplete input and place info elements
const autocompleteInput = document.getElementById('locationInput');

// Set up Google Places Autocomplete
const autocomplete = new google.maps.places.Autocomplete(autocompleteInput);

// Listen for the place_changed event
google.maps.event.addListener(autocomplete, 'place_changed', function () {
    const place = autocomplete.getPlace();
    if (place && place.geometry) {
        const address = place.formatted_address;
        const latitude = place.geometry.location.lat();
        const longitude = place.geometry.location.lng();
        pinSet[0].lat = latitude;
        pinSet[0].lng = longitude;
        globe.htmlElementsData(pinSet);
        globe.pointOfView({ lat: latitude, lng: longitude, altitude: 0.5 }, 500);
        coordinates.value = `${latitude}, ${longitude}`;
    }
});


