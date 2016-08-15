#################################################
# Author: 	Yadvir Singh                  		#
# Date:		16-07-2016                 			#
# Description:                  				#
# 												#
# 	Script that generates statistics about 	  	#
#	authentication results. This includes 		#
#	an IP list and counters of SPF, DKIM, 		#
#	and DMARC authentication results. 			#
#	The statics are generated for both 			#
#	trusted and unknown sources.				#
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
import MySQLdb
import socket
import struct
from collections import Counter


dbAddress = "127.0.0.1"
dbName = "dmarc"
dbUserName = "dmarc"
dbPassword = "dmarcrp2"


def calculateRatio(x1, x2):

	result = ""

	try:
		result = str(round((float(x1)/x2) * 100))
	except:
		result = "0"

	return result


#Function that connects to the SQL database. 
def connectToDB(dbAddress, dbUserName, dbPassword, dbName):

	try:
		db = MySQLdb.connect(dbAddress,dbUserName, dbPassword, dbName)
		return db
	except:
		return None


#Funtion that prepares the HTML ouput files and reads the arguments list to 
#obtain the list of trusted sources. 
def openFile():

	domains = []
	argumentLen = len(sys.argv)
	fileHandle = None

	trusted_list = open("trusted-list.txt", 'r')


	#Collect all trusted sources given by the the trusted list
	for line in trusted_list:
		domains.append(line[0:-1])


	if len(domains) > 0:

		#Collect all trusted sources given by the argument list
		#for x in range(1, argumentLen):
		#	domains.append(sys.argv[x])

		#Prepare output files
		try:
			fileHandleTrusted = open('counterTrust.html', 'w')
			fileHandleForeign = open('counterForeign.html', 'w')
			return fileHandleTrusted, fileHandleForeign, domains
		except:
			print "file error"
			sys.exit()
	else:
		print "No IP address! Closing"
		sys.exit(0)

	
#The main function that retrieves data from the MySQL database and generate
#statics that are written to HTML files. 	
def retrieveData(db, fileHandleTrusted, fileHanldeForeign, domains):

	ipBoxString = ""
	fileHandle = None
	trustedString = "("

	#Generate sql query to filter out only trusted domains
	for domain in domains:
		trustedString += str(struct.unpack("!I", socket.inet_aton(domain))[0]) + ","
	
	trustedString = trustedString[:-1]
	trustedString += ")"


	# prepare a cursor object using cursor() method
	cursor = db.cursor()

	#Generate statistics for both trusted and foreign hosts. 
	for domain in ["trusted", "foreign"]:

		if domain == "trusted":
			cursor.execute("select * from report inner join rptrecord on report.serial=rptrecord.serial where ip IN " + trustedString)
			fileHandle = fileHandleTrusted
		else:
			cursor.execute("select * from report inner join rptrecord on report.serial=rptrecord.serial where ip NOT IN " + trustedString)
			fileHandle = fileHanldeForeign

		data = cursor.fetchall()
		resultCount = len(data)
	
		totalCount = 0
		dkimPass = 0
		dkimFail = 0
		spfPass = 0
		spfFail = 0
		dmarcCompliant = 0
		dmarcUnCompliant = 0

		ipaddr = []


		#Acumulate authentication results
		for entry in data:

			count = entry[17]
			totalCount += count
			dkimResult = entry[21]
			spfResult = entry[24]

			for y in range (0, count):
				ipaddr.append(socket.inet_ntoa(struct.pack('!L', entry[15])))

			#Populate the authentication counters from the result of the SQL query
			if (dkimResult == 'pass'):
				dkimPass += count
			else:
				dkimFail += count

			if spfResult == 'pass':
				spfPass += count
			else:
				spfFail	+= count

			#Configure strictness of DMARC check here.
			if ((dkimResult == 'pass') or (spfResult == 'pass')):
					dmarcCompliant += count
			else:
				dmarcUnCompliant += count
			
		print domain + ":\n"
		print "Totalcount:\t" + str(totalCount) 
		print "dkim pass:\t" + str(dkimPass)
		print "dkim fail:\t" + str(dkimFail)
		print "spf pass:\t" + str(spfPass)
		print "spf fail:\t" + str(spfFail)

		# Count the number of message for each IP
		ipCount = Counter(ipaddr)

		# Generate string for Ip address box:
		for entry in ipCount:
			ipBoxString += entry + "\t|\t" + str(ipCount[entry]) + "\n------------------------------------\n"
			

		print ipBoxString






		result = """
	
	<div class="col-md-2" >
		<div class="well well-lg">
			<div class="form-group">
				<label for="comment">IP address:</label>
				<textarea class="form-control" rows="5" id="comment">""" + ipBoxString + """</textarea>
			</div>
		</div>
	</div>





	<div class="col-md-1" >
		<table style="width:100%">
		  <tr>
			<td>
				<h1 class="text-center bg-success"><strong>""" + str(dkimPass) + """</strong></h1><div class="text-center bg-success"><strong>""" + calculateRatio(dkimPass, totalCount) + """ %</strong></div>
				<p class="text-center"><strong>DKIM pass</strong></p>
			</td>
		  </tr>
		  <tr>
			<td>
				<h1 class="text-center bg-danger"><strong>""" + str(dkimFail) + """</strong></h1><div class="text-center bg-danger"><strong>""" + calculateRatio(dkimFail, totalCount) + """ %</strong></div>
				<p class="text-center"><strong>DKIM fail</strong></p>
			</td>
		  </tr>
		</table>
	</div>

	<div class="col-md-1" >
		<table style="width:100%">
		  <tr>
			<td>
				<h1 class="text-center bg-success"><strong>""" + str(spfPass) + """</strong></h1><div class="text-center bg-success"><strong>""" + calculateRatio(spfPass, totalCount) + """ %</strong></div>
				<p class="text-center"><strong>SPF pass</strong></p>
			</td>
		  </tr>
		  <tr>
			<td>
				<h1 class="text-center bg-danger"><strong>""" + str(spfFail) + """</strong></h1><div class="text-center bg-danger"><strong>""" + calculateRatio(spfFail, totalCount) + """ %</strong></div>
				<p class="text-center"><strong>SPF fail</strong></p>
			</td>
		  </tr>
		</table>
	</div>

	<div class="col-md-1" >
		<table style="width:100%">
		  <tr>
			<td>
				<h1 class="text-center  bg-primary"><strong>""" + str(totalCount) + """</strong></h1><div class="text-center bg-primary"><span style="visibility:hidden" >tekst  </span></div>
				<p class="text-center"><strong>Total count</strong></p>
			</td>
		  </tr>
		  <tr>
			<td>
				<h1 class="text-center bg-warning"><strong>""" + str(dmarcCompliant) + """</strong></h1><div class="text-center bg-warning"><strong>""" + calculateRatio(dmarcCompliant, totalCount) + """ %</strong></div>
				<p class="text-center"><strong>DMARC compliant</strong></p>
			
			</td>
		  </tr>
		</table>
	</div>


	"""

		ipBoxString = ""
		
		# Write HTML results
		fileHandle.write(result)
		fileHandle.close()



database = connectToDB(dbAddress,dbUserName, dbPassword, dbName)
fileHandleTrusted,fileHandleForeign, domains = openFile()
retrieveData(database, fileHandleTrusted, fileHandleForeign, domains)

