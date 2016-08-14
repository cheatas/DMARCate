# coding: utf-8

#################################################
# Author: 	Yadvir Singh                  		#
# Date:		14-08-2016                 			#
# Description:                  				#
# 												#
# 	Server script that listen for incomming     #
#   connections from clients. The email passed  #
#   by client is checked on SPF and DKIM        #
#   allignment. The result is written to an 	#
#	HTML file									#
#												#
# To be set by user:							#
#												#				
#	key variable    	                        #
#   certificate variable						#
#												#               
#################################################

import socket, ssl
import dkim
import spf
import sys
import re
from email.parser import Parser
import email


certificate = "cert"
key = "key"


#Function that checks the mail obtained from the client on SPF and DKIM allignment.
def checkMail (message):	

    outputFileHandle = None

    try:
        outputFileHandle = open('dmarcCheck.html', 'w')
    except:
        print "file error"
        sys.exit()


    htmlDMARCBox = ""
    htmlDKIMBox = ""
    htmlSPFBox = ""
    receivedHeader = ""
    fromHeader = ""	

    #Read the message from the inbox
    headers = email.parser.Parser().parsestr(message)


    for field in headers.items():
	    if field[0] == "Received" and "[" in field[1] and "]" in field[1]:
		    receivedHeader = field[1]

    pattern = re.compile(r'\[.*]')
    result = re.search(pattern, receivedHeader).group(0)

    pattern = re.compile(r'from .*? ')
    result2 = re.search(pattern, receivedHeader).group(0)

    subject = headers['subject']

    #Variables needed for spf check

    #We need only the email address
    if "<" in headers['from'] and ">" in headers['from']:
	    pattern = re.compile(r'\<.*>')
	    fromHeader = re.search(pattern, headers['from']).group(0)
	    fromHeader = fromHeader[1:-1]
    else:
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
    #open(mailbox, 'w').close()


def writeMailTofile(data):
    try:
        fileHandle = open('dmarcTestEmail', 'w')
        fileHandle.write(data)
        fileHandle.close()
    except:
        print "file error"
        sys.exit()


def do_something(connstream, data):
    print "do_something:", data
    
    if data[-1] == "\n" and data[-2] == "\n":
        return False


def deal_with_client(connstream):
    data = connstream.recv(8192)
    while data:
        print "in loop"
        if not do_something(connstream, data):
            break
        data = connstream.recv(8192)
    return data


def startSocket():
    bindsocket = socket.socket()
    bindsocket.bind(('localhost', 12345))
    bindsocket.listen(1)

    while True:
        newsocket, fromaddr = bindsocket.accept()
        connstream = ssl.wrap_socket(newsocket,
                                     server_side=True,
                                     certfile=certificate,
                                     keyfile=key, ssl_version = ssl.PROTOCOL_TLSv1_2)

        try:
            data = deal_with_client(connstream)
        finally:
            connstream.shutdown(socket.SHUT_RDWR)
            connstream.close()
            newsocket.close()
            break
    writeMailTofile(data)
    checkMail(data)


startSocket()

