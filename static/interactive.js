const globe = Globe();
globe(document.getElementById('glb-container'), {
        // Globe options
}).globeImageUrl("http://unpkg.com/three-globe/example/img/earth-blue-marble.jpg");

window.onresize = function(event) {
  globe.width(window.innerWidth);
  globe.height(window.innerHeight);
};

const super_unsafe = 'Ek1K@zW2V9_WDLBDvuUi3aAxp26NAgY1vdlSHC1Hm72grUgHs21PDFr@aCPnhRRF';

const getApiToken = function() {
  fetch("https://m2m.cr.usgs.gov/api/api/json/stable/login-token",
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: 'receive@leozqi.com',
        password: super_unsafe
      })
    }
  ).then(response => response.json())
  .then(data => {
    console.log(data);
  });
};

getApiToken();

