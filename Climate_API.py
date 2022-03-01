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

    #variable...ize all routes for easier modification
    precip_page = '/api/v1.0/precipitation'
    stations_page ='/api/v1.0/stations' 
    tempobs_page = '/api/v1.0/tobs'
    startdate_page = '/api/v1.0/startdate'
    enddate_page = '/enddate'

    return (
        f"Hawaii climate application, version 1.0 is now active.<br/>" 
        f"Available Routes:<br/>"
        f"{precip_page}<br/>"
        f"{stations_page}<br/>"
        f"{tempobs_page}<br/>"
        f"{startdate_page}'YYYY-MM-DD'<br/>"
        f"{startdate_page}'YYYY-MM-DD'{enddate_page}'YYYY-MM-DD'<br/>"
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
        jsonify(all_results)
    )

####################################################################################
@app.route('/api/v1.0/stations')
def stations_list():

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
    activest = session.query(Measurement.station,func.count(Measurement.station).label('qty'))\
    .group_by(Measurement.station).order_by(desc('qty')).first()
    activest = activest[0]

    #make query
    results = session.query(Measurement.date,Measurement.tobs).\
        filter(Measurement.station == activest).\
        filter(Measurement.date >= year_ago).\
        order_by(Measurement.date).all()

    session.close
    
    temps = []

    for date, tobs in results:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['tobs'] = tobs
        temps.append(tobs_dict)

    return jsonify(temps)

####################################################################################
@app.route("/api/v1.0/startdate<startdate>")
def start_date_only(startdate):
    session = Session(engine)

    results = session.query(func.avg(Measurement.tobs),func.min(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= startdate).all()
       
    #query the table with a filter, filling in the input date with a '>'
    session.close

    tempdata = []
    
    for avg,min,max in results:
        tobs_dict = {}
        tobs_dict['Average Temperature post start date'] = avg
        tobs_dict['Minimum Temperature post start date'] = min
        tobs_dict['Maximum Temperature post start date'] = max
        tempdata.append(tobs_dict)

    return(
        jsonify(tempdata)
    )
    # return(jsonify(results))
        
       
    # Return a JSON list of the minimum, the maximum, and the average temperature.
    #When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` 
    # for all dates greater than and equal to the start date.

####################################################################################
app.route("/api/v1.0/startdate<startdate>/enddate<enddate>")
def start_and_end_dates(startdate,enddate):
    session = Session(engine)

    #same as above but with another filter
    results = session.query(func.avg(Measurement.tobs),func.min(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= startdate).\
        filter(Measurement.date <= enddate).all()

    session.close

    #all the same as above
    tempdata = []
    
    for avg,min,max in results:
        tobs_dict = {}
        tobs_dict['Average Temperature between and including start and end dates'] = avg
        tobs_dict['Minimum Temperature between and including start and end dates'] = min
        tobs_dict['Maximum Temperature between and including start and end dates'] = max
        tempdata.append(tobs_dict)

    return(
        jsonify(tempdata)
    )

    


####################################################################################
if __name__ == "__main__":
    app.run(debug=True)
