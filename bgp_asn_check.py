#!/usr/bin/python3
from __future__ import print_function, unicode_literals
from netmiko import Netmiko
import util
from ntc_templates.parse import parse_output
import cgi
import cgitb
cgitb.enable()
form = cgi.FieldStorage()
input_as = form.getfirst('input_as')
print("Content-Type: text/html\n\n")
print('''
<style>
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
if int(input_as) >= 64512 and int(input_as) <= 65535:
    devices = ['dc1-core-sw', 'dc2-core-sw', 'dc3-core-sw']
    aslist = []
    print ("<h2> Live ASN Check </h2>")
    for dev in devices:
        device = util.CiscoDeviceRO(host=dev)
        dev_connect = Netmiko(**device.__dict__)
        bgp_out = dev_connect.send_command("show ip bgp vrf all")
        bgp_parsed = parse_output(platform="cisco_nxos", command="show ip bgp", data=bgp_out)
        dev_connect.disconnect()
        print ("Collected BGP table for " + dev)
        print ('<br />') 
        bgpasns = [ sub['as_path'] for sub in bgp_parsed ]
        for asn in bgpasns:
            asnsplit = asn.split()
            for asnum in asnsplit:
                if asnum not in aslist and int(asnum) >=64512 and int(asnum) <=65535:
                    aslist.append(asnum)
    as_map = map(int, aslist)
    as_sort = sorted(as_map)
    print ("<h4> Requested ASN Number: " + str(input_as) + "</h4>")
    if input_as in aslist:
        print ('<p style="color:red;">AS in use and <b>**NOT**</b> AVAILABLE</p>')
    else:
        print ('<p style="color:green;">AS is currently <b>unused</b></p>')
    print ('<br />')     
    print ('<br />')  
    avail = 64512
    avail_count = 5
    print ("<table><caption><b>Next 5 available Private ASNs from range 64512-65535</b></caption><tr>")
    while avail_count > 0:
        if str(avail) not in aslist:
            print ("<td>" + str(avail) + "</td>")
            avail = avail +1
            avail_count = avail_count -1
        else:
            avail = avail +1       
    print ("</tr></table></br />")
    ascount = str(len(aslist))
    print ('<b>Number of unique Private ASNs across all Devices: " + ascount + "</b><br /><br />')
    print ("Ordered List of AS in use: <br />")
    print(as_sort)
else: 
    print ("UNABLE TO VALIDATE: AS Entered was outside of Valid Private Range (64512-65535)")
