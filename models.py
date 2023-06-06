import urllib.request
import ssl
from flask import json
import pandas as pd


class GetResults:
    def __init__(
        self,
        address: str = None,
        latitude: float = None,
        longitude: float = None,
        elevation: float = None,
    ):
        self.address = address
        self.latitude = latitude
        self.longitude = longitude
        self.elevation = elevation

    def get_coordinates(self):
        request_url = (
            "https://nominatim.openstreetmap.org/search?q="
            + self.address.replace(" ", "+")
            + "&format=json&polygon_geojson=1&addressdetails=1"
        )
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(request_url, context=context) as response:
            response_json = response.read()
        encoding = response.info().get_content_charset("utf-8")
        data = json.loads(response_json.decode(encoding))
        if len(data) > 0:
            return {
                "longitude": float(data[0]["lon"]),
                "latitude": float(data[0]["lat"]),
            }
        return {"longitude": None, "latitude": None}

    def get_elevation(self):
        request_url = (
            "https://nationalmap.gov/epqs/pqs.php?x="
            + str(self.longitude)
            + "&y="
            + str(self.latitude)
            + "&units=Meters&output=json"
        )
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(request_url, context=context) as response:
            response_json = response.read()
        encoding = response.info().get_content_charset("utf-8")
        data = json.loads(response_json.decode(encoding))
        return float(
            data["USGS_Elevation_Point_Query_Service"]["Elevation_Query"]["Elevation"]
        )

    def get_flood(self):
        data = pd.read_pickle("data/ProphetForecast.pkl")
        flood_indices = data.index[data["yhat"] > self.elevation * 1000]
        if len(flood_indices) > 0:
            first_flood = min(flood_indices)
            flood_level = data["yhat"][first_flood] / 1000
            flood_date = data["ds"][first_flood]
            lower_bound = data["yhat_lower"][first_flood] / 1000
            
            upper_bound = data["yhat_upper"][first_flood] / 1000
            return {
                "first_flood": first_flood,
                "flood_level": flood_level,
                "flood_date": str(flood_date),
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
            }
        else:
            return {
                "first_flood": None,
                "flood_level": None,
                "flood_date": None,
                "lower_bound": None,
                "upper_bound": None,
            }
