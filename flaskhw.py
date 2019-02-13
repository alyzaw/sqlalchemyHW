# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import pandas as pd
import numpy as np

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


# This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
max_date = max_date[0]

from flask import Flask, jsonify

# 2 we can create an app

app = Flask(__name__)


@app.route("/")
def home():
    
	print("Server received request for 'Home' page...")
    
	return (f"Welcome to my your surfer weather guide!<br/>"
		f"Check out these available API requests:<br/>"
		f"/api/v1.0/precipitation<br/>"
		f"/api/v1.0/stations<br/>"
		f"/api/v1.0/tobs<br/>"
		f"/api/v1.0/'start'<br/>"
		f"/api/v1.0/'start/end'<br/>")

# 4. Define what to do when a user hits the /precip route

@app.route("/api/v1.0/precipitation")

def precipitation():
    session = Session(engine)
    
    results = session.query(Measurement.date,Measurement.prcp).all()

    all_measurements = []
    for measurements in results:
        measurements_dict = {}
        measurements_dict["Date"] = measurements.date
        measurements_dict["Precip"] = measurements.prcp
        all_measurements.append(measurements_dict)

    return jsonify(all_measurements)

@app.route("/api/v1.0/stations")

def stations():
    session = Session(engine)
    
    results = session.query(Station).all()

    all_stations = []
    for station in results:
        station_dict = {}
        station_dict["Station_ID"] = station.station
        station_dict["Name"] = station.name
        station_dict["Latitude"] = station.latitude
        station_dict["Longitude"] = station.longitude
        station_dict["Elevations"] = station.elevation
        all_stations.append(station_dict)

    return jsonify(all_stations)  


@app.route("/api/v1.0/tobs")

def tobs():
    session = Session(engine)
    
    results = session.query(Measurement.date,Measurement.tobs).all()

    all_tobs = []
    for obs in results:
        obs_dict = {}
        obs_dict["Date"] = obs.date
        obs_dict["Tobs"] = obs.tobs
        all_tobs.append(obs_dict)

    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>")

def start(start):
    session = Session(engine)
    
    results = calc_temps(start, max_date)
    
    start_dict = {"Min" : results[0][0],
              "Max" : results[0][1],
              "Avg" : results[0][2]}

    return jsonify(start_dict)
#	if start in Measurements["Date"]:
     
 #    		return jsonify(calc_temps(start, max_date))
   
	#return jsonify({"error": f"Date not found."}), 404

@app.route("/api/v1.0/<start>/<end>")

def start_end(start,end):
    
	if start in Measurements["Date"]:
     
     		return jsonify(calc_temps(start, end))
   
	return jsonify({"error": f"Date not found."}), 404


from flask import request


def shutdown_server():
    
	func = request.environ.get('werkzeug.server.shutdown')
    
	if func is None:
        
		raise RuntimeError('Not running with the Werkzeug Server')
    
	func()
    

@app.route('/shutdown')

def shutdown():
    
	shutdown_server()
    
	return 'Server shutting down...'


if __name__ == "__main__":
    
	app.run(debug=True)

