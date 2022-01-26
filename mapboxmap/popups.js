const popup_on_click = (map) => {
  map.on("click", "planned-segments", function (e) {
    map.flyTo({
      center: e.lngLat,
      zoom: 13,
      essential: true, // this animation is considered essential with respect to prefers-reduced-motion
    });
    new mapboxgl.Popup()
      .setLngLat(coordinates)
      .setHTML("<p>test</p>")
      .addTo(map);
  });
};

export { popup_on_click };
