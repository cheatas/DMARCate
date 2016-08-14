#!/usr/bin/python

#################################################
# Author: 	Yadvir Singh                  		#
# Date:		16-07-2016                 			#
# Description:                  				#
# 												#
# 	Script that generates DMARC authentication 	#
#	graphs. Additionally, a time line with DNS  #
#	Record changes is also created.  			#
#												#
# Database variables to be set by user:			#
#												#				
#	- dbAddress									#
#	- dbName									#
#	- dbUserName								#
#	- dbPassword								#
#												#
#												#               
#################################################



import sys
import time
from datetime import date, timedelta
import MySQLdb
import socket
import struct


dbAddress = "127.0.0.1"
dbName = "dmarc"
dbUserName = "dmarc"
dbPassword = "dmarcrp2"


#Function to generate date points. By default this function will generate 
#a set of dates that contains the 30 past days from date argument.  
#based on #http://stackoverflow.com/questions/1060279/iterating-through-a-range-of-dates-in-python 
def dateItterator(date):

	dates = []
	day = timedelta(days=1)
	
	date1 = date
	date2 = date - timedelta(days=30) # Adjust date range here

	while date2 < date1:
		dates.append(date2)
		date2 += day

	return dates
	

#Funtion that prepares the HTML ouput files and reads the arguments list to 
#obtain the list of trusted sources. 
def openFile():

	domains = []
	argumentLen = len(sys.argv)
	fileHandle = None

	if argumentLen > 1:

		for x in range(1, argumentLen):
			domains.append(sys.argv[x])

		try:
			fileHandleTrusted = open('graphTrust.js', 'w')
			fileHandleForeign = open('graphForeign.js', 'w')
			return fileHandleTrusted, fileHandleForeign, domains
		except:
			print "file error"
			sys.exit()

	else:
		print "No IP address! Closing"
		sys.exit(0)

#Function to obtain all reports of trusted and unknown sources from the 
#database. 
def sqlFilterQuery(domainList):
	
	trustedString = "("

	for domain in domains:
		trustedString += str(struct.unpack("!I", socket.inet_aton(domain))[0]) + ","
	
	trustedString = trustedString[:-1]
	trustedString += ")"

	queryTrusted = "select * from report inner join rptrecord on report.serial=rptrecord.serial where ip IN " + trustedString
	queryForeign = "select * from report inner join rptrecord on report.serial=rptrecord.serial where ip NOT IN " + trustedString
	
	return queryTrusted, queryForeign

#Main function that collects information for generating the graphs 
#and the DNS history time line. 
def generateGraph(dates, query, dbAddress, dbUserName, dbPassword, dbName):
	
	dkimResult = ""
	spfResult = ""
	count = 0
	dmarcCompliant = 0
	dmarcUnCompliant = 0

	reportAggergate = []
	annotations = []


	# Open database connection
	db = MySQLdb.connect(dbAddress, dbUserName, dbPassword, dbName)

	# prepare a cursor object using cursor() method
	cursor = db.cursor()

	for date in dates:
		
		lowerbound = date - timedelta(days= 1)
		#print str(date), str(lowerbound)

		cursor.execute(query + " and maxdate <= '"+ str(date) +" 23:59:59' and mindate >= '" + str(lowerbound) + " 00:00:00'")

		data = cursor.fetchall()
		resultCount = len(data)


		# Loop through the resulting rows and populate the counters
		if not (len(data) == 0):
			
			for entry in data:

				dkimResult = entry[21]
				spfResult = entry[23]
				count = entry[17]

				#Configure strictness of DMARC check here.
				if ((dkimResult == 'pass') or (spfResult == 'pass')):
					dmarcCompliant += count
				else:
					dmarcUnCompliant += count

			
			reportAggergate.append((date, int(dmarcCompliant),int(dmarcUnCompliant)))	

			dmarcCompliant = 0
			dmarcUnCompliant = 0
	

	#Retrieve the DNS record changes from the database. 
	cursor.execute("select * from dns_records")

	data = cursor.fetchall()
	resultCount = len(data)

	for x in data:
		annotations.append(x)

	db.close()

	return reportAggergate, annotations


#Function that transform the restults of generateGraph into javascript file
def writeToFile (filehandle, data, annotations):
	
	prepend = "data: [ "

	datapointCompliant = ""
	datapointUnCompliant = ""
	annotationString = ""

	#Generate graph points
	for x in data:
		datapointCompliant += "{ x:" + str((x[0]-date(1970,1,1)).total_seconds()) + ", y:" + str(x[1]) +" },"  
		datapointUnCompliant += ("{ x:" + str((x[0]-date(1970,1,1)).total_seconds()) + ", y:" + str(x[2]) +" },")
	

	graph = """
	var palette = new Rickshaw.Color.Palette();

	var graph = new Rickshaw.Graph( {
		    element: document.querySelector("#chart"),
		    width: 550,
		    height: 250,
		    series: [
		            {
		                    name: "Dmarc UnCompliant",
		                    data: [""" + datapointUnCompliant + """],
		                    color: palette.color()
		            },
		            {
		                    name: "Dmarc Compliant",
		                    data: [""" + datapointCompliant + """],
		                    color: palette.color()
		            },
		            
		    ]
	} );

	var x_axis = new Rickshaw.Graph.Axis.Time( { graph: graph } );

	var y_axis = new Rickshaw.Graph.Axis.Y( {
		    graph: graph,
		    orientation: 'left',
		    tickFormat: Rickshaw.Fixtures.Number.formatKMBT,
		    element: document.getElementById('y_axis'),
	} );

	var legend = new Rickshaw.Graph.Legend( {
		    element: document.querySelector('#legend'),
		    graph: graph
	} );

	var annotator = new Rickshaw.Graph.Annotate({
		graph: graph,
		element: document.getElementById('timeline')
	});

	"""
	unixTime = str((x[0]-date(1970,1,1)).total_seconds())

	#Add annotations to the time line with buttons
	for data in annotations:
		annotationString += ("annotator.add(" + unixTime + ", \"<input type=\\\"button\\\" name=\\\"set_Value\\\" id=\\\"set_Value\\\" value=\\\"Review\\\" onclick=\\\"setValue('" + data[1] + "', '" + data[2] + "', '" + data[3] + "', '" + unixTime + "' )\\\" />\" );\n")


	graphEnd = """
	annotator.update();


	graph.render();

	"""


	#Write javascript files to appropriate files. 
	filehandle.write(graph)
	filehandle.write(annotationString)
	filehandle.write(graphEnd)
	filehandle.close()	


fileHandleTrusted, fileHandleForeign, domains = openFile()

trusted, foreign = sqlFilterQuery(domains)
dates = dateItterator(date(2016, 6, 30))

data, annotations = generateGraph(dates, trusted, dbAddress, dbUserName, dbPassword, dbName)
writeToFile(fileHandleTrusted, data, annotations)

data, annotations = generateGraph(dates, foreign, dbAddress, dbUserName, dbPassword, dbName)
writeToFile(fileHandleForeign, data, annotations)

