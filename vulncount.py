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

import csv
sourcefile = input("Enter the Name of the CSV file to convert to count vulns: ")

print ()
print ("-- Working on CSV File -- ")
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

sortedvulns = sorted(vulncount.items(), key =lambda a:a[1], reverse=True)
#print top 50 vulns in the list
print (sortedvulns[:50])
