const yellow_paint_style = {
  "line-width": 4,
  "line-color": "yellow",
  "line-opacity": 0.4,
};

const layers = {
  boundaries: {
    id: "boundaries",
    type: "line",
    source: "boundaries",
    paint: {
      "line-color": "#d4d5d6",
      "line-width": 1,
    },
    filter: ["all", ["==", "dvrpc_reg", "Yes"], ["==", "state", "PA"]],
  },
  plan: {
    id: "planned-segments",
    type: "line",
    source: "plan",
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
    paint: yellow_paint_style,
  },
  C12: {
    id: "C12",
    type: "line",
    source: "C12",
    paint: yellow_paint_style,
  },
  D13: {
    id: "D13",
    type: "line",
    source: "D13",
    paint: yellow_paint_style,
  },
  M11: {
    id: "M11",
    type: "line",
    source: "M11",
    paint: yellow_paint_style,
  },
  P12: {
    id: "P12",
    type: "line",
    source: "P12",
    paint: yellow_paint_style,
  },
};

export { layers };
