# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 08:46:13 2019

@author: gnasses
**Find largest count of Vulns from a Vuln group**
  (Created to find which Vulns to target to create greatest potential reduction in ServiceNow TVM numbers)
    1. Open Vuln Group
    2. Right click on Configuration item
    3. Select Export, then Excel (large file will have to be emailed)
    4. Open Excel file, filter out any servers or unwanted devices, columns except Vulnerability, delete first row woith description
    5. Save as CSV
    6. Run script and enter source CSV filename
"""
import sys
import datetime
import os.path
from pprint import pprint
save_path = 'C:/users/gnasses/AppData/Roaming/Microsoft/Windows/Templates/'
outfile = os.path.join(save_path, "vulncount.html")
orig_stdout = sys.stdout
now = str(datetime.datetime.now())
sys.stdout = open(outfile, 'w')
sourcefile = 'vulns.csv'
print ("{% extends 'base.html' %}")
print ("{% block head %}")
print ("{% endblock %}")
print ("{% block body %}")
print ("<h2> List of Sorted Vulnerabilities by Count </h2>")
print ()
print ("Date and time of Analysis:<br />")
print (now + "<br />")
print ()
#open CSV file and generate list
with open(sourcefile, 'r') as f:
    vulnstring = list(f)

vulncount = {}

vulnlist = vulnstring
for vuln in vulnlist:
    vuln = vuln[:-1]
    if vuln in vulncount:
        vulncount[vuln] +=1
    else:
        vulncount[vuln] = 1

print ("csv file processed")
print ("<br />")
print ("<br />")
f.close() 
sortedvulns = sorted(vulncount.items(), key =lambda a:a[1], reverse=True)
print ("<h4>top 50 vulns in the list</h4>")
print (*sortedvulns[:50], sep="\n")
print ("<br />")
print ("<br />")
print ("Return to Automation Demos Home Page")
print ('<a href="/">Go to Home</a>')
print ("{% endblock %}")
sys.stdout=orig_stdout
print ("Job Complete") 
