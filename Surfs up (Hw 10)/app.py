# Import the dependencies.

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


# DATABASE SETUP

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB

session = Session(engine)



# FLASK SETUP
app = Flask(__name__)

# Functions
def start():
    found_date = session.query(func.min(Measurement.date))

    return found_date[0][0]


def end():
    found_date = session.query(func.max(Measurement.date))

    return found_date[0][0]

# Function to find what day is a year before the last date in the data
def last_year():
    # Find the most recent date
    last_date_found = end()
    # Calculate the last 12 months from most recent date
    last_twelve_months = pd.to_datetime(last_date_found).date() - dt.timedelta(days=365)

    return last_twelve_months

# Function to find the most active station and retunr it
def most_active_station():

    # Build the list of all stations based on how active they are
    most_active_stations = session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    return most_active_stations[0][0]




# LIST ALL AVAILABLE ROUTES

@app.route("/")
def welcome():
    """List all available api routes."""

    # Find the first date and last date found in the data to be used as an example
    last_date_found= end()
    first_date_found = start()

    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/{first_date_found}<br/>"
        f"/api/v1.0/{first_date_found}/{last_date_found}"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Returns a list of precipitation for every date in the last 12 months from most recent date, sort it by date"""
    
    # Get all the dates and prcp's for every date in the last 12 months from most recent date, sort it by date
    prcp_results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year()).order_by(Measurement.date).all()


    # Build a list of dictionary's containing all the dates and the prcp for those dates
    prcp_list = []
    for date, precipitation in prcp_results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = precipitation
        prcp_list.append(prcp_dict)

    # Return the list JSONified
    return jsonify(prcp_list)


@app.route("/api/v1.0/stations")
def stations():

    """Return a JSON list of stations from the dataset."""
    results = session.query(Station.station).all()
    station_list = [station[0] for station in results]
    return jsonify(station_list)

    
@app.route("/api/v1.0/tobs")
def tobs():
    """Returns a list of date and tobs for the most active station over that last 12 months"""
    

    # Get the date and tobs for the most active station over that last 12 months
    tobs_results = session.query(Measurement.date, Measurement.tobs).where(Measurement.station == most_active_station()).filter(Measurement.date >= last_year()).order_by(Measurement.date).all()

    

    # Build a list of dictionary's containing dates and tobs from the most active station over that last 12 months
    tobs_list = []
    for date, temperature in tobs_results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = temperature
        tobs_list.append(tobs_dict)

    # Return the list JSONified
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start_date(start):
    """Returns a list of min temp, avg temp, and max temp from a specified start date to the most current date"""
    

    # Get the min temp, avg temp, and max temp from a specified start date to the most current date
    tobs_results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).where(Measurement.date >= start).all()

    

    # Build a list of dictionary's containing min temp, avg temp, and max temp for the specified date range
    tobs_list = []
    for tmin, tavg, tmax in tobs_results:
        tobs_dict = {}
        tobs_dict["TMIN"] = tmin
        tobs_dict["TAVG"] = tavg
        tobs_dict["TMAX"] = tmax
        tobs_list.append(tobs_dict)

    # Return the list JSONified
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    """Returns a list of min temp, avg temp, and max temp from a specified start date to a specified end date"""
   
    # Get the min temp, avg temp, and max temp from a specified start date to a specified end date
    tobs_results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).where((Measurement.date >= start) & (Measurement.date <= end)).all()

   

    # Build a list of dictionary's containing min temp, avg temp, and max temp for the specified date range
    tobs_list = []
    for tmin, tavg, tmax in tobs_results:
        tobs_dict = {}
        tobs_dict["TMIN"] = tmin
        tobs_dict["TAVG"] = tavg
        tobs_dict["TMAX"] = tmax
        tobs_list.append(tobs_dict)

    # Return the list JSONified
    return jsonify(tobs_list)

if __name__ == '__main__':
    app.run(debug=True)
