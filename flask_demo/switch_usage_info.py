#!/usr/bin/python3
from __future__ import print_function, unicode_literals
import datetime
from netmiko import Netmiko
import util
import cgi
import cgitb
import re
cgitb.enable()
form = cgi.FieldStorage()
hostname = form.getfirst('content3')
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
switch = util.CiscoDeviceRO(host=hostname)
net_connect = Netmiko(**switch.__dict__)
nxos_check = net_connect.send_command("show version")
if "NX-OS" in nxos_check:
    sw_ver = "nxos"
else:
    sw_ver = "ios"
name_port = {}
ports_input = net_connect.send_command("show interface status | i connected")
ports_connected = ports_input.splitlines()
portcount = str(len(ports_connected))
print ("<table><caption>" + hostname + "</caption>")
for line in ports_connected:
    if "mls" not in line and "Vlan" not in line and "SPAN" not in line and "Lo0" not in line: 
        port = line.split(' ')[0]
        print ("<tr><td>" + port + "</td>")
        desc = net_connect.send_command("show interface " + port + " description")
        desc = desc.splitlines()[-1].split('    ')[-1].strip()     
        print ("<td>" + desc + "</td>")
        mac_raw = net_connect.send_command("show mac address interface " + port)
        m = re.findall('\S\S\S\S[.]\S\S\S\S[.]\S\S\S\S', mac_raw, re.MULTILINE)
        macs = []
        ips = []
        for m in m:
            if m not in macs:
                macs.append(m)
                print ("<td>" + m + "</td>")
            arp_raw = net_connect.send_command("show ip arp | i " + m)
            ip = re.findall('^\d+[.]\d+[.]\d+[.]\d+', arp_raw, re.MULTILINE)
            for ip in ip:
                if ip not in ips:
                    print ("<td>" + ip + "</td>")
                    ips.append(ip)
        print ("</tr>")
print ("</table>")
print ("Total Connected Ports: " + portcount)
if net_connect: net_connect.disconnect()

