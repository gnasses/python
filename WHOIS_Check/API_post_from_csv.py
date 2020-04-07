# -*- coding: utf-8 -*-
"""
Created on Feb  6 09:01:49 2020
Whois API Request Demo
@author: gnasses
"""
import requests
import json
import csv
sourcefile = 'ips.csv'

#json print function
def jprint(obj):
    text = json.dumps(obj, sort_keys=True, indent=4)
    print (text)

#csv import 
with open(sourcefile, 'r') as f:
    reader = csv.reader(f)
    iplist = list(reader)
    
#loop through csv entries, format, post to API and print results in JSON format
for i in iplist:
    i = (str(i)[2:-2])
    response = requests.post("http://10.1.1.1:5016/api/"+ i)
    jprint(response.json())
