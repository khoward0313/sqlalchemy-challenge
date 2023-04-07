# Import the dependencies.
import os
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import pandas as pd
from datetime import datetime



#################################################
# Database Setup
#################################################
os.chdir(os.path.dirname(os.path.realpath(__file__)))
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
connection = engine.connect()

Base = automap_base()

Base.prepare(autoload_with=engine)

stations = Base.classes.station
measurements = Base.classes.measurement
start = '2016-11-03'
end = '2016-05-10'

session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
app.config['DEBUG'] = True


#################################################
# Flask Routes
#################################################

# Route 1
@app.route("/")
def home():

    routes = (
        "api/v1.0/precipitation<br>"
        "/api/v1.0/stations<br>"
        "/api/v1.0/tobs<br>"
        "/api/v1.0/&lt;start&gt;<br>"
        "/api/v1.0/&lt;start&gt;/&lt;end&gt;<br>"
        )
    return routes

# Route 2
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    session = Session(engine)

    max_date = session.query(func.max(measurements.date)).scalar()

    past_12 = pd.to_datetime(max_date) - pd.DateOffset(months=12)
    past_12_str = past_12.strftime('%Y-%m-%d')

    results = session.query(measurements.date, measurements.prcp)\
                      .filter(measurements.date >= past_12_str)\
                      .filter(measurements.date <= max_date)\
                      .all()

    precip_df = pd.DataFrame(results, columns=['date', 'prcp'])
    precip_df.set_index('date', inplace=True)

    precip_df = precip_df.sort_index()

    precip_dict = precip_df['prcp'].to_dict()

    return jsonify(precip_dict)

# Route 3
@app.route("/api/v1.0/tobs")
def stations():
    stations = Base.classes.station
    session = Session(engine)
    
    results = session.query(stations.station, stations.name).all()

    station_list = []
    for result in results:
        station_dict = {}
        station_dict["station"] = result[0]
        station_dict["name"] = result[1]
        station_list.append(station_dict)

    return jsonify(station_list)

session.query(func.count(measurements.date)) \
       .filter(measurements.date == start) \
       .all()

# Route 4
@app.route("/api/v1.0/<start>")
def temperature_start(start):
    measurements = Base.classes.measurement
    session = Session(engine)

    results = session.query(func.min(measurements.tobs), func.avg(measurements.tobs), func.max(measurements.tobs)) \
              .filter(measurements.date >= start) \
              .all()

    temp_dict = {"TMIN": results[0][0], "TAVG": results[0][1], "TMAX": results[0][2]}

    return jsonify(temp_dict)


# Route 5
@app.route("/api/v1.0/<start>/<end>")
def temp_range(start, end):
    
    session = Session(engine)

    results = session.query(func.min(measurements.tobs), func.avg(measurements.tobs), func.max(measurements.tobs))\
                      .filter(measurements.date >= start)\
                      .filter(measurements.date <= end)\
                      .all()

    temp_dict2 = {"TMIN": results[0][0], "TAVG": results[0][1], "TMAX": results[0][2]}

    return jsonify(temp_dict2)


#################################################
# Autorun
#################################################
if __name__ == "__main__":
    app.run()
