import Globe from 'globe.gl';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';


const globe = Globe();

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

window.onresize = function(event) {
  globe.width(window.innerWidth);
  globe.height(window.innerHeight);
};

