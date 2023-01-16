# Climate App

from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt

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
Station = Base.classes.station

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
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- List of prior year rain totals in inches from all weather stations<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"- List of weather station numbers and names<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"- List of prior year temperatures from most active weather station (USC00519281)<br/>"
        f"<br/>"
        f"/api/v1.0/start_date/<start_date><br/>"
        f"- When given the start date (YYYY-MM-DD), calculates the MIN/AVG/MAX temperature for all dates greater than and equal to the start date.<br/>"
        f"<br/>"
        f"/api/v1.0/start_end/<start_date>/<end_date><br/>"
        f"- When given the start and the end date (YYYY-MM-DD), calculate the MIN/AVG/MAX temperature for dates between the start and end date.<br/>"
    )

#########################################################################################

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
    
    session.close()

    year_prcp_all = []
    for date, prcp in year_prcp:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        year_prcp_all.append(prcp_dict)

    return jsonify(year_prcp_all)

#########################################################################################

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Perform a query to retrieve the station name and ID
    stations_query = session.query(Station.name, Station.station)
 
    session.close()

    stations_list = []
    for name, station in stations_query:
        station_dict = {}
        station_dict["name"] = name
        station_dict["station"] = station
        stations_list.append(station_dict)

    return jsonify(stations_list)

#########################################################################################

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Create object for last year
    last_year = dt.date(2017,8,23) - dt.timedelta(days= 365)

    # Query for tobs, dates from most active station
    active_year_temp = session.query(measurements.tobs, measurements.date).\
      filter(measurements.date >= last_year, measurements.station == 'USC00519281').\
      order_by(measurements.tobs).all()

    session.close()

    # Create a dictionary from the row data and append to a list
    tob_all = []
    for date, tobs in active_year_temp:
        tob_dict = {}
        tob_dict["date"] = date
        tob_dict["tobs"] = tobs
        tob_all.append(tob_dict)

    return jsonify(tob_all)

#########################################################################################
#Return a JSON list of the minimum temperature, the average temperature, and the maximum 
# temperature for a specified start or start-end range.

#For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or 
# equal to the start date.

#For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from 
# the start date to the end date, inclusive.
 
@app.route("/api/v1.0/start_date/<start_date>")
def Start_date(start_date):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Query for min, max, and avg tobs greater than or equal to given start date
    results = session.query(func.min(measurements.tobs), func.avg(measurements.tobs), func.max(measurements.tobs)).filter(measurements.date >= start_date).all()
    
    session.close()

    # Create a dictionary from the row data and append to a list
    tobsall = []
    for min, avg, max in results:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobsall.append(tobs_dict)

    return jsonify(tobsall)

#########################################################################################

@app.route("/api/v1.0/start_end/<start_date>/<end_date>")
def start_end(start_date, end_date):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Query for min, max, and avg tobs between given start and end dates
    results = session.query(func.min(measurements.tobs), func.avg(measurements.tobs), func.max(measurements.tobs)).filter(measurements.date >= start_date).filter(measurements.date <= end_date).all()
    
    session.close()

    # Create a dictionary from the row data and append to a list
    startend = []
    for min, avg, max in results:
        startend_dict = {}
        startend_dict["Min"] = min
        startend_dict["Average"] = avg
        startend_dict["Max"] = max
        startend.append(startend_dict)

    return jsonify(startend)

#########################################################################################


if __name__ == '__main__':
    app.run(debug=True)