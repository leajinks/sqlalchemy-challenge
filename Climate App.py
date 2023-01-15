# Climate App

from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt
import numpy as np

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite", echo = False)

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurements = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) 
# to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

   # Calculate the date one year from the last date in data set.
    last_year = dt.date(2017,8,23) - dt.timedelta(days= 365)
    print(last_year)

# Perform a query to retrieve the data and precipitation scores
    year_prcp = session.query(measurements.date, measurements.prcp).\
    filter(measurements.date >= last_year, measurements.prcp != None).\
    order_by(measurements.date).all()
    
    year_prcp_all = []
    for date, prcp in year_prcp:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        year_prcp_all.append(prcp_dict)

    return jsonify(dict(year_prcp))

#Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query stations
    stations_query = session.query(measurements.station).distinct()

    session.close()

    # Create a dictionary from the row data and append to a list
    stations_all = []
    for station in stations:
        station_dict = {}
        station_dict["station"] = station
        stations_all.append(station_dict)

    return jsonify(dict(stations_query))


#Query the dates and temperature observations of the most-active station for the previous year of data.
#Return a JSON list of temperature observations for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query: active_year_temp from cell 18
    most_active = session.query(measurements.station,func.count(measurements.station)).\
    group_by(measurements.station).\
    order_by(func.count(measurements.station).desc()).all()

    last_year = dt.date(2017,8,23) - dt.timedelta(days= 365)

    active_year_temp = session.query(measurements.tobs).\
      filter(measurements.date >= last_year, measurements.station == 'USC00519281').\
      order_by(measurements.tobs).all()

    session.close()

    # Create a dictionary from the row data and append to a list
    tob_all = []
    for date, tobs in most_active:
        tob_dict = {}
        tob_dict["date"] = date
        tob_dict["tobs"] = tobs
        tob_all.append(tob_dict)

    return jsonify(dict(active_year_temp))

#Return a JSON list of the minimum temperature, the average temperature, and the maximum 
# temperature for a specified start or start-end range.

#For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or 
# equal to the start date.

#For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from 
# the start date to the end date, inclusive.
#@app.route("/api/v1.0/<start>")

@app.route("/api/v1.0/<start>")
    
def start_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    return session.query(func.min(measurements.tobs), func.avg(measurements.tobs), func.max(measurements.tobs)).\
        filter(measurements.date >= start_date).all()



if __name__ == '__main__':
    app.run()