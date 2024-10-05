import Globe from 'globe.gl';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import * as THREE from '//unpkg.com/three/build/three.module.js';

const globe = Globe({animateIn:false});

import {MTLLoader} from 'three/addons/loaders/MTLLoader.js';
import {OBJLoader} from 'three/addons/loaders/OBJLoader.js';

const globe = Globe();
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
  .polygonAltitude(0.06)
  .polygonStrokeColor(() => '#111')
  .lineHoverPrecision(0)
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

const getScenes = async function() {
  fetch("/static/small.geojson")
    .then(response => response.json())
    .then(data => {
      globe.polygonsData(data);
    });
}

const renderSatellite = async function() {
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
await renderSatellite();

const rotate = function(){
  globe.controls().autoRotate = true;
  globe.controls().autoRotateSpeed = 0.4;

}

rotate();

window.onresize = function(event) {
  globe.width(window.innerWidth);
  globe.height(window.innerHeight);
};

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
