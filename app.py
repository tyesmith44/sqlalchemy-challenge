# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func



#################################################
# Database Setup
#################################################
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
# reflect the tables
Base.prepare(autoload_with=engine)

# View all of the classes that automap found
#Base.classes.keys()
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


# Create our session (link) from Python to the DB
# Lazy loading
session = Session(engine)

#################################################
# Flask Setup
#################################################

# Create an app, being sure to pass __name__
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
# Home Route
@app.route("/")
def home():
    """Home route that list all my route paths"""
    return (
        f"Welcome to my HI Weather API<br/>"
        f"Available Routes: <br>"
        f"api/v1.0/precipitation<br>"
        f"api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/start<br>"
        f"/api/v1.0/start/end<br>"
        f"note: start and end must be dates in YYYYMMDD format with start and end seperated by '/'"
    )

# Precipitation Route
@app.route("/api/v1.0/precipitation")
def prcp_output():
    """Return precipitation for the last 12 months in json format"""

    # Calculate the date one year from the last date in data set.
    year_ago = dt.datetime(2017,8,23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    prcp_query = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()
    
    # Close Session
    session.close()

    precip = {date: prcp for date, prcp in prcp_query}

    """
    precip = {}

    for date, prcp in prcp_query:
        precip[date] = prcp

    """

    # return jsonify(precip)
    return precip

# Station Route
@app.route("/api/v1.0/stations")
def station_output():
    """Returns list of stations"""
    all_stations_results = session.query(Station.station).all()

     # Close Session
    session.close()

    #Convert list of tuples into normal list
    all_stations = list(np.ravel(all_stations_results))

    #return jsonify all_stations
    return jsonify(all_stations)

#Temperature Route
@app.route("/api/v1.0/tobs")
def temp_output():
    """Return the temperatures for the last year for most active station: 'USC00519281'"""
    
    # Calculate the date one year from the last date in data set.
    year_ago = dt.datetime(2017,8,23) - dt.timedelta(days=365)

    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram
    most_active_station_query = session.query(Measurement.tobs).\
                            filter(Measurement.station == 'USC00519281').\
                            filter(Measurement.date >= year_ago).all()
    
     # Close Session
    session.close()

    # unravel results
    temperatures = list(np.ravel(most_active_station_query))

    # return array of temperatures for the last year for station USC00519281
    return jsonify(temperatures = temperatures)

# start and start and end route for temperatures for USC00519281
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start=None, end=None):
    """Return a JSON list of the minimum temperature, 
    the average temperature, and the maximum temperature 
    for a specified start and or a start and end."""    

    # sel technique
    sel = [func.min(Measurement.tobs),
       func.avg(Measurement.tobs),
       func.max(Measurement.tobs)]
    
    # two possible routes
    # start is provided (without an end)
    if not end: 
    
        # transform start into date using dt.datetime
        start = dt.datetime.strptime(start, "%Y%m%d")

        temp_stats_results = session.query(*sel).\
                filter(Measurement.station == 'USC00519281').\
                filter(Measurement.date >= start).all()

        # Close Session
        session.close()
    
        # unravel using numpy and convert to list (to jsonify)
        temp_stats = list(np.ravel(temp_stats_results))

        # return jsonify version of temp_stats
        return jsonify(min_avg_max = temp_stats)
    
    # start and end are provided
    # transform start into date using dt.datetime
    start = dt.datetime.strptime(start, "%Y%m%d")
    end = dt.datetime.strptime(end, "%Y%m%d")

    temp_stats_results = session.query(*sel).\
            filter(Measurement.station == 'USC00519281').\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()

    # Close Session
    session.close()
    
    # unravel using numpy and convert to list (to jsonify)
    temp_stats = list(np.ravel(temp_stats_results))

    # return jsonify version of temp_stats
    return jsonify(min_avg_max = temp_stats)


if __name__ == "__main__":
    app.run(debug=True)