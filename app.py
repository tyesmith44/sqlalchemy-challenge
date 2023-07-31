# Import the dependencies.
from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import numpy as np
import pandas as pd
import datetime as dt

#################################################
# Database Setup
#################################################
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

#################################################
# Flask Setup
#################################################
# Create an app, being sure to pass __name__
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
#route("/")
@app.route("/")
def home():
    """Home with paths"""
    return (
        f"HOME<br/>" 
        f"these are the possible paths:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
        )
# f"Note: dates must be in YYYMMDD format with start and end seperated by "/"<br/>"

#route("/api/v1.0/precipitation")
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Precipitation for last 12 months JSON"""

    #Calculate the date one year from the last date in data set.
    year_ago = dt.datetime(2017, 8, 23) - dt.timedelta(days=365)

    #Perform a query to retrieve the data and precipitation scores
    precp_df = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()
    
    #close session
    session.close()

    #jsonify
    prcp = {date: prcp for date, prcp in precp_df}
    return jsonify(prcp)


#route("/api/v1.0/stations")       
@app.route("/api/v1.0/stations")
def stations():
    """List of stations"""
    stations_all_res = session.query(Station.name, Station.station).all()

    #close session
    session.close()

    # Convert list of tuples into normal list
    stations_all = list(np.ravel(stations_all_res))

    #jsonify
    return jsonify(Stations = stations_all)


#route("/api/v1.0/tobs")       
@app.route("/api/v1.0/tobs")
def temperature():
    """Temperatures for the last 12mo at the Waihee Station"""

    #Calculate the date one year from the last date in data set.
    year_ago = dt.datetime(2017, 8, 23) - dt.timedelta(days=365)

    # Query the last 12 months of temperature observation data for this station 
    most_active_station = session.query(Measurement.tobs).\
                        filter(Measurement.station == 'USC00519281').\
                        filter(Measurement.date >= year_ago).all()

    #close session
    session.close()

    # Convert list of tuples into normal list
    temps_active = list(np.ravel(most_active_station))

    #jsonify
    return jsonify(Temperatures = temps_active)


#route("/api/v1.0/<start>")       
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def date_start(start=None, end=None):
    """List of the minimum temp, average temp, and the maximum temp for a given start day."""

    sel = [func.min(Measurement.tobs), 
           func.avg(Measurement.tobs),
           func.max(Measurement.tobs)]
    
    #start only
    if not end: 
    
    
        #Query minimum temp, average temp, and the maximum temp for a given start day at most_active
        temp_stats_results = session.query(*sel).\
            filter(Measurement.station == 'USC00519281').\
            filter(Measurement.date >= start).all()
    
        #close session
        session.close()

        #Convert list of tuples into normal list
        temp_stats = list(np.ravel(temp_stats_results))

        #jsonify
        return jsonify(min_avg_max = temp_stats)
    

    if start and end:
        start = dt.datetime.strptime(start, '%Y%m%d')
        end = dt.datetime.strptime(end, '%Y%m%d')
        #Query minimum temp, average temp, and the maximum temp for a given start day at most_active
        temp_stats_results = session.query(*sel).\
                filter(Measurement.station == 'USC00519281').\
                filter(Measurement.date >= start).\
                filter(Measurement.date <= end).all()
    
        #close session
        session.close()
        
        #Convert list of tuples into normal list
        temp_stats = list(np.ravel(temp_stats_results))
       
        #jsonify
        return jsonify(min_avg_max = temp_stats)


if __name__ == "__main__":
    app.run(debug=True)