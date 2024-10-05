import Globe from 'globe.gl';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';


const globe = Globe();

globe(document.getElementById('glb-container'), {
        // Globe options
})
  .globeImageUrl("http://unpkg.com/three-globe/example/img/earth-blue-marble.jpg")
  .polygonCapColor(feat => 'rgba(200, 0, 0, 0.6)')
  .polygonSideColor(() => 'rgba(0, 100, 0, 0.05)')
  .polygonAltitude(0.06)
  .polygonStrokeColor(() => '#111')
  .lineHoverPrecision(0)

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
    scene.add(gltf.scene);
  }, undefined, function(error) {
    console.error(error);
  });

  globe.objectsData([
    { type: 'satellite', lat: 0, lng: 0, altitude: 10}
  ]);
}

renderSatellite();

const rotate = function(){
  globe.controls().autoRotate = true;
  globe.controls().autoRotateSpeed = 0.4;

  const cloudurl= "http://unpkg.com/three-globe/example/img/clouds/clouds.png";

  const speed = -0.006;

}

rotate();

window.onresize = function(event) {
  globe.width(window.innerWidth);
  globe.height(window.innerHeight);
};

