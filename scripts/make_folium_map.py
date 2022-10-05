"""
make_folium_map.py
------------------

This script makes a HTML map using folium
and the geojson data stored within ./data/geojson

"""

from urllib import parse
import folium
from pathlib import Path
import json
from folium.map import Popup
import geopandas as gpd
import env_vars as ev
from map_packages import lookup_county_code


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


county_lookup = {
    "B": "Bucks",
    "C": "Chester",
    "D": "Delaware",
    "M": "Montgomery",
    "P": "Philadelpiha",
}


def parse_name(package_name):
    string = package_name
    return string[0:3]


def lookup_county_code(letter):
    return county_lookup[letter[0:1]]

def strip(string):
    return string.replace(" ","")

def main():

    data_dir = Path("./data/geojson")
    mapped_seg = Path("./data/mapped_segments_geojson")
    philly_city_hall = [39.952179401878304, -75.16376402095634]
    output_path = "./maps/2023_packages.html"

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
                "color": "gray",
                # if x["properties"]["CALENDAR_YEAR"] == 2022
                # else "blue"
                # if x["properties"]["CALENDAR_YEAR"] == 2023
                # else "darkblue"
                # if x["properties"]["CALENDAR_YEAR"] == 2024
                # else "gray",
                "weight": "1",
            },
            popup=folium.GeoJsonPopup(
                fields=["sr", "CALENDAR_YEAR"],
                aliases=["State Route: ", "Planned Year: "],
            ),
            zoom_on_click=True,
        ).add_to(m)

    # add package geojson files to the map
    for geojsonfilepath in data_dir.rglob("*.geojson"):
        file_name = geojsonfilepath.stem
        code = parse_name(strip(file_name))
        County = lookup_county_code(code)
        layername = (fr"{County}: {code}",)
        print("Adding", file_name)
        folium.GeoJson(
            json.load(open(geojsonfilepath)),
            name=layername,
            style_function=lambda x: {
                "color": "purple"
                if x["properties"]["status"] == "Initial Screening"
                else "orange"
                if x["properties"]["status"] == "For PennDOT to Screen for Feasibility"
                else "green"
                if x["properties"]["status"] == "Letter Received"
                else "red"
                if x["properties"]["status"] == "Begin Municipal Outreach"
                else "blue"
                if x["properties"]["status"] == "Complete"
                else "lightblue"
                if x["properties"]["status"] == "Pending Review"
                else "lightred"
                if x["properties"]["status"] == "Not Reviewed"
                else "darkred"
                if x["properties"]["status"] == "Waiting for municipal letter"
                else "lightgreen"
                if x["properties"]["status"] == "For DVRPC to Screen for Feasibility"
                else "white"
                if x["properties"]["status"] == "Beyond Scope of Resurfacing"
                else "yellow"
                if x["properties"]["status"] == "Reviewed, not pursued"
                else "black",
                "weight": "4",
            },
            popup=folium.GeoJsonPopup(
                fields=["sr", "name", "status"],
                aliases=["State Route: ", "Local Road Name: ", "Status: "],
            ),
            zoom_on_click=False,
        ).add_to(m)

    # add layer toggle box and save to HTML file
    folium.LayerControl().add_to(m)

    print("Writing HTML file to", output_path)
    m.save(output_path)


if __name__ == "__main__":
    main()
