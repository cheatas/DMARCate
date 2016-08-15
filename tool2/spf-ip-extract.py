#################################################
# Author: 	Yadvir Singh                  		#
# Date:		15-08-2016                 			#
# Description:                  				#
# 												#
# 	Script that extracts IP addresses from  	#
#	spf records. Networks addresses are also 	#
#	supported. All addresses are written to a  	#
#	file.  										#
#												#
# 	Variables to be set by user:				#
#												#				
#	- domain									#
#												#               
#################################################




import re
import dns.resolver
import netaddr as ne

domain = "dmarc-research.nl"
ip_list = []

def writeToFile(data):
	
	fileHandle = open('trusted-list.txt', 'w')	
	
	for line in data:
		fileHandle.write(line + "\n")

	fileHandle.close()

def dnsLookup(domain):
	record = ""

	try:
		answer = dns.resolver.query(domain , "TXT")
		return str(answer[0])
	except:
		return "None"


#Start
def init():
	# Pattern based on https://gist.github.com/0x9900/4471462

	pattern = re.compile(r'ip4[:=](.*?\s)', re.IGNORECASE)
	spfRecord =  dnsLookup(domain)

	result = re.findall(pattern, spfRecord)


	#Parse IP addresses
	for x in result:
		ip = x[0:-1]

		print ip

		if "/" in ip:
			print "Dealing with complete network"
		
			ip_network = ne.IPNetwork(ip)

			for address in list(ip_network):
				ip_list.append(str(address))

		else:
			ip_list.append(ip)

	writeToFile(ip_list)
	

init()


