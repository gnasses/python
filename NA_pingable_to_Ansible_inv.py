# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 10:31:22 2019

@author: gnasses

**Convert CSV list of single type of devices to ansible hostname file**
  (Created to create ansible inventory files from a TVM Vulnerability group)
    4. Open CSV file, delete all rows and columns except device names
    5. Save as CSV
    6. Run script and enter source CSV filename and filename for Ansible inventory
"""
import csv
import util
#util.py located on ns python github

#prompt user for source and destination file
sourcefile = input("Enter the Name of the CSV file to convert to Ansible Inventory: ")
dstfile = input("Enter the Name of the destination Inventory: ")
invgroup = input("Enter the Name of the Inventory File Group: ")
print ()
print ("-- Working on CSV File -- ")
#open CSV file and generate list
with open(sourcefile, 'r') as f:
    reader = csv.reader(f)
    devlist = list(reader)
    print (devlist)
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
Leverages the Netmiko function, and RO automation user in the utils.py, and the n9kswitch01 router to ping/resolve. 
Please adapt to other routers or hosts as appropriate. 
"""
print("-- Collecting Device IP Addresses -- ") 

try:
    n9kswitch01 = util.CiscoDeviceRO(host="switch01")
    net_connect = Netmiko(**cisctc01ipt01.__dict__)

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
        except:
            print ("unable to collect device IP")
            net_connect.disconnect()
    print ("inv generated")
except:
    print ("it broke making inventory")
finally:
    net_connect.disconnect()
print ("addresses collected")
# write line to output file and reset vars
outF = open(dstfile, 'w') 
outF.write("[" + invgroup + "]")
outF.write("\n")   
for item in inv:
    outF.write(item)
    outF.write("\n")
outF.write("\n") 
outF.close()
print (" ** Inventory file created successfully ** ")
inv = []
