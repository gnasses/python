#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  26  2020

@author: gnasses
"""
import csv
from netmiko import Netmiko
import util
import datetime
#from pythonping import ping
import cgi
import cgitb
cgitb.enable()
form = cgi.FieldStorage()
hostname = form.getfirst('content5')
#hostname = 'n9k05'
#hostname = 'c6k13'
#hostname = 'n7k01'
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
print ("<b>Post-Change Checkout for device: " + hostname + "</b><br /> Checkout time: " + now + "<br />")
switch = util.CiscoDeviceRO(host=hostname)
net_connect = Netmiko(**switch.__dict__)
sw_ver = util.nxos_check(hostname)
vrf_list = util.vrf_list(hostname)
#open CSV file and generate list
if sw_ver == "nxos":
    for vrf in vrf_list:
        sourcefile = (hostname + "." + vrf + ".pre_checkout.csv")
        dstfile = (hostname + "." + vrf + ".post_checkout.csv")
        precheck = {}
        print ("<table><caption>VRF: " +  vrf + "</caption><tr><th>IP</th><th>Pre-Check Status</th><th>Post-Check status</th><th>Pre-Post Comparison</th></tr>")
        with open(sourcefile, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                ip = row[0]
                pre_status = row[1]
                precheck.update( {ip : pre_status} )
        with open(dstfile, 'w') as d:
            for key, value in precheck.items():
                iping = net_connect.send_command("ping " + key + " vrf " + vrf + " count 2")
                if "100.00% packet loss" not in iping: 
                    status = "Success"
                else: 
                    status = "Fail"
                if status == value:
                    match = '</td><td><b><p style="color:green;">Pass</p></b></td></tr>'
                else: 
                    match = '</td><td><b><p style="color:red;">FAIL!</p></b></td></tr>'
                print ("<tr><td>" + key + "</td><td>" + value + "</td><td>" + status + match)
                writer = csv.writer(d)
                writer.writerow([key, value, status])
        print ("</table>")                                                         
if net_connect: net_connect.disconnect()
