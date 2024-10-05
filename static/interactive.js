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

getScenes();

window.onresize = function(event) {
  globe.width(window.innerWidth);
  globe.height(window.innerHeight);
};

