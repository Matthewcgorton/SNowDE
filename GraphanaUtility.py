#!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3
#! python
import requests, json
import base64
import datetime
import math
import time
from   calendar import timegm

import sys, getopt
import requests
import re




class Graphana:

	""" represents a connection to ServiceNow to create and manage a change request
	"""
	
	def __init__(self, chg=''):
		self.baseurl = ''
		self.payload = ''
		self.headers = ''
		self.debug = 0
		self.headers = {"Content-Type":"application/json", "Accept":"application/json"}
		self.session = requests.Session()
#		self.session.config['keep_alive'] = False	
		

		
	def display(self):
		if self.debug == 1 :
			print("baseurl    : %s" % self.baseurl)
			print("Debug mode : %s" % self.debug)
	
		if self.debug == 3 :
			print("payload   : %s" % self.payload)


	def loadRefValues( self, filename ) : 

		with open( filename, 'rb') as f:
			read_data = f.read()
		f.closed

		if self.debug == 1 : print( len( json.loads(read_data.decode("utf-8")) ))


		self.SNowRef = json.loads(read_data.decode("utf-8"))



	def getRefValues(self, affected_ci):
		
		if affected_ci in self.SNowRef : 
			return ( self.SNowRef[ affected_ci ]['Dest'], self.SNowRef[ affected_ci ]['offset'], self.SNowRef[ affected_ci ]['opsname'])  
		else : 
			return ( '', '', '')



	def addEvent(self, event, number, description, ci, eventDate, eventType, approval, eventDest ) :

		print ( eventDate )
		utc_time = time.strptime( eventDate, "%Y-%m-%d %H:%M:%S")
		epoch_time = timegm(utc_time)
		print (epoch_time ) 
		
		
		
		refValues = self.getRefValues( ci )
		
		print( 'ref' + refValues[0]  )
		print ( 'even' + eventDest )
		
		if refValues[1] == '' : epoch_time = epoch_time + refValues[1] 
		if refValues[2] == '' : ci = refValues[2] 
		
		if refValues[0] != '' : eventDest = refValues[0] 
		else : eventDest = self.baseurl
				
		epoch_time = epoch_time + 28800
		
		print( "eventDest" + eventDest )
		
		if(self.debug >= 1) :
			print("adding %s event: '%s %s (%s) [%s] %s %s'" % (event, number, description[0:40], ci, epoch_time, eventType, approval ))

		ci = ci.replace( ',', ' ' )
		ci = ci.replace( ' ', '_' )
        

		if(self.debug >= 1) :
			print( eventDest + "/events/\" -d '", end='' )
			print( json.dumps( {"what": event + ' ' + eventType + ' ' + number + ' ' + description[0:40] + ' | ' + ci, "tags" : "Change " + ci + ' '  + eventType + ' SNow', "when" : epoch_time} )  + "'" )
		
		
		response = self.session.post(eventDest + '/events/',
		                             data=json.dumps( {"what": event + ' ' + eventType + ' ' + number + ' ' + description[0:40] + ' | ' + ci, "tags" : "Change " + ci + ' '  + eventType + ' SNow', "when" : epoch_time} ), 
		                             headers=self.headers)
	
		
		if response.status_code != 200: 
			print('Status:', response.status_code, 
			      'Headers:', response.headers, 
			      'Error Response:',response.json())
			exit()
		

		return()


	
	def addStartEvent(self, number, description, ci, eventDate, eventType, approval, eventDest) :

		self.addEvent( 'START', number, description, ci, eventDate, eventType, approval, eventDest )

		return
		
	
	def addEndEvent(self, number, description, ci, eventDate, eventType, approval, eventDest) :

		self.addEvent( 'END', number, description, ci, eventDate, eventType, approval, eventDest )

		return
		
		
		
def main(argv):
		
	
	g = Graphana()
	g.baseurl = ""
	g.debug = 1
		
	currentTimeStr = datetime.datetime.fromtimestamp( round(time.time(),0) ).strftime('%Y-%m-%d %H:%M:%S')
		
	g.addEndEvent( "CHG0067000", "This is a test two " + datetime.datetime.fromtimestamp( round(time.time(),0) ).strftime('%Y-%m-%d %H:%M:%S'), "TestApp", currentTimeStr , "START", "approved", "pre-prod"   )
	
	
if __name__ == "__main__":
   main(sys.argv[1:])	



