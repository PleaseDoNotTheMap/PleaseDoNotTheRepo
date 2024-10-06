import Globe from 'globe.gl';
import * as THREE from '//unpkg.com/three/build/three.module.js';

import {MTLLoader} from 'three/addons/loaders/MTLLoader.js';
import {OBJLoader} from 'three/addons/loaders/OBJLoader.js';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';

const globe = Globe({animateIn:false});
const markerSvg = `<svg viewBox="-4 0 36 36">
  <path fill="currentColor" d="M14,0 C21.732,0 28,5.641 28,12.6 C28,23.963 14,36 14,36 C14,36 0,24.064 0,12.6 C0,5.641 6.268,0 14,0 Z"></path>
  <circle fill="black" cx="14" cy="14" r="7"></circle>
</svg>`;

const coordinates = document.getElementById('coordinates');

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
      coordinates.value = `${lat}, ${lng}`


 
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
    color: 'white',
    size: 30,
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
  .pointAltitude(0.1)
  .objectLat('lat')
  .objectLng('lng')
  .objectAltitude('alt')
  .objectRotation(d => d.rot)
  .objectFacesSurface(false)
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


  coordinates.addEventListener('change', function() {
    const [lat, lng] = coordinates.value.split(',').map(parseFloat);
    pinSet[0].lat = lat;
    pinSet[0].lng = lng;
    globe.htmlElementsData(pinSet);
    globe.pointOfView({ lat, lng, altitude: 2.5 }, 500);
  });

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

let sat = [{
  lat: 0,
  lng: 0,
  alt: 0.1,
  name: 'Landsat 9',
  rot: { x: 0, y: 90, z: 0},
}];


const renderSatellite = function() {
//  const mtlLoader = new MTLLoader();
  const loader = new GLTFLoader();
  loader.load('/static/pleasedonotcat.glb', (obj) => {
      globe.objectThreeObject(obj.scene);
    }, undefined, function(error) {
      console.error(error);
    });
}
renderSatellite();
globe.objectsData(sat);

let allPaths = null;
let path = null;
let pathIndex = 1;
let allPathsIndex = 1;

const getPaths = function() {
  fetch("/static/paths.json")
    .then(response => response.json())
    .then(data => {
      allPaths = data;
      path = data[1];
      globe.pointsData(path);
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

window.setInterval(function(){
  // Update satellite location
  if (pathIndex >= path.length) {
    path = allPaths[++allPathsIndex];
    globe.pointsData(path);
    pathIndex = 1;
    sat[0].lat = path[1][1];
    sat[0].lng = path[1][0];
    globe.objectsData(sat);
    return;
  }
  sat[0].lng = path[pathIndex][0];
  sat[0].lat = path[pathIndex][1];
  pathIndex++;
  globe.objectsData(sat);
}, 10);
