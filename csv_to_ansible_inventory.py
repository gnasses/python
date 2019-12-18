# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 10:09:46 2019

@author: gnasses

**Convert CSV list of devices to ansible hostname file**
  (Created to create ansible inventory files from a TVM Vulnerability group)
    1. Open Vuln Group
    2. Right click on Configuration item
    3. Select Export, then Excel (large file will have to be emailed)
    4. Open Excel file, filter out any servers or unwanted devices, delete all rows and columns except CI names
    5. Save as CSV
    6. Run script and enter source CSV filename and filename for Ansible inventory
    
    Note: This script logs in to all devices to verify NOS so it can take a LONG time to generate from a large list. 
"""
import csv
from netmiko import Netmiko
import util
#util.py located on ns python github

#prompt user for source and destination file
sourcefile = input("Enter the Name of the CSV file to convert to Ansible Inventory: ")
dstfile = input("Enter the Name of the destination Inventory: ")
print ()
print ("-- Working on CSV File -- ")
#open CSV file and generate list
with open(sourcefile, 'r') as f:
    reader = csv.reader(f)
    devlist = list(reader)
#    print (devlist)
print ("csv file processed")
#close out the file
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
"""
Code below use try/except/finally blocks to be sure to close router connections and revert lists
and also continue the loops in case the script has a problem.
Leverages the Netmiko function, and RO automation user in the utils.py, and the "ciscorouter" router to ping/resolve. 
Please adapt to other routers or hosts as appropriate. 
"""
print("-- Collecting Device IP Addresses -- ") 

try:
    ciscorouter = util.CiscoDeviceRO(host="ciscorouter)
    net_connect = Netmiko(**ciscorouter.__dict__)

    for dev in devlist1:
        try:
            print (dev)
            ping1 = net_connect.send_command('ping ' + dev)
            if "%" not in ping1:
                ip = ping1.splitlines()[1].split()[6][:-1]
            else:
                ip = ()
                print ("couldn't ping or couldn't resolve name!")
            if ip:
                invline = (dev + " ansible_host=" + ip)
                inv.append(invline)
                print ("ok")
                net_connect.disconnect()
        except:
            print ("unable to collect device IP")
            net_connect.disconnect()
    print ("inv generated")
except:
    print ("it broke making inventory")
finally:
    net_connect.disconnect()
    devlist = []
    devlist1 = []
print ("addresses collected")
print("-- Connecting to devices to sort by Network OS -- ") 
# sort this list into NXOS and non-ios devices
nxos_inv = []
ios_inv = []
unknown_inv = []
"""
Nested Try/Except blocks are used here to keep the loops running if a host has a problem or timeout
to print a messaage to the screen so you could investigate if you were watching as it ran.  
"""
try: 
    for invline in inv:
        inv_host = invline.split()[0]
        print (inv_host)
        try:
            device = util.CiscoDeviceRO(host=inv_host)
            net_connect = Netmiko(**device.__dict__)
            ver = net_connect.send_command('show version')
        except:
            print ("could not connect to device or run show version")
        try: 
            if "NX-OS" in ver:
                nxos_inv.append(invline)
                print ("nxos device")
            elif "IOS" in ver:
                ios_inv.append(invline)
                print ("ios device")
            elif "ios" in ver:
                ios_inv.append(invline)
                print ("ios device")
            else:
                unknown_inv.append(invline)  
                print ("neither nxos, nor ios")
        except:
            print ("could not sort, device not added to Inventory")
    print ("inv sorted by OS")
except:
    print ("it broke checking Network OS")
finally:
    net_connect.disconnect()     
    
# write line to output file and reset vars
outF = open(dstfile, 'w') 
outF.write("[NXOS]")
outF.write("\n")   
for item in nxos_inv:
    outF.write(item)
    outF.write("\n")
outF.write("\n") 
outF.write("[IOS]")
outF.write("\n") 
for item in ios_inv:
    outF.write(item)
    outF.write("\n")
outF.write("\n") 
outF.write("[UNKNOWN]")
outF.write("\n") 
for item in unknown_inv:
    outF.write(item)
    outF.write("\n")
outF.write("\n") 
outF.close()
print (" ** Inventory file created successfully ** ")
inv = []
nxos_inv = []
ios_inv = []
unknown_inv = []
