#################################################
# Author: 	Yadvir Singh                  		#
# Date:		16-07-2016                 			#
# Description:                  				#
# 												#
# 	Script that parses a csv file created with 	#
#	parse.py. The contents of the csv file are  #
#	converted to an webpage. 					#
#												#
# To be set by user:							#
#												#				
#	None										#
#												#               
#################################################

import sys
import csv



def init():

	filename = sys.argv[1]
	return filename

#Function that parses the input csv file and 
#generates a HTML page. 
def parse(input_csv):

	totalCount = 0
	domainCount = 0
	dmarcPubCount = 0
	dmarcNoPubCount = 0
	domain_list = []

	f = open(input_csv, 'r')



	#Read input csv line by line	
	try:
		reader = csv.reader(f)
		for row in reader:
			print row
			domain_list.append(row)
			totalCount += int(row[1])
			if row[3] != "None":
				dmarcPubCount += 1
		domainCount = len(domain_list)
		dmarcNoPubCount = domainCount - dmarcPubCount
		
	finally:
		f.close()
	
	#The corrsonding HTML page is written to dm-ph1.html
	output = open('dm-ph1.html', 'w')
	

	header = """<!DOCTYPE html>
	<html lang="en">
		<head>
			<link href="css/bootstrap.min.css" rel="stylesheet">
			<meta name="viewport" content="width=device-width, initial-scale=1">

			<meta charset="utf-8">
		</head>

		<body>
			<!--<style type="text/css">
			   body { background: #cce6ff !important; } /* Adding !important forces the browser to overwrite the default style applied by Bootstrap */
			</style> -->


			<h1><p class="text-center">DMARC deployer</p></h1>
			<h4><p class="text-center">Phase 1</p></h4>
			<!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
			<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
			<!-- Include all compiled plugins (below), or include individual files as needed -->
			<script src="js/bootstrap.min.js"></script>
			<hr>
			<div class="row" >

				<div class="col-md-4"></div>"""
	emailCountHtml = """<div class="col-md-1">
	
  					<h1 class="text-center bg-primary"><strong>""" + str(totalCount) + """</strong></h1>
					<p class="text-center"><strong>Emails</strong></p>
				
			</div>"""
	domainCountHtml = """<div class="col-md-1" >

  					<h1 class="text-center bg-success"><strong>""" + str(domainCount) + """</strong></h1>
					<p class="text-center"><strong>Domains</strong></p>

			</div>"""
	dmarcPubHtml = """<div class="col-md-1">

  					<h1 class="text-center bg-warning"><strong>""" + str(dmarcPubCount) +"""</strong></h1>
					<p class="text-center"><strong>DMARC record published</strong></p>

			</div>""" 
	dmarcNoPubHtml = """<div class="col-md-1">

  					<h1 class="text-center bg-danger"><strong>""" + str(dmarcNoPubCount) +"""</strong></h1>
					<p class="text-center"><strong>No DMARC record published</strong></p>

			</div>""" 
	tailCountersHtml = """<div class="col-md-4"></div>

  		</div>

		<hr>"""
	startTableHtml = """<div class="row">

		
			<div class="container"> 
			  <table class="table">
			    <thead>
			      <tr>
				<th>Domain</th>
				<th>Email Volume</th>
				<th>DMARC record</th>
			      </tr>
			    </thead>
			    <tbody>"""
	pageEndHtml = """</tbody>
			  </table>
			</div>



		</div>


  </body>

</html>"""
	

	#Write all parts of webpage to the HTML file
	output.write(header)
	output.write(emailCountHtml)
	output.write(domainCountHtml)
	output.write(dmarcPubHtml)
	output.write(dmarcNoPubHtml)
	output.write(tailCountersHtml)
	output.write(startTableHtml)
	
	#Genergate the table overview
	for domain in domain_list:
		output.write("""<tr>
				<td>""" + str(domain[0]) + """</td>
				<td>""" + str(domain[1]) + """</td>
				<td>""" + str(domain[3]) + """</td>
			      </tr>""")
	
	
	output.write(pageEndHtml)
	output.close()


parse(init())
