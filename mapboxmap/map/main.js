import sources from "./mapSources.js";
import layers from "./mapLayers.js";

mapboxgl.accessToken =
  "pk.eyJ1IjoiZHZycGNvbWFkIiwiYSI6ImNrczZlNDBkZzFnOG0ydm50bXR0dTJ4cGYifQ.VaJDo9EtH2JyzKm3cC0ypA";

const map = new mapboxgl.Map({
  container: "map",
  style: "mapbox://styles/mapbox/light-v10",
  center: [-75.273611, 40.036894],
  zoom: 9.5,
});

//add geocoder/search bar using mapbox defaults
map.addControl(
  new MapboxGeocoder({
    accessToken: mapboxgl.accessToken,
    mapboxgl: mapboxgl,
    marker: false,
  })
);

//add mabox standard navigation controls; zoom in/out and rotate
map.addControl(new mapboxgl.NavigationControl());

const popupmessage = (e) => {
  var num = e.features.length;
  var properties = features[0].properties;

  let year = properties["Year"];
  let name = properties["Road Name"];
  let sr = properties["sr"];
  let length = properties["Miles Planned"];
  if (num <= 1)
    return `
    <h4>${name} /SR ${sr}</h4>
    <p>Planned Milage: ${length}</p>
    <p>Planned Year: ${year}</p>`;
  else
    return `
    <h4>${name} /SR ${sr}</h4>
    <p>Planned Milage: ${length}</p>
    <p>Planned Year: ${year}</p>
    <h4>Included in 2022 paving package</h4>
    `;
};

map.on("load", () => {
  //load sources
  for (const source in sources) map.addSource(source, sources[source]);
  //load layer styles
  for (const layer in layers) map.addLayer(layers[layer]);

  map.on("click", (e) => {
    const features = map.queryRenderedFeatures(e.point, {
      layers: ["planned-segments", "B12", "C12", "D13", "M11", "P12"],
    });
    let message = popupmessage;

    let popup = new mapboxgl.Popup({
      closeButton: false,
      className: "popup-style",
    });

    popup.setLngLat(e.lngLat).setHTML(message).addTo(map);
  });

  //popups
  map.on("mouseenter", "planned-segments", (e) => {
    map.getCanvas().style.cursor = "pointer";
  });
  map.on("mouseleave", "planned-segments", () => {
    map.getCanvas().style.cursor = "";
    let popup = document.getElementsByClassName("popup-style");

    if (popup.length) {
      popup[0].remove();
    }
  });
  //B12
  map.on("mouseenter", "B12", (e) => {
    map.getCanvas().style.cursor = "pointer";

    map.on("click", "B12", (e) => {
      let message = `
      <p>Paving Package: B12</p>
    `;

      let popup = new mapboxgl.Popup({
        closeButton: false,
        className: "popup-style",
      });

      popup.setLngLat(e.lngLat).setHTML(message).addTo(map);
    });
  });
  map.on("mouseleave", "B12", () => {
    map.getCanvas().style.cursor = "";
    let popup = document.getElementsByClassName("popup-style");

    if (popup.length) {
      popup[0].remove();
    }
  });
});
