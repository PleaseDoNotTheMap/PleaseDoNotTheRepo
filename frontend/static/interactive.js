import Globe from 'globe.gl';

import {MTLLoader} from 'three/addons/loaders/MTLLoader.js';
import {OBJLoader} from 'three/addons/loaders/OBJLoader.js';

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

window.onresize = function(event) {
  globe.width(window.innerWidth);
  globe.height(window.innerHeight);
};

