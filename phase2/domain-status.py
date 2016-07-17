#################################################
# Author: 	Yadvir Singh                  		#
# Date:		16-07-2016                 			#
# Description:                  				#
# 												#
# 	Script that retrieves the DMARC record  	#
#	and checks several parameters for their  	#
#	presences. Generates a HTML widget with 	#
#	the results									#
#												#
# To be set by user:							#
#												#				
#	variable domain								#
#												#               
#################################################



import dns.resolver
import sys

domain = "dmarc-research.nl"


#Funtion that creates the filehandle for writing the results
def openFile():
	
	try:
		fileHandle = open('domainstatus.html', 'w')

	except:
		print "file error"
		sys.exit()

	return fileHandle
	

#Funtion for lookup of DMARC DNS record. 	
def dnsLookup(domain):
	record = ""

	try:
		answer = dns.resolver.query('_dmarc.' + domain , "TXT")
		for data in answer:
			record = str(data).replace("\"", "")
		return record
	except:
		return "None"	
		

#Helper funtion to strip DNS results
def getSubString(string, char):
	
	try:
		IndexStart = string.index(char)
	except:
		return None	
	IndexEqual = string.index ('=', IndexStart) + 1	
	IndexEnd = string.index(';',IndexStart) 	
	
	subString = string[IndexEqual:IndexEnd]
	
	return subString


#Funtion that writes the results to an HTML file.  
def generateHtml(fileHandle, recordData):
	
	print recordData
	
	rowString = ""
	
	dmarcRecordDisection = []
	
	htmlStart = """<div class="well well-lg">
						<h4><p class="text-center"><strong>Status</strong></p></h4>
						<table class="table table-condensed">
							<thead>
							  <tr>
								<th>DMARC status</th>
							  </tr>
							</thead>
							<tbody>"""
								
	htmlEnd = """			</tbody>

  						</table>
  						<div class="form-group">
							<label>DMARC record</label>
							<input type="text" class="form-control" id="dmarcrecord" value=\"""" + recordData + """\">
						</div>
  						
					</div>
				</div>"""
	

	#Extract the parameters from the DMARC record
	policy = getSubString(recordData, "p=") 
	subPolicy = getSubString(recordData, "sp=") 
	rua = getSubString(recordData, "rua=")
	ruf = getSubString(recordData, "ruf=")  
	pct = getSubString(recordData, "pct=")
	

	dmarcRecordDisection.append(("Policy",policy))
	dmarcRecordDisection.append(("Sub-policy",subPolicy))
	dmarcRecordDisection.append(("RUA",rua))
	dmarcRecordDisection.append(("RUF",ruf))
	dmarcRecordDisection.append(("PCT",pct))


	
	#Wrap results into HTML. 
	for data in dmarcRecordDisection:
	
		if (data[1] == None) and ((data[0] == "RUA") or (data[0] == "RUF")):
			rowString += """<tr class="warning"><td>No email specified for """ + data [0] +""" reports</td></tr> \n"""
	
		elif (data[1] == None):
			rowString += """<tr class="warning"><td>No value found for """ + data [0] +"""</td></tr> \n"""
	
		else:
			rowString += """<tr class="success"><td>""" + data [0] +""" configured</td></tr> \n"""
		 
	
	
	fileHandle.write(htmlStart)
	fileHandle.write(rowString)
	fileHandle.write(htmlEnd)
	fileHandle.close()


fileHandle = openFile()
record = dnsLookup(domain)		
generateHtml(fileHandle, record)

	
	
	
	
	
	
	
