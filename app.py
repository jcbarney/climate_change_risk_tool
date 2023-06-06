import numpy as np
from flask import Flask, request, render_template, json
from flask_bootstrap import Bootstrap
import pickle
from models import *
from datetime import datetime

app = Flask(__name__)
bootstrap = Bootstrap(app)

##DEV NOTES: EXAMPLES FOR TESTING
# below: S.C.Bootle Hwy, The Bahamas
# Not in danger: 107 S Indiana Ave, Bloomington, IN 47405
# danger: 88-22 Bal Bay Dr, Bal Harbour, FL 33154


@app.route("/")
def home():
    return render_template("index.html", title="Home Page")


@app.route("/get_data", methods=["POST"])
def get_data():
    address = str(request.form["address"])
    get_coordinates = GetResults(address=address)
    coordinates = get_coordinates.get_coordinates()
    if coordinates["longitude"] is None:
        return json.jsonify(
            {
                "latitude": 39.167438,
                "longitude": -86.519962,
                "years": 100,
                "results": "address not found. Please try again using the correct format and no special characters.",
            }
        )
    else:
        get_elevation = GetResults(
            latitude=coordinates["latitude"], longitude=coordinates["longitude"]
        )
        elevation = get_elevation.get_elevation()
        get_flood = GetResults(elevation=elevation)
        flood_results = get_flood.get_flood()
        if flood_results["first_flood"] is not None:
            flood_date = datetime.strptime(
                str(flood_results["flood_date"])[:10], "%Y-%m-%d"
            )
            delta = flood_date - datetime.today()
            years = int(round(delta.days / 360, 0))
            print(years, elevation, flood_results["flood_level"])
            if years >= 0:
                statement = f"the sea level may rise to {str(round(flood_results['flood_level'],2))} meters above sea level within {str(years)} years. The true sea level may be between {str(round(flood_results['lower_bound'],2))} and {str(round(flood_results['upper_bound'],2))} meters with 95% confidence given the current trajectory. *This assumes that there is direct access from the given address to the ocean"
                return json.jsonify(
                    {
                        "latitude": coordinates["latitude"],
                        "longitude": coordinates["longitude"],
                        "years": str(years),
                        "results": statement,
                    }
                )
            else:
                statement = f"you may already be in trouble. The elevation of the given location is below the current sea level. *This assumes that there is direct access from the given address to the ocean"
                return json.jsonify(
                    {
                        "latitude": coordinates["latitude"],
                        "longitude": coordinates["longitude"],
                        "years": str(0),
                        "results": statement,
                    }
                )
        else:
            print(elevation, flood_results["flood_level"])
            statement = f"this location should not be directly impacted by rising sea levels for the distant future. *locations above, but near, sea level can still have a risk of major flooding as a direct cause of rising sea levels"
            return json.jsonify(
                {
                    "latitude": coordinates["latitude"],
                    "longitude": coordinates["longitude"],
                    "years": "-",
                    "results": statement,
                }
            )


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", title="Calculator")


@app.route("/about")
def about():
    return render_template("about.html", title="About")


if __name__ == "__main__":
    app.run(debug=True)
