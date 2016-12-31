#!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3
#test

import sys, getopt
import requests
import re
import time
import json
import datetime


from ServiceNowUtility import ServiceNow
from GraphanaUtility import Graphana



def getSNowValues( change):
		
		if   'start_date'     in change : eventDate = change[ 'start_date' ]
		elif 'end_date'       in change : eventDate = change[ 'end_date' ]
		elif 'sys_created_on' in change : eventDate = change[ 'sys_created_on' ]
		else : 
			eventDate = "1970-01-01 00:00:00"
			print ( 'unknown date' )


		eventDest = 'prod'
		eventType = ""

		if change['type']  == 'planned' :		## override if the sub type is buinessevent
			if change['u_sub_type'] == 'businessevent'  : eventType = 'BUS_EVENT'
			if change['u_sub_type'] == 'small_crb' 		: eventType = 'PLN_CRB'		
			if change['u_sub_type'] == 'cycled_deploy' 	: eventType = 'PLN_CYC'	
		elif change['type']  == 'continuous_delivery' 	: eventType = 'PLN_CD'
		elif change['type']  == 'emergency' 			: eventType = 'EMERGENCY'
		elif change['type']  == 'pre_prod' 			: 
			eventType = 'PLN CRB'
			eventDest = 'pre-prod'
		elif change['type']  == 'fast_track' :
		 	if change['u_sub_type'] == 'non_exempt' 	: eventType = 'PLN_FTK_EMP'	
		 	else										: eventType = 'PLN_FTK'	
		else : 
			eventType = 'UNKNOWN'
			print( 'UNKNOWN change type >>>> ' + change['type'] + " : " )
			
		return( eventDate, eventType, eventDest )
		

def main(argv):

	debug = 0
	username = ''
	password = ''
	env = '-'
	sysId = ''
	chg = ''
	filename = ''
	change = []
	gbaseurl = ''
	

	try:
			opts, args = getopt.getopt(argv,"h:u:p:d:g:b:",["username=","password=","debug=", "group=", "file=", "sys=", "chg=", "env=", "gbaseurl"])
	except getopt.GetoptError:
		print('unknown error')
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-h':
			print ('Snowv2.py --e=[dev|test] [--chg==CHG00????? | --sysid=<sysid>]--file=<testresultsfile>--d=[1-9]' )
			sys.exit()
		elif opt in ("-d", "--debug"):
			if   arg == '1' : debug = 1
			elif arg == '2' : debug = 2
			elif arg == '3' : debug = 3
		elif opt in ("-e", "--env"):
			if   arg == 'dev' : 		env = 'dev'
			elif arg == 'test' : 		env = 'test'
		elif opt in ("--sys"):				sysId = arg
		elif opt in ("--file"):				filename = arg
		elif opt in ("--chg"):				chg = arg
		elif opt in ("-u", "--username"):	username = arg
		elif opt in ("-p", "--password"):	password = arg
		elif opt in ("-b", "--gbaseurl"):   
			if	 arg == 'prod-retail' :  gbaseurl = 'http://graphite.sf.gid.gap.com'
			elif arg == 'prod' 		  :  gbaseurl = 'http://graphite.sf.gid.gap.com'
			elif arg == 'pre-prod'	  :  gbaseurl = 'http://graphite.sf.gid.gap.com'

	print( 'asdf')


	if   env == 'test' :	baseurl = 'https://gaptechtest.service-now.com/api/now'
	elif env == 'dev'  :	baseurl = 'https://gaptechdev.service-now.com/api/now'
	else :
		print("Unknown environment (--env=%s)" % env)
		exit(1)
	
	
	
	g = Graphana()
	

	
	g.baseurl = gbaseurl
	g.debug = debug
	
	
	
	s = ServiceNow(chg)

	s.baseurl = baseurl
	s.debug = debug

		
	with open('creds.txt', 'rb') as f:
		read_data = f.read()
	f.closed

	s.username = json.loads(read_data.decode("utf-8"))['username']
	s.password = json.loads(read_data.decode("utf-8"))['password']
	

# load Snow reference data

	print( "loading SNow reference data" )
	g.loadRefValues( 'SNowRef.txt' )


	
# get changes that have started  

	if (chg != '') :
		if(debug >= 1) : print("Get start data for change : " + chg)
		changes = s.getStartDateByNumber(chg)
	else : 
		if(debug >= 1) : print("Get Changes that should have started ")
		changes = s.getChangesStartingBetweenDates( '2016-10-05 14:52:39', '2016-10-06 14:59:39' )
	

# step through changes
	for index in range(len(changes)) :
	
		eventDate, eventType, eventDest = getSNowValues( changes[index] )
		print( eventDate )

		if 'cmdb_ci.name' in changes[index]  : 
			g.addStartEvent( changes[index]['number'], changes[index]['short_description'], changes[index]['cmdb_ci.name'], eventDate, eventType, changes[index]['approval'], eventDest )
		else :
			print ( "\n>>>> SKIPPING" + eventType )



# get changes that have ended  


	if (chg != '') :
		if(debug >= 1) : print("Get start data for change : " + chg)
		changes = s.getEndDateByNumber(chg)
	else : 
		if(debug >= 1) : print("Get Changes that should have completed")
		changes = s.getChangesEndingBetweenDates( '2016-10-05 00:52:39', '2016-10-06 16:52:39' )


	for index in range(len(changes)) :
	
		eventDate, eventType, eventDest = getSNowValues( changes[index] )
		print( eventDate )
		
		if 'cmdb_ci.name' in changes[index]  : 
			g.addEndEvent( changes[index]['number'], changes[index]['short_description'], changes[index]['cmdb_ci.name'], eventDate, eventType, changes[index]['approval'], eventDest )
		else :
			print ( "\n>>>> SKIPPING" + eventType )




	
if __name__ == "__main__":
   main(sys.argv[1:])	








