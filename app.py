import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route('/')
def home():
	return(
		f'<b/>Welcome to my Climate App.</b></br></br>'
		f'The available routes are:</br></br>'
		f'/api/v1.0/precipitation</br>'
		f'/api/v1.0/stations</br>'
		f'/api/v1.0/tobs</br>'
		f'/api/v1.0/"<start>"</br>'
		"'/api/v1.0/<start>/<end>' for min/avg/max temperatures between two dates")

@app.route('/api/v1.0/precipitation')
def precipitation():
	session = Session(engine)
	results = session.query(Measurement.date, Measurement.prcp).\
    	filter(Measurement.date >'2016-08-23').\
    	filter(Measurement.date <='2017-08-23').all()
	session.close()
	weather_results = []
	for date, prcp in results:
		weather = {}
		weather["date"] = date
		weather["precipitation"] = prcp
		weather_results.append(weather)
	return jsonify(weather_results)

@app.route('/api/v1.0/stations')
def stations():
	session = Session(engine)
	results = session.query(Measurement.station).group_by(Measurement.station).all()
	session.close()
	return jsonify(list(np.ravel(results)))

@app.route('/api/v1.0/tobs')
def temperatures():
	session = Session(engine)
	results= session.query(Measurement.date, Measurement.tobs).\
    	filter(Measurement.date >'2016-08-23').\
    	filter(Measurement.date <='2017-08-23').\
    	filter(Measurement.station == "USC00519281").all()
	session.close()
	weather_results = []
	for date, tobs in results:
		weather = {}
		weather["date"] = date
		weather["tobs"] = tobs
		weather_results.append(weather)
	return jsonify(weather_results)

@app.route('/api/v1.0/<start>')
def start_only(start):
	print("Provide a datestring in the format %Y-%m-%d")
	session = Session(engine)
	oldest = session.query(Measurement.date).order_by(Measurement.date.asc()).first()
	if start >= oldest[0]:
		results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
	        filter(Measurement.date >= start).all()
	else: return f'Date entered is prior to beginning of database or in incorrect format.</br></br>\
					Please enter a date after {oldest[0]} in %Y-%m-%d format.'
	session.close()
	weather_results = []
	for tmin, tavg, tmax in results:
    	 weather = {}
    	 weather["start_date"] = start
    	 weather['TMIN'] = tmin
    	 weather['TAVG'] = tavg
    	 weather['TMAX'] = tmax
    	 weather_results.append(weather)
	return jsonify(weather_results)

@app.route('/api/v1.0/<start>/<end>')
def start_end(start, end):
	print("Provide a datestring in the format %Y-%m-%d")
	session = Session(engine)
	oldest = session.query(Measurement.date).order_by(Measurement.date.asc()).first()
	newest = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
	if start >= oldest[0] or end <= newest[0]:
		results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
	        filter(Measurement.date >= start).\
	        filter(Measurement.date <= end).all()
	else: return(f'Date entered is outside date range of database or in incorrect format.</br></br>'
				f'Please enter a start date after {oldest[0]} and an end date before {newest[0]} in %Y-%m-%d format.')
	session.close()
	weather_results = []
	for tmin, tavg, tmax in results:
    	 weather = {}
    	 weather["start_date"] = start
    	 weather["end_date"] = end
    	 weather['TMIN'] = tmin
    	 weather['TAVG'] = tavg
    	 weather['TMAX'] = tmax
    	 weather_results.append(weather)
	return jsonify(weather_results)


if __name__ == '__main__':
    app.run(debug=True)