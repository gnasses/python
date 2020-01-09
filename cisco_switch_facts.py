#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 08:29:02 2020

@author: gnasses
"""
import csv
from netmiko import Netmiko
import util

#prompt user for source and destination file
sourcefile = 'voice_switch_test.csv'
dstfile = 'voice_switch_facts.csv'
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
dedup_devices = []
header = ["Device", "Image Version", "Hardware Version"]
dedup_devices.append(header)
for dev in devlist:
    dev = (str(dev)[2:-2])
    my_device = util.CiscoDeviceRO(host=dev)
    net_connect = Netmiko(**my_device.__dict__)
#standin for parsed content    
    raw_ver = net_connect.send_command("show version")
    if "NX-OS" in raw_ver:
        version = net_connect.send_command("show version | include bootflash://")
        version = version.splitlines()[-1].split()[-1]
        version = (str(version)[13:-4])
    else:
        version = net_connect.send_command("show version | include bootdisk")
        version = version.splitlines()[-1].split()[-1]
        version = (str(version)[11:-5])
    supervisor = net_connect.send_command("show mod | include Supervisor")
    if not supervisor:
        model = net_connect.send_command("show mod")
        model = model.splitlines()[2].split()[-3]
    else:
        model = supervisor.splitlines()[-1].split()[-2]
    if "active" in model:
        model = supervisor.splitlines()[-2].split()[-2]
    print(version)
    print(model)
    net_connect.disconnect()
    dev = (dev , version , model)
    #    print (dev)
    if dev not in dedup_devices:
        dedup_devices.append(dev)   
print ("duplicates filtered")
print (dedup_devices)

with open(dstfile, 'w', newline='') as w:
    writer = csv.writer(w)
    writer.writerows(dedup_devices)
w.close() 
