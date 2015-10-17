"""
Very simple Flask web site, with one page
displaying a course schedule.

"""

import flask
from flask import render_template
from flask import request
from flask import url_for
from flask import jsonify # For AJAX transactions

import json
import logging

# Date handling 
import arrow # Replacement for datetime, based on moment.js
import datetime # But we still need time
from dateutil import tz  # For interpreting local times

# Our own module
# import acp_limits


###
# Globals
###
app = flask.Flask(__name__)
import CONFIG

import uuid
app.secret_key = str(uuid.uuid4())
app.debug=CONFIG.DEBUG
app.logger.setLevel(logging.DEBUG)


###
# Pages
###

@app.route("/")
@app.route("/index")
@app.route("/calc")
def index():
  app.logger.debug("Main page entry")
  return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    flask.session['linkback'] =  flask.url_for("calc")
    return flask.render_template('page_not_found.html'), 404


###############
#
# AJAX request handlers 
#   These return JSON, rather than rendering pages. 
#
###############
@app.route("/_calc_times")
def calc_times():
  """
  Calculates open/close times from miles, using rules 
  described at http://www.rusa.org/octime_alg.html.
  Expects one URL-encoded argument, the number of miles. 
  """
  app.logger.debug("Got a JSON request");
  miles = request.args.get('miles', 0, type= float)
  Brevet = request.args.get('Brevet', 1, type = float)
  dis_type = request.args.get('dis_type', " ", type = str)
  app.logger.debug(miles)
  app.logger.debug(dis_type)
  day = request.args.get('day', 0, type = str)
  time = request.args.get('time', 0, type = str)
  day_time = day + " " + time
  app.logger.debug(day_time)

  if dis_type == 'Miles':
  	miles = miles * 1.6093

  begin = arrow.get(day_time, 'MM/DD/YYYY HH:mm')
  app.logger.debug(begin)

  if(miles < 0 or miles > (Brevet * 1.1)):
  	print_out = {'OT': 'Distance is too far!', 'CT': 'Distance is too far!'}
  	print_out = json.dumps(print_out)
  	return jsonify(result = print_out)
  elif miles == 0:
  	print_out = {'OT': format_arrow_date(begin), 'CT': format_arrow_date(begin.replace(hours =+ 1))}
  	print_out = json.dumps(print_out)
  	return jsonify(result = print_out)

  if(200 <= miles and miles <= 220 and Brevet == 200):
  	OT = begin.replace(minutes =+ 200.0 / 34 * 60)
  	CT = begin.replace(minutes =+ 13.5 * 60)
  elif(300 <= miles and miles <= 330 and Brevet == 300):
  	OT = begin.replace(minutes =+ 60*((200.0/34) + (100.0/32)))
  	CT = begin.replace(minutes =+ 20.0 *60)
  elif(400 <= miles and miles <=440 and Brevet == 400):
  	OT = begin.replace(minutes =+ 60*((200.0/34) + (200.0/32)))
  	CT = begin.replace(minutes =+ 27.0*60)
  elif(600 <= miles and miles <= 660 and Brevet == 600):
  	OT = begin.replace(minutes =+ 60*((200.0/32) + (200.0/32) + (200.0/30)))
  	CT = begin.replace(minutes =+ 40.0*60)

  elif(1000 <=miles and miles<= 1100 and Brevet == 1000):
  	OT = begin.replace(minutes =+ 60*((200.0/34)+ (200.0/32) + (200.0/30) + (400.0/28)))
  	CT = begin.replace(minutes =+ 75.0 *60)
  else:
  	OT = open_time_fun(miles)
  	OT = begin.replace(minutes =+ OT)
  	CT = close_time_fun(miles)
  	CT = begin.replace(minutes =+ CT)



  
  
  
  OT = format_arrow_date(OT)
  CT = format_arrow_date(CT)
  app.logger.debug(OT)
  app.logger.debug(CT)

  print_out = {'OT': OT, 'CT':CT}
  print_out = json.dumps(print_out)
  return jsonify(result = print_out)

def open_time_fun(miles):
  	if(miles < 200):
  		#OT = begin.replace(minutes =+ miles / 34 * 60)
  		OT = miles / 34 *60
  		#app.logger.debug(OT)
  	#elif(200 <= miles and miles <= 220 and Brevet == 200):
  		#OT = begin.replace(minutes =+ 200.0 / 34 * 60)

  	elif(miles < 300):
  		#OT = begin.replace(minutes =+ 60*((200.0/34) + ((miles-200)/32)))
  		OT = 60*((200.0/34) + ((miles-200)/32))
  	#elif(300 <= miles and miles <= 330 and Brevet == 300):
  		#OT = begin.replace(minutes =+ 60*((200.0/34) + (100.0/32)))

  	elif(miles < 400):
  		#OT = begin.replace(minutes =+ 60*((200.0/34) + ((miles-200)/32)))
  		OT = 60*((200.0/34) + ((miles-200)/32))
  	#elif(400 <= miles and miles <=440 and Brevet == 400):
  		#OT = begin.replace(minutes =+ 60*((200.0/34) + (200.0/32)))

  	elif(miles < 600):
  		#OT = begin.replace(minutes =+ 60*((200.0/34) + (200.0/32) + ((miles -400)/30)))
  		OT = 60*((200.0/34) + (200.0/32) + ((miles -400)/30))
  	#elif(600 <= miles and miles <= 660 and Brevet == 600):
  		#OT = begin.replace(minutes =+ 60*((200.0/32) + (200.0/32) + (200.0/30)))

  	elif(miles < 1000):
  		#OT = begin.replace(minutes =+ 60*((200.0/34) + (200.0/32) + (200.0/30) + ((miles-600)/28)))
  		OT = 60*((200.0/34) + (200.0/32) + (200.0/30) + ((miles-600)/28))
  	#elif(1000 <=miles and miles<= 1100 and Brevet == 1000):
  		#OT = begin.replace(minutes =+ 60*((200.0/34)+ (200.0/32) + (200.0/30) + (400.0/28)))

  	return OT

def close_time_fun(miles):
  	if(miles < 600):
  		#CT = begin.replace(minutes =+ miles / 15 * 60)
  		CT = miles / 15 * 60
  	#elif(200 <= miles and miles <= 220 and Brevet == 200):
  		#CT = begin.replace(minutes =+ 13.5 * 60)

  	#elif(miles < 300):
  		#CT = begin.replace(minutes =+ miles /15 *60)
  	#elif(300 <= miles and miles <= 330 and Brevet == 300):
  		#CT = begin.replace(minutes =+ 20.0 *60)

  	#elif(miles < 400):
  		#CT = begin.replace(minutes =+ miles /15*60)
  	#elif(400 <= miles and miles <=440 and Brevet == 400):
  		#CT = begin.replace(minutes =+ 27.0*60)

  	#elif(miles < 600):
  		#CT = begin.replace(minutes =+ miles / 15*60)
  	#elif(600 <= miles and miles <= 660 and Brevet == 600):
  		#CT = begin.replace(minutes =+ 40.0*60)


  	elif(miles < 1000):
  		#CT = begin.replace(minutes =+ 60*((600/15) + ((miles-600)/11.428)))
  		CT = 60*((600/15) + ((miles-600)/11.428))
  	#elif(1000 <=miles and miles<= 1100 and Brevet == 1000):
  		#CT = begin.replace(minutes =+ 75.0 *60)

  	return CT




  
 
#################
#
# Functions used within the templates
#
#################

@app.template_filter( 'fmtdate' )
def format_arrow_date( date ):
    try: 
        normal = arrow.get( date )
        return normal.format("ddd MM/DD/YYYY HH:mm")
    except:
        return "(bad date)"

@app.template_filter( 'fmttime' )
def format_arrow_time( time ):
    try: 
        normal = arrow.get( date )
        return normal.format("hh:mm")
    except:
        return "(bad time)"



#############


if __name__ == "__main__":
    import uuid
    app.secret_key = str(uuid.uuid4())
    app.debug=CONFIG.DEBUG
    app.logger.setLevel(logging.DEBUG)
    app.run(port=CONFIG.PORT)

    
