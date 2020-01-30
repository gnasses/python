#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  25  2020

@author: gnasses
"""
import csv
from netmiko import Netmiko
import util
import datetime
import re
#import cgi
#import cgitb
#
#cgitb.enable()
#form = cgi.FieldStorage()
#hostname = form.getfirst('content4')
hostname = 'n9k05'
#hostname = 'c6k13'
#hostname = 'n7k01'
#dstfile = 'pre_checkout.csv'
print("Content-Type: text/html\n\n")
print('''<style>
table {
  border-collapse: collapse;
}

td, th {
  border: 1px solid black;
  text-align: left;
  padding: 8px;
}

tr:nth-child(even) {
  background-color: #dddddd;
}
</style>''')
now = str(datetime.datetime.now())
print ("<b>Pre-Change Checkout for device: " + hostname + "</b><br /> Checkout time: " + now + "<br />")
switch = util.CiscoDeviceRO(host=hostname)
net_connect = Netmiko(**switch.__dict__)
sw_ver = util.nxos_check(hostname)
vrf_list = util.vrf_list(hostname)
#print (vrf_list)
if sw_ver == "nxos":
    for vrf in vrf_list:
        dstfile = (hostname + "." + vrf + ".pre_checkout.csv")  
        arp_raw = net_connect.send_command("show ip arp vrf " + vrf)
        iplist = util.iplist(arp_raw)
        print ("ARP Entries for VRF " + vrf + ": " + str(len(iplist)) + "<table><caption>VRF: " + vrf + " : ARP Entry Ping status</caption><tr><th>IP Address</th><th>Ping Status</th>")
        with open(dstfile, 'w', newline='') as w:            
            for ipentry in iplist:
                iping = net_connect.send_command("ping " + ipentry + " vrf " + vrf + " count 2")
                if "100.00% packet loss" not in iping: 
                    status = "Success"
                else: 
                    status = "Fail"
                print ("<tr><td>" + ipentry + "</td><td>" + status + "</td></tr>")
                writer = csv.writer(w)
                writer.writerow([ipentry, status])                
        w.close()
        print ("</table>")
if sw_ver == "ios":
    for vrf in vrf_list: 
        dstfile = (hostname + "." + vrf + ".pre_checkout.csv")
        arp_raw = net_connect.send_command("show ip arp vrf " + vrf)
        iplist = util.iplist(arp_raw)
        print ("ARP Entries for VRF " + vrf + ": " + str(len(iplist)) + "<table><caption>VRF: " + vrf + " : ARP Entry Ping status</caption><tr><th>IP Address</th><th>Ping Status</th>")
        with open(dstfile, 'w', newline='') as w:  
            for ipentry in iplist:
                iping = net_connect.send_command("ping vrf " + vrf + " " + ipentry +  "repeat 2")
                if "100.00% packet loss" not in iping: 
                    status = "Success"
                else: 
                    status = "Fail"
                print ("<tr><td>" + ipentry + "</td><td>" + status + "</td></tr>")
                writer = csv.writer(w)
                writer.writerow([ipentry, status])
        w.close()
        print ("</table>")
    dstfile = (hostname + "default.pre_checkout.csv")
    arp_raw = net_connect.send_command("show ip arp")
    ipaddr = re.findall('\d+[.]\d+[.]\d+[.]\d+', arp_raw, re.MULTILINE)
    print("VRF: NONE")
    iplist = util.iplist(arp_raw)
    print ("ARP Entries for VRF Default : " + str(len(iplist)) + "<table><caption>VRF: Default : ARP Entry Ping status</caption><tr><th>IP Address</th><th>Ping Status</th>")
    with open(dstfile, 'w', newline='') as w:
        for ipentry in iplist:
            iping = net_connect.send_command("ping " + ipentry + " repeat 2")
            if "100.00% packet loss" not in iping: 
                status = "Success"
            else: 
                status = "Fail"
            print ("<tr><td>" + ipentry + "</td><td>" + status + "</td></tr>")
            writer = csv.writer(w)
            writer.writerow([ipentry, status])
    w.close()
    print ("</table>")    
if net_connect: net_connect.disconnect()    
