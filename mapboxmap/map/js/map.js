const make_map = () => {
  mapboxgl.accessToken =
    "pk.eyJ1IjoiZHZycGNvbWFkIiwiYSI6ImNrczZlNDBkZzFnOG0ydm50bXR0dTJ4cGYifQ.VaJDo9EtH2JyzKm3cC0ypA";

  let map = new mapboxgl.Map({
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

  return map;
};

export { make_map };
