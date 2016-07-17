
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
#												#               
#################################################



from __future__ import division # needed for float division in python < 3
import netaddr as ne
import MySQLdb
import matplotlib.pyplot as plt
import collections
import numpy as np
import random


dbAddress = "127.0.0.1"
dbName = "dmarc"
dbUserName = "dmarc"
dbPassword = "dmarcrp2"


ipVolume = {}


#The complete IPv4 Space divided into 256 chunks. Used for categorization.
ipBlocks = ['0.0.0.0/8', '1.0.0.0/8', '2.0.0.0/8', '3.0.0.0/8', '4.0.0.0/8', '5.0.0.0/8', '6.0.0.0/8', '7.0.0.0/8', '8.0.0.0/8', '9.0.0.0/8', '10.0.0.0/8', '11.0.0.0/8', '12.0.0.0/8', '13.0.0.0/8', '14.0.0.0/8', '15.0.0.0/8', '16.0.0.0/8', '17.0.0.0/8', '18.0.0.0/8', '19.0.0.0/8', '20.0.0.0/8', '21.0.0.0/8', '22.0.0.0/8', '23.0.0.0/8', '24.0.0.0/8', '25.0.0.0/8', '26.0.0.0/8', '27.0.0.0/8', '28.0.0.0/8', '29.0.0.0/8', '30.0.0.0/8', '31.0.0.0/8', '32.0.0.0/8', '33.0.0.0/8', '34.0.0.0/8', '35.0.0.0/8', '36.0.0.0/8', '37.0.0.0/8', '38.0.0.0/8', '39.0.0.0/8', '40.0.0.0/8', '41.0.0.0/8', '42.0.0.0/8', '43.0.0.0/8', '44.0.0.0/8', '45.0.0.0/8', '46.0.0.0/8', '47.0.0.0/8', '48.0.0.0/8', '49.0.0.0/8', '50.0.0.0/8', '51.0.0.0/8', '52.0.0.0/8', '53.0.0.0/8', '54.0.0.0/8', '55.0.0.0/8', '56.0.0.0/8', '57.0.0.0/8', '58.0.0.0/8', '59.0.0.0/8', '60.0.0.0/8', '61.0.0.0/8', '62.0.0.0/8', '63.0.0.0/8', '64.0.0.0/8', '65.0.0.0/8', '66.0.0.0/8', '67.0.0.0/8', '68.0.0.0/8', '69.0.0.0/8', '70.0.0.0/8', '71.0.0.0/8', '72.0.0.0/8', '73.0.0.0/8', '74.0.0.0/8', '75.0.0.0/8', '76.0.0.0/8', '77.0.0.0/8', '78.0.0.0/8', '79.0.0.0/8', '80.0.0.0/8', '81.0.0.0/8', '82.0.0.0/8', '83.0.0.0/8', '84.0.0.0/8', '85.0.0.0/8', '86.0.0.0/8', '87.0.0.0/8', '88.0.0.0/8', '89.0.0.0/8', '90.0.0.0/8', '91.0.0.0/8', '92.0.0.0/8', '93.0.0.0/8', '94.0.0.0/8', '95.0.0.0/8', '96.0.0.0/8', '97.0.0.0/8', '98.0.0.0/8', '99.0.0.0/8', '100.0.0.0/8', '101.0.0.0/8', '102.0.0.0/8', '103.0.0.0/8', '104.0.0.0/8', '105.0.0.0/8', '106.0.0.0/8', '107.0.0.0/8', '108.0.0.0/8', '109.0.0.0/8', '110.0.0.0/8', '111.0.0.0/8', '112.0.0.0/8', '113.0.0.0/8', '114.0.0.0/8', '115.0.0.0/8', '116.0.0.0/8', '117.0.0.0/8', '118.0.0.0/8', '119.0.0.0/8', '120.0.0.0/8', '121.0.0.0/8', '122.0.0.0/8', '123.0.0.0/8', '124.0.0.0/8', '125.0.0.0/8', '126.0.0.0/8', '127.0.0.0/8', '128.0.0.0/8', '129.0.0.0/8', '130.0.0.0/8', '131.0.0.0/8', '132.0.0.0/8', '133.0.0.0/8', '134.0.0.0/8', '135.0.0.0/8', '136.0.0.0/8', '137.0.0.0/8', '138.0.0.0/8', '139.0.0.0/8', '140.0.0.0/8', '141.0.0.0/8', '142.0.0.0/8', '143.0.0.0/8', '144.0.0.0/8', '145.0.0.0/8', '146.0.0.0/8', '147.0.0.0/8', '148.0.0.0/8', '149.0.0.0/8', '150.0.0.0/8', '151.0.0.0/8', '152.0.0.0/8', '153.0.0.0/8', '154.0.0.0/8', '155.0.0.0/8', '156.0.0.0/8', '157.0.0.0/8', '158.0.0.0/8', '159.0.0.0/8', '160.0.0.0/8', '161.0.0.0/8', '162.0.0.0/8', '163.0.0.0/8', '164.0.0.0/8', '165.0.0.0/8', '166.0.0.0/8', '167.0.0.0/8', '168.0.0.0/8', '169.0.0.0/8', '170.0.0.0/8', '171.0.0.0/8', '172.0.0.0/8', '173.0.0.0/8', '174.0.0.0/8', '175.0.0.0/8', '176.0.0.0/8', '177.0.0.0/8', '178.0.0.0/8', '179.0.0.0/8', '180.0.0.0/8', '181.0.0.0/8', '182.0.0.0/8', '183.0.0.0/8', '184.0.0.0/8', '185.0.0.0/8', '186.0.0.0/8', '187.0.0.0/8', '188.0.0.0/8', '189.0.0.0/8', '190.0.0.0/8', '191.0.0.0/8', '192.0.0.0/8', '193.0.0.0/8', '194.0.0.0/8', '195.0.0.0/8', '196.0.0.0/8', '197.0.0.0/8', '198.0.0.0/8', '199.0.0.0/8', '200.0.0.0/8', '201.0.0.0/8', '202.0.0.0/8', '203.0.0.0/8', '204.0.0.0/8', '205.0.0.0/8', '206.0.0.0/8', '207.0.0.0/8', '208.0.0.0/8', '209.0.0.0/8', '210.0.0.0/8', '211.0.0.0/8', '212.0.0.0/8', '213.0.0.0/8', '214.0.0.0/8', '215.0.0.0/8', '216.0.0.0/8', '217.0.0.0/8', '218.0.0.0/8', '219.0.0.0/8', '220.0.0.0/8', '221.0.0.0/8', '222.0.0.0/8', '223.0.0.0/8', '224.0.0.0/8', '225.0.0.0/8', '226.0.0.0/8', '227.0.0.0/8', '228.0.0.0/8', '229.0.0.0/8', '230.0.0.0/8', '231.0.0.0/8', '232.0.0.0/8', '233.0.0.0/8', '234.0.0.0/8', '235.0.0.0/8', '236.0.0.0/8', '237.0.0.0/8', '238.0.0.0/8', '239.0.0.0/8', '240.0.0.0/8', '241.0.0.0/8', '242.0.0.0/8', '243.0.0.0/8', '244.0.0.0/8', '245.0.0.0/8', '246.0.0.0/8', '247.0.0.0/8', '248.0.0.0/8', '249.0.0.0/8', '250.0.0.0/8', '251.0.0.0/8', '252.0.0.0/8', '253.0.0.0/8', '254.0.0.0/8', '255.0.0.0/8']


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
	dkimResult = x[21]
	spfResult = x[23]
	count = x[17]		


	# Categorize the IP address from the report into one of the 256 IP chunks.
	ipSpace = str(ne.all_matching_cidrs(ip, ipBlocks)[0])

	try:
		volume = ipVolume[ipSpace]
		dmarcPassCount = volume[0]
		volumeCount = volume[1]
	
		if dkimResult == "pass" or spfResult == "pass":
			dmarcPassCount += count
			volumeCount += count
		else:
			volumeCount += count

		ipVolume[ipSpace] = (dmarcPassCount, volumeCount)

	except:
		#Apperently we are the first to insert something for this IP block
		if dkimResult == "pass" or spfResult == "pass":
			ipVolume[ipSpace] = (count, count)
		else:
			ipVolume[ipSpace] = (0, count)
		


#Calculate the ratio of each IP chunk
for key, value in ipVolume.iteritems():
	dmarcPass = value[0]
	totalCount = value[1]

	ratio = dmarcPass / totalCount
	ipVolume[key] = (dmarcPass, totalCount , ratio)


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
"""for key, value in ipVolume.iteritems():

	chunkIP = key.partition(".")[0]
	chunkVolume = value[1]
	chunkRatio = value[2]


	print int(chunkIP)

	ip.append(chunkIP)
	volume.append(chunkVolume)
	ratioList.append(chunkRatio)

	xAxis.append(int(chunkIP))
        yAxis.append(chunkRatio)

        ax.annotate(str(chunkIP), (xAxis[-1]+(chunkVolume/600), yAxis[-1]), size=20)	

"""

#For demo purposes only. Comment out and comment in for loop above if
#you want to generate the bubble chart for a real domain
for x in range (0,12):

	ipRandom = random.randrange(0, 256)

	while ipRandom in ip:
		ipRandom = random.randrange(0, 256)
	
	ip.append(ipRandom)
	total = random.randrange(0, 10000)

	ratio = random.random()
	
	ratioList.append(ratio)

	xAxis.append(ipRandom)
	yAxis.append(ratio)

	ax.annotate(str(ipRandom), (xAxis[-1]+(total/600), yAxis[-1]), size=20)

	volume.append(total)

ax.scatter(xAxis, yAxis, s=volume, marker='o', c=ratioList, cmap=plt.cm.RdYlGn)
ax.set_ylim(bottom=0)
ax.set_xlabel('IP chunk')
ax.set_ylabel('Ratio')

plt.show()

