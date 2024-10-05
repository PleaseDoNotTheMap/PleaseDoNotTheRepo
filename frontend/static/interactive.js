import Globe from 'globe.gl';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import * as THREE from '//unpkg.com/three/build/three.module.js';

const globe = Globe({animateIn:false});

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
      .objectLabel('name');

const getScenes = async function() {
  fetch("/static/small.geojson")
    .then(response => response.json())
    .then(data => {
      globe.polygonsData(data);
    });
}

getScenes();

const renderSatellite = function() {
  let loader = new GLTFLoader();

  loader.load('/static/satellite.glb', function(gltf) {
    globe.objectThreeObject(gltf.scene);
    globe.objectsData([{
      lat: 0,
      lng: 0,
      alt: 1,
      lbl: 'Satellite',
    }]);
  }, undefined, function(error) {
    console.error(error);
  });
}

renderSatellite();

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