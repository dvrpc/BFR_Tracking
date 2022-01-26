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

map.on("load", () => {
  //load sources
  for (const source in sources) map.addSource(source, sources[source]);
  //load layer styles
  for (const layer in layers) map.addLayer(layers[layer]);
});

//popups
map.on("mouseenter", "planned-segments", () => {
  map.getCanvas().style.cursor = "pointer";
});
map.on("mouseleave", "planned-segments", () => {
  map.getCanvas().style.cursor = "";
});

map.on("click", "planned-segments", (e) => {
  const coordinates = e.features[0].geometry.coordinates.slide();
  const description = e.features[0].properties.description;

  new mapboxgl.Popup().setLngLat(coordinates).setHTML("<p>test</p>").addTo(map);
});
