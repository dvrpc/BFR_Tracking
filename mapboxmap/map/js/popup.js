const make_popup = (e, message, map) => {
  let popup = new mapboxgl.Popup({
    closeButton: true,
    className: "popup-style",
  });

  popup.setLngLat(e.lngLat).setHTML(message).addTo(map);
};

// const remove_popup = () => {
//   let popup = document.getElementsByClassName("popup-style");

//   if (popup.length) {
//     popup[0].remove();
//   }
// };

export { make_popup };
