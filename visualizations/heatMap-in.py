#################################################
# Author: 	Yadvir Singh                  		#
# Date:		17-07-2016                 			#
# Description:                  				#
# 												#
# 	Script that generates a heat map of 		#
#	incoming reports by name. Each tile 		#
#	contains the domain, the total number of 	#
#	email, volume of DMARC passes and DMARC 	#
#	failures. Each tile is color coded with 	#
#	a ratio. 									#
#	This ratio is calculated as: total DMARC	#
#	passes divided by total email volume. 		#
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

from __future__ import division
import matplotlib.pyplot as plt
import MySQLdb
import numpy as np
from mpl_toolkits.mplot3d import axes3d, Axes3D
import sys
import random
import string


dbAddress = "127.0.0.1"
dbName = "dmarc"
dbUserName = "dmarc"
dbPassword = "dmarcrp2"


#Main function that retrieves data from the database and populates all counters. 
def getData(dbAddress, dbName, dbUserName, dbPassword):

	domainsOfIntrest = []
	domains = []
	domainRatioList = []

	try:
		db = MySQLdb.connect(dbAddress, dbUserName, dbPassword, dbName)

	except:
		print "Error while accessing the database"


	#Fetch all organization from which reports have been received
	cursor = db.cursor()
	cursor.execute("select distinct org from report")
	queryResult = cursor.fetchall()
			
	dmarcPass = 0
	dmarcFail = 0	
	totalCount = 0	
	ratio = 0


	# Fetch authentication results per organization
	for x in queryResult:
		domain = x[0]
		cursor.execute("select * from report inner join rptrecord on report.serial=rptrecord.serial where org = \"" + domain + "\"")
		queryResult = cursor.fetchall()
		
		for row in queryResult:
			dkimResult = row[21]
			spfResult = row[23]
			count = row[17]

			if dkimResult == "pass" or spfResult == "pass":
				dmarcPass += count
			else:
				dmarcFail += count

			totalCount += count
			 
		ratio = dmarcPass/totalCount
		domainRatioList.append((domain, ratio, totalCount, dmarcPass, dmarcFail))

		dmarcPass = 0
		dmarcFail = 0
		totalCount = 0
		ratio = 0

	return domainRatioList



#Function that inserts text values in each tile. Based on:
#http://stackoverflow.com/questions/25071968/heatmap-with-text-in-each-cell-with-matplotlibs-pyplot
def show_values(pc, domainList, fmt="%.2f", **kw):
    from itertools import izip
    pc.update_scalarmappable()
    ax = pc.get_axes()
    for p, color, value, ratio in izip(pc.get_paths(), pc.get_facecolors(), pc.get_array(), domainList):
        x, y = p.vertices[:-2, :].mean(0)

		#Choose a lite color if we the tile is dark and vice versa. 
        if np.all(color[:3] > 0.5):
            color = (0.0, 0.0, 0.0)
        else:
            color = (1.0, 1.0, 1.0)
        ax.text(x, y+0.15, ratio[0], ha="center", va="center", color=color, size='large', **kw)
        ax.text(x, y-0.15, "Total " + str(ratio[2]) + "\n DMARC-P " + str(ratio[3]) + "\n DMARC-F " + str(ratio[4]), ha="center", va="center", color=color, size='x-small', **kw)


#Funtion that generates the heatmap from a list of domains and their 
#authentication results. Based on:
#http://stackoverflow.com/questions/14391959/heatmap-in-matplotlib-with-pcolor
def generateMap(ratioList):

	#If there are not enough results, populate missing tiles manually. We need
	#more elegant solution for this.
	while len(ratioList) < 36:
		ratioList.append(("",1.0,0,0,0))

	values = []


	#Uncomment the following for a demo heatmap
	"""
	demo = []

	for x in range (0,36):

		domain = ''.join(random.choice(string.lowercase) for i in range(8)) + ".com"

		total = random.randrange(0, 1000)

		dmarcPass =  random.randrange(0,total)

		dmarcFail = total - dmarcPass

		ratio = dmarcPass/total 

		demo.append((domain, ratio, total, dmarcPass, dmarcFail ))
		
	demo = sorted(demo, key=lambda x: x[1])

	ratioList = demo

	"""

	ratioList = sorted(ratioList, key=lambda x: x[1])

	for data in ratioList:
		values.append(data[1])


	#Create the tile map
	values = np.array(values).reshape((6, 6))

	column_labels = list('ABCD')
	row_labels = list('WXYZ')

	data = values
	fig, ax = plt.subplots()

	heatmap = ax.pcolor(data, cmap=plt.cm.RdYlGn, vmin = 0.0, vmax = 1.0)
	heatmap.update_scalarmappable()

	col = heatmap.get_facecolors()

	show_values(heatmap, ratioList)
	plt.colorbar(heatmap)
	plt.show()

ratioList = getData(dbAddress, dbName, dbUserName, dbPassword)
generateMap(ratioList)

