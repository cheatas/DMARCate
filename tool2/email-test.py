# coding: utf-8

#################################################
# Author: 	Yadvir Singh                  		#
# Date:		16-07-2016                 			#
# Description:                  				#
# 												#
# 	Script that reads email out mailbox and  	#
#	checks if the email is SPF and DKIM			#
#	alignedd. The result is written to an 		#
#	HTML file									#
#												#
# To be set by user:							#
#												#				
#	mailbox variable							#
#												#               
#################################################


import dkim
import spf
import sys
import re
from email.parser import Parser


mailbox = '/var/mail/test'


#Function that creates a filehandle for writing the result
def openFile():

	try:
		fileHandleTrusted = open('dmarcCheck.html', 'w')
		return fileHandleTrusted
	except:
		print "file error"
		sys.exit()



#Function that checks mail from the defined mailbox
def checkMail (mailbox, outputFileHandle):	


	htmlDMARCBox = ""
	htmlDKIMBox = ""
	htmlSPFBox = ""


	#Read the message from the inbox
	mailBoxFileHandle = open(mailbox,'r+')
	message = mailBoxFileHandle.read()
	headers = Parser().parsestr(message)



	receivedHeader =  headers['Received']
	#print headers.items()

	pattern = re.compile(r'\[.*]')
	result = re.search(pattern, receivedHeader).group(0)

	pattern = re.compile(r'from .*? ')
	result2 = re.search(pattern, receivedHeader).group(0)


	subject = headers['subject']

	#Variables needed for spf check
	fromHeader = headers['from']
	ipaddr = result[1:-1]
	host = result2[5:-1]




	# Perfom SPF and DKIM checks
	spfResult = spf.check(i=ipaddr,s=fromHeader,h=host)
	dkimResult = dkim.verify(message ,None)


	#Create HTML conentent according to the results of the test
	if (spfResult[0] == 'pass'):
		htmlSPFBox = """<tr class="success">
					<td>SPF check passed <br><strong>↳</strong>""" + spfResult[2] + """</td>
				</tr>"""
	else:
		htmlSPFBox = """<tr class="danger">
					<td>SPF check failed <br><strong>↳</strong>""" + spfResult[2] + """</td>	
				</tr>"""
		
	if (dkimResult == True):
		htmlDKIMBox = """<tr class="success">
					<td>DKIM check passed</td>
				</tr>"""
	else:
		htmlDKIMBox = """<tr class="danger">
					<td>DKIM check failed</td>
				</tr>"""
		
	if (spfResult[0] == 'pass' or dkimResult == True):
		htmlDMARCBox = """<tr class="success">
					<td>DMARC check passed</td>
				</tr>"""
	else:
		htmlDMARCBox = """<tr class="danger">
					<td>DMARC check failed</td>
				</tr>"""		
	
		
	html = """
	<div class="well well-lg">
		<h4><p class="text-center"><strong>DMARC test</strong></p></h4>
		<table class="table table-condensed">
			<thead>
				<tr>
					<th>Result</th>
				</tr>
				<tr></tr>
			</thead>
			<tbody>
				<tr>
					<td>Subject: """ + subject + """</td>
				</tr>
				<tr><td></td></tr>
				""" + htmlDKIMBox + htmlSPFBox + """<tr><td></td></tr>""" + htmlDMARCBox + """
			</tbody>

		</table>
	</div>
	"""

	outputFileHandle.write(html)
	outputFileHandle.close()

	# Empty the mail box for the the next test, remove this line if 
	# you whish to keep the email. 
	# (Hackish way of emtying the file contents)
	open(mailbox, 'w').close()


fileHandle = openFile()
checkMail(mailbox, fileHandle)
