# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 21:54:59 2019

@author: gnasses
"""

import csv
from netmiko import Netmiko
import util
#util.py located on ns python github
import sys
import datetime
import os.path
save_path = 'C:/users/gnasses/AppData/Roaming/Microsoft/Windows/Templates/'
outfile = os.path.join(save_path, "vuln17.html")
orig_stdout = sys.stdout
now = str(datetime.datetime.now())
sys.stdout = open(outfile, 'w')

#prompt user for source and destination file
sourcefile = 'switch_vuln_devices.csv'
print ("{% extends 'base.html' %}")
print ("{% block head %}")
print ("{% endblock %}")
print ("{% block body %}")
print ("<h2> Results </h2>")
print ("TVM VULNERABILITY VERIFICATION<br />")
print ("Date and time of Analysis:<br />")
print (now + "<br />")
print ("<h4>BEGINNING CHECK FOR ACTIVE NX-API</h4>")
print ("Runs following command to check for active API: 'show feature | i nxapi' ")
print ("<h4>These checks cover all of R7-148264, R7-142285, R7-140163</h4>")
print ("<h4>Relevant CVEs: CVE-2019-1968,CVE-2019-1733, CVE-2019-1614</h4>")
print ("<br />")
print ("-- Working on CSV File -- <br />")
#open CSV file and generate list
with open(sourcefile, 'r') as f:
    reader = csv.reader(f)
    devlist = list(reader)
#    print (devlist)
print ("csv file processed<br />")
f.close()    

print ("-- Filtering Duplicates -- <br />")
#filter out non-unique entries using a new list
devlist1 = []
unreachables = []
for dev in devlist:
    dev = (str(dev)[2:-2])
#    print (dev)
    if dev not in devlist1:
        devlist1.append(dev)   
inv = []
print ("duplicates filtered<br />")
print ("---Analyzing Device Configurations---<br />")
print ("<br />")

try: 
    for dev in devlist1:
        try:
            router = util.CiscoDeviceRO(host=dev)
            net_connect = Netmiko(**router.__dict__)
            ver = net_connect.send_command('show version')
            hostname = net_connect.send_command('show hostname')
#        except:
#            print ("*" + dev + "*")
#            print ("--could not connect to device or run show version")
#            print ()
#            net_connect.disconnect()
            try: 
                if "NX-OS" in ver:
                    print ("<br />")
                    print (hostname.strip().split()[0] + "<br />")
                    print ("verified as nxos device <br />")
                    """
                    Check the device for enabled NX-API (Disabled by default)
                    These checks cover all of 
                    Cisco NX-OS Software NX-API Denial of Service Vulnerability - CVE-2019-1968 - R7-148264
                    Cisco NX-OS Software NX-API Sandbox Cross-Site Scripting Vulnerability - CVE-2019-1733 - R7-142285
                    Cisco NX-OS Software NX-API Command Injection Vulnerability - CVE-2019-1614 - R7-140163
                    """
                    try:
                        nxapi = net_connect.send_command('show feature | i nxapi')
    #                    print (showcfs)
                        if "enabled" in nxapi:                        
                            print ("<strong>***VULNERABLE CONFIGURATION FOUND***<br />")
                            print (nxapi + "</strong><br />")
                            print("<br />")
                        else:
                            print ("config ok (vulnerable config not present)<br />")
                            print ("<br />")
                    except:
    #                    print (dev)
    #                    print ("Timeout, or unable to collect device Info")
    #                    print()
                        net_connect.disconnect()
                    finally:
                        net_connect.disconnect()
                elif "IOS" in ver:
                    print ("ios device (not vulnerable)<br />")                    
                elif "ios" in ver:
                    print ("ios device (not vulnerable)<br />")
                else:
                    print ("neither nxos, nor ios (not vulnerable)<br />")
            except:
                print ("it broke sorting via OS<br />")
        except:
            unreachables.append(dev)
except:
    print ("it broke running the loop<br />")

finally:
    net_connect.disconnect()
    print ("*List of unreachable devices -- investigate or remove from VULN group *<br />")
    print (unreachables)
    print ("<br />")
    print ("{% endblock %}")
    unreachables = []
    devlist = []
    devlist1 = []
    sys.stdout=orig_stdout
    print ("Job Complete")    
