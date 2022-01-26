const layers = {
  plan: {
    id: "planned-segments",
    type: "line",
    source: "plan",
    layout: {
      visibility: "visible",
    },
    paint: {
      "line-width": 1.5,
      "line-color": [
        "match",
        ["get", "Year"],
        "2022",
        "#27AE60 ", //green
        "2023",
        "#F39C12", //orange
        "2024",
        "red", //red
        "2025",
        "#A569BD", //purple
        "2026",
        "#3498DB", //blue
        "gray",
      ],
    },
  },
  B12: {
    id: "B12",
    type: "line",
    source: "B12",
    layout: {
      visibility: "visible",
    },
    paint: {
      "line-width": 4,
      "line-color": "yellow",
      "line-opacity": 0.4,
    },
  },
  C12: {
    id: "C12",
    type: "line",
    source: "C12",
    paint: {
      "line-width": 4,
      "line-color": "yellow",
      "line-opacity": 0.4,
    },
  },
  D13: {
    id: "D13",
    type: "line",
    source: "D13",
    paint: {
      "line-width": 4,
      "line-color": "yellow",
      "line-opacity": 0.4,
    },
  },
  M11: {
    id: "M11",
    type: "line",
    source: "M11",
    paint: {
      "line-width": 4,
      "line-color": "yellow",
      "line-opacity": 0.4,
    },
  },
  P12: {
    id: "P12",
    type: "line",
    source: "P12",
    paint: {
      "line-width": 4,
      "line-color": "yellow",
      "line-opacity": 0.4,
    },
  },
};

export default layers;
