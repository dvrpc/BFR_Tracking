const add_pointer_when_hovering = (map, layername) => {
  map.on("mouseenter", layername, (e) => {
    map.getCanvas().style.cursor = "pointer";
  });

  map.on("mouseleave", layername, () => {
    map.getCanvas().style.cursor = "";
  });
};

export { add_pointer_when_hovering };
