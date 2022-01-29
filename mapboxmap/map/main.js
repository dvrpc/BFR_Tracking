import { sources } from "./sources.js";
import { layers } from "./layers.js";
import { add_pointer_when_hovering } from "./hover.js";
import { make_popup } from "./popup.js";
import { make_popup_message } from "./click.js";
import { make_map } from "./map.js";

const map = make_map();

map.on("load", () => {
  //load sources
  for (const source in sources) map.addSource(source, sources[source]);
  //load layer styles
  for (const layer in layers) map.addLayer(layers[layer]);

  // set the pointer style when hovering specific layers
  ["planned-segments", "B12"].forEach((layer) => {
    add_pointer_when_hovering(map, layer);
  });

  // make a popup when the user clicks on one or more of the map layers
  map.on("click", (e) => {
    // get all features near the user's click
    let features = map.queryRenderedFeatures(e.point, {
      layers: ["planned-segments", "B12", "C12", "D13", "M11", "P12"],
    });

    // as long as there's at least one feature, make the message
    // and then add the popup to the map
    if (features.length > 0) {
      let message = make_popup_message(features);
      make_popup(e, message, map);
    }
  });
});
