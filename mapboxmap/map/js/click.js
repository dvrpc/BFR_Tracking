const make_popup_message = (featurelist) => {
  // Review every feature that was clicked on, and add a section
  // to the popup message for each one, split by a horizontal rule tag

  let messages = [];

  // Use different popup templates depending on the source layer,
  // in order to account for slightly different columns and names
  featurelist.forEach((feature) => {
    // Handle colorful layer showing all future years
    if (feature.layer.source == "plan") {
      let msg = `
        <h4>${feature.properties["Road Name"]} / SR ${feature.properties.sr}</h4>
        <p>Planned Year: ${feature.properties.Year}</p>
        `;
      if (messages.indexOf(msg) == -1) {
        messages.push(msg);
      }
    }
    // Handle yellow layers for county-specific 2022 schedule
    // TODO: duplicates may show up if one layer uses "AVE" and the other uses "AV" (etc...)
    else {
      let msg = `
        <h4>${feature.properties.name.toUpperCase()} / SR ${
        feature.properties.sr
      }</h4>
        <p>Planned Year: 2022</p>
        `;
      if (messages.indexOf(msg) == -1) {
        messages.push(msg);
      }
    }
  });

  return messages.join("<hr>");
};

export { make_popup_message };
