# -*- coding: utf-8 -*-
"""
Created on Thu Nov  8 15:32:46 2019

@author: gnasses

"""
import csv
from netmiko import Netmiko
import util
import sys
orig_stdout = sys.stdout
sys.stdout = open('VUL0065238_vulncheck_results.txt', 'w')
#util.py located on ns python github

#prompt user for source and destination file
sourcefile = 'nxos.csv'
print ()
print ("TVM VULNERABILITY VERIFICATION IN PROCESS")
print ("BEGINNING CHECK FOR ACTIVE CISCO FABRIC SERVICE DISTRIBUTION")
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
            net_connect.disconnect()
        try: 
            if "NX-OS" in ver:
                print (hostname)
                print ("nxos device")
                """
                Check the CFS service for either CFSoE or CFSoIP
                These checks cover all of 
                R7-148243, R7-128842, R7-128864, R7-128900
                CVE-2018-0304, CVE-2018-314, CVE-2018-308, CVE-2019-1962
                """
                try:
                    showcfs = net_connect.send_command('show run | i cfs')
#                    print (showcfs)
                    if "distribute" in showcfs:                        
                        print ("***VULNERABLE CONFIGURATION FOUND***")
                        show_cfs_status = net_connect.send_command('show cfs status')
                        print (show_cfs_status)
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
                    net_connect.disconnect(                    
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
