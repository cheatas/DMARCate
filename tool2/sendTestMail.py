#################################################################################
# Author: 	Yadvir Singh                  										#
# Date:		16-07-2016                 											#
# Description:                  												#
# 																				#
# 	Script that automatically sends an email  									#
#	to the reserved mailbox that is read by     								#
#	email-test.py 																#
#																				#
# Based on example from: https://docs.python.org/2/library/email-examples.html  #
#																				#
# To be set by user:															#
#																				#				
#	- smptAddress																#
#	- mailAddress																#               
#################################################################################

import smtplib
import time
from email.mime.text import MIMEText

smtpAddress = '145.100.104.165'
mailAddress = 'test@dmarc-research.nl'

#Email message content
msg = MIMEText('Test email for DMARC')

#Use the current time as an identifier in the subject line
msg['Subject'] = str(time.time())
msg['From'] = mailAddress
msg['To'] = mailAddress

# Send the message via our own SMTP server. 
s = smtplib.SMTP(smtpAddress)
s.sendmail(mailAddress, [mailAddress], msg.as_string())
s.quit()

