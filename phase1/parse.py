#################################################
# Author: 	Yadvir Singh                  		#
# Date:		16-07-2016                 			#
# Description:                  				#
# 												#
# 	Script that parses emails log and outputs	#
# 	a csv containing all outgoing				#
# 	email domains and their DMARC records		#
#												#
# To be set by user:							#
#												#				
#	domain variable								#
#												#               
#################################################



import sys
import re
from collections import Counter
import dns.resolver
import csv

#Setup your domain here:
domain = "dmarc-research.nl"



#Function that creates a filehandle for the mail log
def init():

	filename = sys.argv[1]
	try:
		mail_log = open(filename, 'r')
	except:
		print "File error"
		sys.exit()

	return mail_log

#Funtion that parses the email log
def parse(input_file, domain):

	tokens = input_file.readlines();
	pattern = re.compile(r'@.*?>,')
	domains = []


	#Read mail log line by line
	for token in tokens:
		fields = token.split(" ")
		result = re.findall(pattern, token)

		#We dont want emails that are sent to the domain, only outgoing emails.
		#Ugly but works for now. We need a propper domain selection tool	
		if result and ("@" + domain +">," not in result):
			print result
			domains.append(result[0].strip('@').strip('>,'))

	counts = Counter(domains)
	return counts


#Function to retrieve a DMARC record	
def dmarc_lookup(domain):
	
	answer=""
	
	try:
		answer = dns.resolver.query("_dmarc." + domain , "TXT")
		for data in answer:
			answer = data
	except:
		answer = "None"	

	return answer


#Function for writing the results to output.csv
def write_csv(values):

	f = open('output.csv', 'wt')

	try:
		writer = csv.writer(f)
		for domain in values:
			dmarc = dmarc_lookup(domain) #Lookup DMARC record of domain
			writer.writerow( (domain, values[domain], dmarc))
	
	finally:
		f.close()


domain_stats = parse(init(), domain)
write_csv(domain_stats)	
