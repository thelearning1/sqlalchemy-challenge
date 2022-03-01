# Import Dependencies
from re import M
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, create_engine
from flask import Flask, jsonify

#create all the sql stuff to access it.
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine,reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


#initialize the app
app = Flask(__name__)

####################################################################################
#create all static Routes
@app.route('/')
def index():
    '''List all routes in api'''
    return (
        f"Hawaii climate application, version 1.0 is now active.<br/>" 
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )
####################################################################################
@app.route('/api/v1.0/precipitation')
def precipitation():
    
    session = Session(engine)

    #calculate the latest date and the year prior
    latest_date = session.query(Measurement.date).order_by(desc('date')).first()
    latest_date = latest_date[0]
    x = latest_date.split('-',1) 
    year = int(x[0])
    last_year = str(year-1)
    x[0] = last_year
    year_ago = '-'.join(x)
    

    # Perform a query to retrieve the date and precipitation scores
    results = session.query(Measurement.date,Measurement.prcp).\
        filter(func.strftime('%Y,%m,%d',Measurement.date) >= \
            func.strftime('%Y,%m,%d',year_ago)).\
                                order_by(Measurement.date).all()

    session.close

    #Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
    #Return the JSON representation of your dictionary.
    #set an empty list to fill with dictionaries
    all_results = []
    for date, precipitation in results:
        precip_dict = {}
        precip_dict['date'] = date
        precip_dict['prcp'] = precipitation
        all_results.append(precip_dict)

    return (
        jsonify(precip_dict)
    )

####################################################################################
@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)

    results = session.query(Station.station,Station.name).all()

    session.close

    stations = []

    for station, name in results:
        station_dict = {}
        station_dict['station'] = station
        station_dict['name'] = name
        stations.append(station_dict)

    #Return a JSON list of stations from the dataset
    return (
        jsonify(stations)
    )

####################################################################################
@app.route('/api/v1.0/tobs')
def stations():

    session = Session(engine)
    
    #calculate the latest date and the year prior
    latest_date = session.query(Measurement.date).order_by(desc('date')).first()
    latest_date = latest_date[0]
    x = latest_date.split('-',1) 
    year = int(x[0])
    last_year = str(year-1)
    x[0] = last_year
    year_ago = '-'.join(x)


    #calculate the most active station
    ###NOTE: The rubric declares the station USC00519281 as the most active because it has the most lifetime records
    ### However, in the timeframe of the past 12 months being analyzed, 
    ### the station USC00519397 has more records with 361 over USC00519281's 352
    ### I wrote this long query that I'm very proud of and will submit the app with it. 
    ### to return the station with the most lifetime queries, simply remove the line(120)
    ### beginning with '.filter' in the below, adjacent codeblock. The code will function to the rubric then.
    activest = session.query(Measurement.station,func.count(Measurement.station).label('qty'))\
    .filter(func.strftime('%Y,%m,%d',Measurement.date) >= func.strftime('%Y,%m,%d',year_ago))\
    .group_by(Measurement.station).order_by(desc('qty')).first()
    activest = activest[0]

    #make query
    results = session.query(Measurement.date,Measurement.tobs).\
        filter(Measurement.station == activest).\
        filter(func.strftime('%Y,%m,%d',Measurement.date) >= func.strftime('%Y,%m,%d',year_ago)).\
        order_by(Measurement.date).all()

    session.close
    
    temps = []

    for date, tobs in results:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['tobs'] = tobs
        temps.append(tobs_dict)

    return #Query the dates and temperature observations of the most active station for the last year of data.

#   * Return a JSON list of temperature observations (TOBS) for the previous year.

####################################################################################
@app.route("/api/v1.0/<start>")
def start_date_only(start):
    session = Session(engine)

    results = session.query
    #choose how the input needs to be formatted.
    #query the table with a filter, filling in the input date with a '>'
    #put all tobs values into a list
    #run .mean, .min, and .max on it, putting those values into another list.

    session.close
    return
    # Return a JSON list of the minimum, the maximum, and the average temperature.
    #When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` 
    # for all dates greater than and equal to the start date.

####################################################################################
app.route('/api/v1.0/<start>/<end>')
def start_and_end_dates():
    session = Session(engine)

    results = 

    session.close
    return
    # Return a JSON list of the minimum temperature, the average temperature,
    # and the max temperature for a given start or start-end range.
    # When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` 
    # for dates between the start and end date inclusive.


####################################################################################
if __name__ == "__main__":
    app.run(debug=True)







# ## Hints

# * You will need to join the station and measurement tables for some of the queries.

# * Use Flask `jsonify` to convert your API data into a valid JSON response obj