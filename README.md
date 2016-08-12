Description
======

A DMARC deployment/monitoring tool written in python. 

Requirements
=======

* Bootstrap
* Rickshaw JS
* w3data.js. Can be found at: http://www.w3schools.com/lib/w3data.js
* python 2.7 (not tested with python 3)
* dnspython
* pythone MySQLdb
* python netaddr
* For DMARC email test:
 * pydkim 3
 * pyspf 2.0.12
 * python email
* Techsneeze's dmarc parser. Can be found at: https://github.com/techsneeze/dmarcts-report-parser/blob/master/dmarcts-report-parser.pl
* For Visualizations:
 * Matplotlib
 * numpy
 * python Tkinter
 * pyasn
 * urllib
 * json
* MySQL database

Make sure you place the database user credentials in the following files:

* parse.py
* counters.py
* graph.py
* dns-record-tracker.py
* bubble-chart.py
* heatMap-in.py
* heatMap-out.py


Tool 1 
============

This tool is meant to give the domain owner an overview of the possible sources
that can deliver DMARC reports.

Phase 1 consist of two files:

* `parse.py`
* `html-output.py`

Use `parse.py` to generate a CSV file that is accepted by `html-output.py`.
`parse.py` should be supplied with file containing the mail log. An example:

    python parse.py /var/log/mail.log

This will create a CSV file called `output.csv` which must be supplied to `html-output.py`:

    python html-output output.CSV

After running `html-output.py` a HTML called `dm-phase1.html` is created that holds the result.



Tool 2 
===========

This tool is meant to monitor the domain during the deployment/operation of DMARC. 
It provides various tools which include: current DMARC status, DMARC tester, authentication 
results and a DNS history tool. 

Phase 2 consist of the following files with their corresponding output:

* `domain-status.py` -> `domainstatus.html`
* `email-test.py` -> `dmarcCheck.html`
* `senTestMail.py`
* `counters.py` -> `counterTrust.html`, `counterForeign.html`
* `graph.py` -> `graphTrust.js`, `graphForeign.js`
* `dns-record-tracker.py`
* `dm-ph2.html`

`domain-status.py` checks the presence of several important DMARC parameters and warns the user if any of these are not configured. Additionally the current DMARC record is displayed.

`email-test.py` is a script script automatically reads the contents of a reserved mailbox after which it checks if the email is SPF and DKIM aligned.

`sendTestMail.py` can automatically send an test mail to the reserved mailbox that
is used by `email-test.py`

`counters.py` generates statistics about authentication results. The results are dived into
two sections: Trusted and Unknown sources. Each section contains an IP list that displays
the IP addresses that fall within this category and the number of messages that they have sent.
Additionally, a set of counters shows the aggregate authentication results. These include SPF, DKIM and DMARC results. The script must be supplied with a list of trusted sources like:

    python counter.py 192.0.0.1

`graph.py` generates the graphs which show DMARC authentication results over the last 30 days (by default). Like `counters.py`, this done for both trusted and unknown sources. Additionally it also generates the DNS history time line. The script must be supplied with a list of trusted sources like:

    python counter.py 192.0.0.1

`dns-record-tracker.py` tracks the SPF, DKIM and DMARC records of a domain. Any record change is saved
in the MySQL database. These records are used by `graph.py` to generate the DNS history time line.
It advised to run this script frequently when one is changing one of the 3 records (SPF, DKIM, DMARC) frequently (for example during the deployment).

The individual generated files for each widget are combined into one web interface in `dm-ph2.html`. 


Visualizations
=============

The visualizations consist of the following files:

* bubble-chart-ASN.py
* heatMap-in.py
* heatMap-out.py
* bubble-chart.py


`bubble-chart-ASN.py` generates a bubble chart to review where emails come from, in which quantities and the ratio of successful DMARC authentication results. The categorization is based on ASN numbers obtained using `pyasn`. This libary requires a BGP/MRT dump file as input. These dumps can be found at http://archive.routeviews.org/. The ASN <-> IP mapping for IPv4 and IPv6 is found in seppreate files which are not autmatically merged by `pyasn`. An mergeged file of this mapping can be found under `asn-mapping.dat` (version of 12-08-15). Additionally, a text file with the results of each AS is generated. This file is named `asn-mapping.dat`. The user can optionally call this script with the `--asn-lookup` argument which will lookup the corrosponding (orginizational) name of the AS. 

`heatMap-in.py` generates a heat map that displays the authentication results of different domains based on incoming reports. Each tile is awarded a color based on the ratio of successful authentication results against the total amount of emails. Each tile contains text fields that indicate the total number of emails, volume of emails that passed DMARC and volume of email that failed DMARC.

`heatMap-out.py` has the same functionality as `heatMap-in.py` but than for outgoing reports. Based on OpenDmarc's import functionality.

`bubble-chart.py` generates a bubble chart to review where emails come from, in which quantities and the ratio of successful DMARC authentication results. These three variables are displayed in a bubble chart. 