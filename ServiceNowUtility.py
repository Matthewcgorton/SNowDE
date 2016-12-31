#!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3
#! python
import requests, json
import base64
import datetime
import math




class ServiceNow:

	""" represents a connection to ServiceNow to create and manage a change request
	"""
	
	def __init__(self, chg=''):
		self.baseurl = ''
		self.username = ''
		self.password = ''
		self.payload = ''
		self.headers = ''
		self.sysId = ''
		self.chg = chg
		self.debug = 0
		self.headers = {"Content-Type":"application/json", "Accept":"application/json"}
		self.session = requests.Session()	
		

		
	def display(self):
		if self.debug == 1 :
			print("baseurl    : %s" % self.baseurl)
			print("Debug mode : %s" % self.debug)
	
		if self.debug == 2 :
			print("username   : %s" % self.username)
			print("password   : %s" % self.password)

		if self.debug == 3 :
			print("payload   : %s" % self.payload)



	def loopkupChangeRequest(self, chg) :

		if( chg == '') :
			exit()
		
		self.chg = chg
			
		response = self.session.get(self.baseurl + '/table/change_request?sysparm_query=number=' + self.chg, 
		                            auth=(self.username, self.password), 
		                            headers=self.headers)

		if response.status_code != 200: 
			print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())
			exit()

		self.sysId = json.loads( response.content.decode("UTF-8"))['result'][0]['sys_id']

		if(self.debug >= 1) :
			print ('Change ', self.chg, ' is sys_id', self.sysId)

		return( self.sysId )



	
		
	def createChangeRequest(self) :
		if(self.debug >= 1) :
			print("\tcreateChangeRequest method")

		if( self.chg != '') :
			print("\n\tchange already created '%s'" % self.chg)
			exit()
			
		if( self.baseurl == '') :
			print("no base url")
			exit()
		
		response = self.session.post(self.baseurl + '/table/change_request', 
		                             auth=(self.username, self.password), 
		                             data=json.dumps(self.payload), 
		                             headers=self.headers)

		if response.status_code != 201: 
			print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())
			exit()

		if(self.debug >= 2) :
			print('Status:\n',response.status_code,'\nHeaders:\n',response.headers, '\nContent:\n', response.content)



		self.changeNumber = json.loads( response.content.decode("UTF-8"))['result']['number']
		self.sysId = json.loads( response.content.decode("UTF-8"))['result']['sys_id']

		if(self.debug >= 1) :
			print ("Change :", self.changeNumber)
			print ("SysId", self.sysId)
		


			
	def approvedState(self) :
			
		response = self.session.get(self.baseurl + '/table/change_request?sys_id=' + self.sysId, 
		                            auth=(self.username, self.password), 
		                            headers=self.headers)

		if response.status_code != 200: 
			print('Status:', response.status_code, 
			      'Headers:', response.headers, 
			      'Error Response:',response.json())
			exit()

		self.approved = json.loads( response.content.decode("UTF-8"))['result'][0]['approval']
		self.state = json.loads( response.content.decode("UTF-8"))['result'][0]['state']


		if(self.debug >= 1) :
			print ('%s-' % self.state, end='', flush=True)

		return( int(self.state) )


	def isChangeWindowOpen(self) :
			
		response = self.session.get(self.baseurl + '/table/change_request?sys_id=' + self.sysId, auth=(self.username, self.password), headers=self.headers)

		if response.status_code != 200: 
			print('Status:', response.status_code, 
			      'Headers:', response.headers, 
			      'Error Response:',response.json())
			exit()

		start_time = json.loads( response.content.decode("UTF-8"))['result'][0]['start_date']

		wait_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S') - datetime.datetime.now()

		if(self.debug >= 1) :
			print ('%ss-' % math.floor(wait_time.total_seconds()), end='', flush=True)

		if wait_time.total_seconds() <= 0 :
			return( 1 )
		else:
			return( 0 )



	def updateAssignedTo(self, assigned_to ) :

		if(self.debug >= 1) :
			print("UpdateAssignedTo")
	
		if assigned_to == '' : 
			print( "assigned to is blank")
			exit()
			
		response = self.session.patch(self.baseurl + '/table/change_request/' + self.sysId, 
		                              auth=(self.username, self.password), 
		                              data=json.dumps({"assigned_to":assigned_to}), 
		                              headers=self.headers)
		
		if response.status_code != 200: 
			print('Status:', response.status_code, 
			      'Headers:', response.headers, 
			      'Error Response:',response.json())
			exit()



	def updateWorkInProgress(self) :

		if(self.debug >= 1) :
			print("Updating state : Work in Progress")
			
		
		response = self.session.patch(self.baseurl + '/table/change_request/' + self.sysId, 
		                              auth=(self.username, self.password), 
		                              data=json.dumps({'state':'9'}), 
		                              headers=self.headers)

		if response.status_code != 200: 
			print('Status:', response.status_code, 
			      'Headers:', response.headers, 
			      'Error Response:',response.json())
			exit()
		


	def updateClosed(self) :
		if(self.debug >= 1) :
			print("Updating status : Closed")
		
		response = self.session.patch(self.baseurl + '/table/change_request/' + self.sysId, 
		                              auth=(self.username, 
		                              self.password), 
		                              data=json.dumps({'state':'7', "u_closure_code": "successful"}), 
		                              headers=self.headers)

		if response.status_code != 200: 
			print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())
			exit()
		


	
	def addWorkNotes(self, notes) :

		if(self.debug >= 1) :
			print("adding notes: '%s'" % notes)

		response = self.session.put(self.baseurl + '/table/change_request/' + self.sysId, 
		                            auth=(self.username, self.password), 
		                            data=json.dumps({"work_notes":notes}), 
		                            headers=self.headers)
	
		if response.status_code != 200: 
			print('Status:', response.status_code, 
			      'Headers:', response.headers, 
			      'Error Response:',response.json())
			exit()
		
	
	
	
	def attachFile(self, filename) :

		if(self.debug >= 1) :
			print( "attaching file %s" % filename)
		
		with open(filename, 'rb') as f:
			read_data = f.read()
		f.closed

		response = self.session.post(self.baseurl + '/attachment/file?table_name=change_request&table_sys_id=' + self.sysId + '&file_name=' + filename, 
		                             auth=(self.username, self.password), 
		                             data=read_data,
		                             headers = {"Content-Type":"application/octet-stream", "Accept":"application/json"})
		                             
		if response.status_code != 201: 
			print('\nStatus:', response.status_code,
			      '\nHeaders:', response.headers,
			      '\nError Response:',response.json())
			exit()
			

	def getChangesByNumber(self, datefield, chg) :

		if( chg == '') :
			exit()
		
		self.chg = chg

		if(self.debug >= 1) :
			print( "finding %s for change: %s " % (datefield, chg))
			print( self.baseurl + '/table/change_request?sysparm_query=number=' + self.chg + "&sysparm_fields=cmdb_ci.name,number,short_description," + datefield + ",u_closure_code,u_sub_type,type,approval")

#		response = self.session.get(self.baseurl + '/table/change_request?sysparm_query=number=' + self.chg + '&sysparm_display_value=true', 
		response = self.session.get(self.baseurl + '/table/change_request?sysparm_query=number=' + self.chg + "&sysparm_fields=cmdb_ci.name,number,short_description," + datefield + ",u_closure_code,u_sub_type,type,approval", 
		                            auth=(self.username, self.password), 
		                            headers=self.headers)

		if response.status_code != 200: 
			print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())
			exit()

		return( json.loads( response.content.decode("UTF-8"))['result'] )


	def getStartDateByNumber(self, chg) :
		
		return(self.getChangesByNumber( "start_date", chg))
	
		
	def getEndDateByNumber(self, chg) :
		
		return(self.getChangesByNumber( "end_date", chg))
			
			
	def getCreatedDateByNumber(self, chg) :
		
		return(self.getChangesByNumber( "sys_created_on", chg))	
		
		


	def getChangesBetweenDates(self, dateField, startDate, endDate) :

		if(self.debug >= 1) :
			print( "finding changes where %s is between %s and %s" % (dateField, startDate, endDate))
			print( self.baseurl + "/table/change_request?sysparm_query=approval=approved^" + dateField + "BETWEENjavascript:gs.dateGenerate('" + 
									 startDate[0:10] + "','" +  startDate[11:20] + "')@javascript:gs.dateGenerate('" + 
									 endDate[0:10]   + "','" +  endDate[11:20]   + "')&sysparm_fields=cmdb_ci.name,number,short_description," + dateField + ",sys_created_on,start_date,end_date,u_closure_code,u_sub_type,type,approval")
			
			
		response = self.session.get(self.baseurl + "/table/change_request?sysparm_query=approval=approved^" + dateField + "BETWEENjavascript:gs.dateGenerate('" + 
									 startDate[0:10] + "','" +  startDate[11:20] + "')@javascript:gs.dateGenerate('" + 
									 endDate[0:10]   + "','" +  endDate[11:20]   + "')&sysparm_fields=cmdb_ci.name,number,short_description," + dateField + "sys_created_on,start_date,end_dateu_closure_code,u_sub_type,type,approval", 
		                             auth=(self.username, self.password), 
		                             headers=self.headers)


		if(self.debug >= 2) :
			print( response.content.decode("UTF-8"))


		if response.status_code != 200: 
			print('\nStatus:', response.status_code,
			      '\nHeaders:', response.headers,
			      '\nError Response:',response.json(),
			      '\nContent Response:', response.content)
			exit()
			

		return( json.loads( response.content.decode("UTF-8"))['result'] )



	def getChangesStartingBetweenDates(self, startDate, endDate) :
		
		return(self.getChangesBetweenDates( "start_date", startDate, endDate))
	
		
		
	def getChangesEndingBetweenDates(self, startDate, endDate) :
		
		return(self.getChangesBetweenDates( "end_date", startDate, endDate))
			
			
	def getChangesCreatedBetweenDates(self, startDate, endDate) :
		
		return(self.getChangesBetweenDates( "sys_created_on", startDate, endDate))	