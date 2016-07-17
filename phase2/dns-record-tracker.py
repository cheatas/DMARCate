#################################################
# Author: 	Yadvir Singh                  		#
# Date:		17-07-2016                 			#
# Description:                  				#
# 												#
# 	Script retrieves the current SPF, DKIM and  #
#	DMARC records. These records are saved in  	#
#	the database. If DNS records have been 		#
#	changed, a new entry is inserted into 		#
#	the database 								#
#												#
# Database variables to be set by user:			#
#												#				
#	- dbAddress									#
#	- dbName									#
#	- dbUserName								#
#	- dbPassword								#
#	- domain									#
#	- dkim_id (dkim identifier)					#
#												#
#												#               
#################################################



import dns.resolver
import MySQLdb
import time


dbAddress = "127.0.0.1"
dbName = "dmarc"
dbUserName = "dmarc"
dbPassword = "dmarcrp2"
domain = "dmarc-research.nl"
dkim_id = "mail"


#Create the database connection
def DBconnect(dbAddress, dbUserName, dbPassword, dbName):

	try:
	
		db = MySQLdb.connect(dbAddress, dbUserName, dbPassword, dbName)
		return db

	except:
		return None
	

def dnsLookup(domain):
	record = ""

	try:
		answer = dns.resolver.query(domain , "TXT")
		for data in answer:
			record = str(data).replace("\"", "")
		return record
	except:
		return "None"

#Function that does a DNS lookup of SPF, DKIM and DMARC and checks if
#any of the 3 records have changed. 
def recordLookup(domain, dkim_id, db):

	dmarcRecord = ""
	dkimRecord = ""
	spfRecord = ""

	#Prepare a cursor object
	cursor = db.cursor()


	#Fetch all previous records.
	cursor.execute("select * from dns_records")

	data = cursor.fetchall();
	resultCount = len(data)
	
	#Fetch current records
	dmarcRecord = str(dnsLookup("_dmarc." + domain))
	dkimRecord = str(dnsLookup(dkim_id + "._domainkey." + domain))
	spfRecord = str(dnsLookup (domain))
	currentTime = str(time.strftime("%y-%m-%d"))


	#If no records are found in database, insert the first one.
	if resultCount == 0:

		addUpdate  = ("insert into dns_records (dmarc ,dkim, spf, dateStamp) values (%s, %s, %s, %s)" )
		cursor.execute(addUpdate, (dmarcRecord, dkimRecord, spfRecord, currentTime))
		db.commit()

	else:

		print "Not the first"

		#Check if the record is changed, if so insert the current record.
		if (dmarcRecord != data[-1][1]) or (dkimRecord != data[-1][2]) or (spfRecord != data[-1][3]):
			print "difference spotted"
			addUpdate  = ("insert into dns_records (dmarc ,dkim, spf, dateStamp) values (%s, %s, %s, %s)" )
			cursor.execute(addUpdate, (dmarcRecord, dkimRecord, spfRecord, currentTime))
			db.commit()

		else:
			print "No change detected"
	



db = DBconnect(dbAddress, dbUserName, dbPassword, dbName)
recordLookup(domain, dkim_id, db)
