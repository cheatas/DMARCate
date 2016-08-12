
#################################################
# Author: 	Yadvir Singh                  		#
# Date:		17-07-2016                 			#
# Description:                  				#
# 												#
# 	Script that generates a bubble chart to	 	#
#	review where emails come from, in which 	#
#	quantities and the ratio of successful		# 
#	DMARC authentication results	  			#
#												#
# Database variables to be set by user:			#
#												#				
#	- dbAddress									#
#	- dbName									#
#	- dbUserName								#
#	- dbPassword								#
#												#
#  Other variables to be set by the user:		#
#	- asnDatabase that contains IP <-> AN		#
#	  mapping									#
#												#
#												#               
#################################################



from __future__ import division # needed for float division in python < 3
import MySQLdb
import matplotlib.pyplot as plt
import collections
import numpy as np
import random
import pyasn
import struct
import netaddr
import urllib
import json
import sys


dbAddress = "127.0.0.1"
dbName = "dmarc"
dbUserName = "dmarc"
dbPassword = "dmarcrp2"
asnDatabase = 'asn-mapping.dat'

ASvolume = {}
asndb = pyasn.pyasn(asnDatabase)

lookup = False
output = open('asn-list.txt', 'w')


#Convert MySQL binary blob data to IPv6 string
def convertIPv6(ipv6):

	ipv6String = ""
	octetCount = 0

	for a in ipv6:
		hexValue = hex(int(struct.unpack('!B', a)[0]))[2:]
	
		if len(hexValue) < 2:
			hexValue = "0" + hexValue
			
		ipv6String = ipv6String + hexValue
		octetCount += 1

		if octetCount == 2:
			ipv6String += ":"
			octetCount = 0
			
	return ipv6String[:-1]


#Get name linked to the AS
def getASNdata(asn):
	url = "http://rdap.arin.net/bootstrap/autnum/" + str(asn)
	response = urllib.urlopen(url)
	data = json.loads(response.read())
	return data['name']


#Check if the user wants to lookup ASN names
if len(sys.argv) > 1:
	argument = sys.argv[1]
	if argument == '--asn-lookup':		
		lookup = True
		print "ASN lookup enabled"

try:
	db = MySQLdb.connect(dbAddress, dbUserName, dbPassword, dbName)
except:
	print "Error while accessing the database"

cursor = db.cursor()

#Fetch all reports that are neede for the bubble chart
cursor.execute("select * from report inner join rptrecord on report.serial=rptrecord.serial")
queryResult = cursor.fetchall()


#Parse result and count total volume and successful authentication results. 
for x in queryResult:
	ip = x[15]
	ipv6 = x[16]
	ipv6String = None
	dkimResult = x[21]
	spfResult = x[23]
	count = x[17]

	
	#Check if the address is IPv4 or IPv6 and retrieve the ASN
	if ipv6 == None:
		ASnumber = asndb.lookup(str(netaddr.IPAddress(ip)))[0]
	else:
		#The binary blob from the MySQL database needs to be converted to a 
		#IPv6 string first.
		ipv6String = convertIPv6(ipv6)
		ASnumber = asndb.lookup(str(netaddr.IPAddress(ipv6String)))[0]

	try:
		volume = ASvolume[ASnumber]
		dmarcPassCount = volume[0]
		volumeCount = volume[1]
	
		if dkimResult == "pass" or spfResult == "pass":
			dmarcPassCount += count
			volumeCount += count
		else:
			volumeCount += count

		ASvolume[ASnumber] = (dmarcPassCount, volumeCount)

	except:
		#Apperently we are the first to insert something for this IP block
		if dkimResult == "pass" or spfResult == "pass":
			ASvolume[ASnumber] = (count, count)
		else:
			ASvolume[ASnumber] = (0, count)
		


#Calculate the ratio of each IP chunk
for key, value in ASvolume.iteritems():
	dmarcPass = value[0]
	totalCount = value[1]

	ratio = dmarcPass / totalCount
	ASvolume[key] = (dmarcPass, totalCount , ratio)

fig, ax = plt.subplots()
xAxis = []
yAxis = []
volume = []
ip = []
ratioList = []
chunkIP = None
chunkRatio  = None
chunkVolume = None


#Comment in this section for creating real bubble chart
'''for key, value in ASvolume.iteritems():

	ASnumber = key
	chunkVolume = value[1]
	chunkRatio = value[2]

	ip.append(chunkIP)
	volume.append(chunkVolume)
	ratioList.append(chunkRatio)

	xAxis.append(int(ASnumber))
	yAxis.append(chunkRatio)
	if(total < 10000):
		ax.annotate(str(ASnumber), (xAxis[-1]+(chunkVolume/3), yAxis[-1]), size=20)
	else:
		ax.annotate(str(ASnumber), (xAxis[-1]+(chunkVolume/10), yAxis[-1]), size=20)
	'''

#For demo purposes only. Comment out and comment in for loop above if
#you want to generate the bubble chart for a real domain
#############Demo start
for x in range (0,4):

	ASNrandom = random.randrange(0, 30000)

	while ASNrandom in ip:
		ASNrandom = random.randrange(0, 30000)
	
	ip.append(ASNrandom)
	total = random.randrange(0, 1000)

	ratio = random.random()
	
	ratioList.append(ratio)

	xAxis.append(ASNrandom)
	yAxis.append(ratio)

	
	if(total < 10000):
		ax.annotate(str(ASNrandom), (xAxis[-1]+int(total/3), yAxis[-1]), size=20)
	else:
		ax.annotate(str(1103), (xAxis[-1]+int(total/10), yAxis[-1]), size=20)

	volume.append(total)


#############Demo end

ax.scatter(xAxis, yAxis, s=volume, marker='o', c=ratioList, cmap=plt.cm.RdYlGn, vmin=0, vmax=1)
ax.set_ylim(bottom=-0.1)
ax.set_xlim(left=0, right=max(xAxis)+5000)
ax.set_xlabel('AS Number')
ax.set_ylabel('Ratio')

plt.show()


#Generate asn list which holds volume and ratio per AS
if lookup:
	for	asn, value in ASvolume.iteritems():
		output.write("----- " + str(asn) + " -----\n")
		output.write("Name: \t\t" + getASNdata(asn) + "\n")
		output.write("Ratio: \t\t" + str(value[2]) + "\n")
		output.write("Volume: \t" + str(value[1]) + "\n")
		output.write("\n\n")
else:
	for	asn, value in ASvolume.iteritems():
		output.write("----- " + str(asn) + " -----\n")
		output.write("Ratio: \t\t" + str(value[2]) + "\n")
		output.write("Volume: \t" + str(value[1]) + "\n")
		output.write("\n\n")

output.close()
	


