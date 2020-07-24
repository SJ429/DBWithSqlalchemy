import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
from flask import Flask

app = Flask(__name__)

@app.route("/")
def Homepage():
    """List all available api routes."""

    return (
    f"Available Routes:<br/>"
    f"----------------------------------------------------------------------------------------<br/>"
    f"Precipitation by date<br/>"
    f"/api/v1.0/precipitation<br/>"
    f"-----------------------------------------------------------------------------------------<br/>"
    f"List of Stations <br/>"
    f"/api/v1.0/stations<br/>"
    f"------------------------------------------------------------------------------------------<br/>"
    f"Dates and temperature observations of most active station for the last year <br/>"
    f"/api/v1.0/tobs<br/>"
    f"------------------------------------------------------------------------------------------<br/>"
    f"List of the minimum, average and max temperature for a given start<br/>"
    f"/api/v1.0/startdate<br/>" 
    f"------------------------------------------------------------------------------------------<br/>"
    f"List of the minimum, average and max temperature for a given start-end range<br/>"
    f"/api/v1.0/enddate"
    ) 

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query for the dates and precipitation values
    prcp_results = session.query(Measurement.date, Measurement.prcp).\
         group_by (Measurement.prcp).order_by(Measurement.date).all()
    
    session.close()

     # Convert to list of dictionaries to jsonify
    prcp_date_list = []

    for date, prcp in prcp_results:
        new_dict = {}
        new_dict[date] = prcp
        prcp_date_list.append(new_dict)

    return jsonify (prcp_date_list)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    station_results = session.query(Station.name, Station.id).all()
    
    session.close()    

    # Convert to list of dictionaries to jsonify
    station_list = []

    for name, station in station_results:
        new_dict = {}
        new_dict[name] = station
        station_list.append(new_dict)

    return jsonify (station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Query the dates and temperature observations of the most active station "USC00519281" for the last year of data
    #Last year data
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    date_yearago = (dt.datetime.strptime(last_date[0],'%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d')

    #Data
    tobs_results = session.query(Measurement.date,
       Measurement.tobs).\
        filter(Measurement.date >= date_yearago).\
        filter(Measurement.station == 'USC00519281').\
        group_by(Measurement.date).\
        order_by(Measurement.date.asc()).all()
    
    session.close()
   
    # Convert to list of dictionaries to jsonify
    tobs_list = []
    
    for date, tobs in tobs_results:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

@app.route("/api/v1.0/startdate")
def start():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query   
    start_date = '2016-06-28'
    
    tobs_start_results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), 
       func.max(Measurement.tobs)).\
      filter(Measurement.date >= start_date).all()
    
    session.close()
    
    # Convert to list of dictionaries to jsonify
    tobs_s_list = []

    for date,min,avg,max in tobs_start_results:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobs_s_list.append(tobs_dict)

    return jsonify(tobs_s_list)

@app.route("/api/v1.0/enddate")
def enddate():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #query
    start_date = '2016-06-28'
    end_date = '2016-07-05'
    tobs_end_results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), 
        func.max(Measurement.tobs)).\
       filter(Measurement.date >= start_date).\
           filter(Measurement.date <= end_date).all()    
    session.close()

    # Convert to list of dictionaries to jsonify
    tobs_e_list = []
    
    #for min,avg,max in tobs_end_results:
    for date,min,avg,max in tobs_end_results:    
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobs_e_list.append(tobs_dict)
    
    return jsonify(tobs_e_list)

if __name__ == "__main__":
    app.run(debug=True)    