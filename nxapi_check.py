# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 16:36:56 2019

@author: gnasses
"""
import csv
from netmiko import Netmiko
import util
import sys
orig_stdout = sys.stdout
sys.stdout = open('vul0065517_vulncheck_results.txt', 'w')
#util.py located on ns python github

#prompt user for source and destination file
sourcefile = 'nxos.csv'
print ("TVM VULNERABILITY VERIFICATION IN PROCESS")
print ("BEGINNING CHECK FOR ACTIVE NX-API")
print ()
print ("-- Working on CSV File -- ")
#open CSV file and generate list
with open(sourcefile, 'r') as f:
    reader = csv.reader(f)
    devlist = list(reader)
    print (devlist)
print ("csv file processed")
f.close()    

print ("-- Filtering Duplicates -- ")
#filter out non-unique entries using a new list
devlist1 = []
for dev in devlist:
    dev = (str(dev)[2:-2])
#    print (dev)
    if dev not in devlist1:
        devlist1.append(dev)   
inv = []
print ("duplicates filtered")
print ("---Analyzing Device Configurations---")
print ()

try: 
    for dev in devlist1:
        try:
            router = util.CiscoDeviceRO(host=dev)
            net_connect = Netmiko(**router.__dict__)
            ver = net_connect.send_command('show version')
            hostname = net_connect.send_command('show hostname')
        except:
            print ("*" + dev + "*")
            print ("--could not connect to device or run show version")
            print ()
            net_connect.disconnect()
        try: 
            if "NX-OS" in ver:
                print (hostname)
                print ("nxos device")
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
                        print ("***VULNERABLE CONFIGURATION FOUND***")
                        print (nxapi)
                        print()
                    else:
                        print ("config ok (not vulnerable)")
                        print ()
                except:
                    print (dev)
                    print ("Timeout, or unable to collect device Info")
                    print()
                    net_connect.disconnect()
                finally:
                    net_connect.disconnect()
            elif "IOS" in ver:
                print ("ios device (not vulnerable)")
            elif "ios" in ver:
                print ("ios device (not vulnerable)")
            else:
                print ("neither nxos, nor ios (not vulnerable)")
        except:
            print ("it broke sorting via OS")
except:
    print ("it broke running the loop")

finally:
    net_connect.disconnect()
    devlist = []
    devlist1 = []
    sys.stdout=orig_stdout
    print ("Job Complete") 
