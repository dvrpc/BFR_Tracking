"""
make_folium_map.py
------------------

This script makes a HTML map using folium
and the geojson data stored within ./data/geojson

Note: update the lambda function if you want each
distinct layer to have its own color!
"""

import folium
from pathlib import Path
import json
import geopandas as gpd


def main():

    data_dir = Path("./data/geojson")
    philly_city_hall = [39.952179401878304, -75.16376402095634]
    output_path = "./maps/demo.html"

    # ensure geojson files use epsg=4326
    for geojsonfilepath in data_dir.rglob("*.geojson"):
        gdf = gpd.read_file(geojsonfilepath)

        # if not already projected, project it and overwrite the original file
        if gdf.crs != 4326:
            gdf.to_crs(epsg=4326, inplace=True)

        # save the filename in a new column, to be used for coloring the map
        gdf["src"] = geojsonfilepath.stem
        gdf.to_file(geojsonfilepath, driver="GeoJSON")

    # make the folium map
    m = folium.Map(
        location=philly_city_hall,
        tiles="cartodbpositron",
        zoom_start=9,
    )

    # add each geojson file to the map
    for geojsonfilepath in data_dir.rglob("*.geojson"):
        file_name = geojsonfilepath.stem
        print("Adding", file_name)
        folium.GeoJson(
            json.load(open(geojsonfilepath)),
            name=file_name,
            style_function=lambda x: {
                "color": "green"
                if x["properties"]["src"] == "D13_mappedreport"
                else "orange"
                if x["properties"]["src"] == "C12_mappedreport"
                else "red"
            },
            zoom_on_click=True,
        ).add_to(m)

    # add layer toggle box and save to HTML file
    folium.LayerControl().add_to(m)

    print("Writing HTML file to", output_path)
    m.save(output_path)


if __name__ == "__main__":
    main()
