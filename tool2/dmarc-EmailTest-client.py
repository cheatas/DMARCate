# coding: utf-8

#################################################
# Author: 	Yadvir Singh                  		#
# Date:		14-08-2016                 			#
# Description:                  				#
# 												#
# 	Client script that reads email from a       # 
#   reserved mailbox. The complete email        #
#   (including headers) is sent to the server   #
#   over a secure channel 		                #
#												#
#   SSL connection based on:                    #
#                                               #
#   https://carlo-hamalainen.net/blog           #
#   /2013/1/24/python-ssl-socket-echo-          #
#   test-with-self-signed-certificate           #
#	                                			#
# To be set by user:							#
#												#				
#	mailbox variable	                        #
#   certificate variable						#
#												#               
#################################################


import socket, ssl
import os
import time

mailbox = 'domain.txt'
certificate = "cert"

#Check if any mail is present in the reserved mailbox. 
#If so, sent the mail including all the headers over the secure channel. 
def poll():

    while True:
        mailBoxFileHandle = open(mailbox,'r+')
        message = mailBoxFileHandle.read()

        #Check if message is not empty
        if len(message) > 10:
            send(message)
            mailBoxFileHandle.close()
        
            
            # Empty the mail box for the the next test, remove this line if 
            # you whish to keep the email. 
            # (Hackish way of emtying the file contents)
            open(mailbox, 'w').close()

        time.sleep(5)

#Function that builds a secure connection between the client and server. 
def send(data):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Require a certificate from the server. We used a self-signed certificate
    # so here ca_certs must be the server certificate itself.
    ssl_sock = ssl.wrap_socket(s,
                               ca_certs=certificate,
                               cert_reqs=ssl.CERT_REQUIRED)


    ssl_sock.connect(('localhost', 12345))
    ssl_sock.write(data)
    ssl_sock.close()




poll()

