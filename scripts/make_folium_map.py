"""
make_folium_map.py
------------------

This script makes a HTML map using folium
and the geojson data stored within ./data/geojson

Note: update the lambda function if you want each
distinct layer to have its own color!

TO DO
- create pop-up
"""

import folium
from pathlib import Path
import json
import geopandas as gpd
import env_vars as ev


# ensure geojson files use epsg=4326
def reproject(filelocation):
    for geojsonfilepath in filelocation.rglob("*.geojson"):
        gdf = gpd.read_file(geojsonfilepath)

        # if not already projected, project it and overwrite the original file
        if gdf.crs != 4326:
            gdf.to_crs(epsg=4326, inplace=True)

        # save the filename in a new column, to be used for coloring the map
        gdf["src"] = geojsonfilepath.stem
        gdf.to_file(geojsonfilepath, driver="GeoJSON")


# seg_gdf = gpd.read_file(fr"{ev.DATA_ROOT}/mapped_segments_geojson/mapped_segments.geojson")
# def style_function_years(feature):


def main():

    data_dir = Path("./data/geojson")
    mapped_seg = Path("./data/mapped_segments_geojson")
    philly_city_hall = [39.952179401878304, -75.16376402095634]
    output_path = "./maps/demo.html"

    reproject(data_dir)
    reproject(mapped_seg)

    # make the folium map
    m = folium.Map(
        location=philly_city_hall,
        tiles="cartodbpositron",
        zoom_start=9,
    )
    # add 5-year plan segments to the map
    for geojsonfilepath in mapped_seg.rglob("*.geojson"):
        file_name = geojsonfilepath.stem
        print("Adding", file_name)
        folium.GeoJson(
            json.load(open(geojsonfilepath)),
            name="5-year Plan",
            style_function=lambda x: {
                "color": "lightblue"
                if x["properties"]["CALENDAR_YEAR"] == 2022
                else "blue"
                if x["properties"]["CALENDAR_YEAR"] == 2023
                else "darkblue"
                if x["properties"]["CALENDAR_YEAR"] == 2024
                else "gray",
                "weight": "1",
                "popup": ["CALENDAR_YEAR"],
            },
            zoom_on_click=True,
        ).add_to(m)

    # add package geojson files to the map
    for geojsonfilepath in data_dir.rglob("*.geojson"):
        file_name = geojsonfilepath.stem
        print("Adding", file_name)
        folium.GeoJson(
            json.load(open(geojsonfilepath)),
            name=file_name,
            style_function=lambda x: {
                "color": "green"
                if x["properties"]["ReportStatus"] == "Not Evaluated"
                else "orange"
                if x["properties"]["ReportStatus"] == "Repeated"
                else "purple"
                if x["properties"]["ReportStatus"] == "Not Repeated"
                else "black"
            },
            zoom_on_click=True,
        ).add_to(m)

    # add layer toggle box and save to HTML file
    folium.LayerControl().add_to(m)

    print("Writing HTML file to", output_path)
    m.save(output_path)


if __name__ == "__main__":
    main()
