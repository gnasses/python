"""
Created on Tue Feb 25 16:46:37 2020

@author: gnasses
"""
input_as = '<ASN>'
import util
from netmiko import Netmiko
from ntc_templates.parse import parse_output
devices = [dc1-core-sw, 'dc2-core-sw', 'dc3-core-sw]
aslist = []
for dev in devices:
    device = util.CiscoDeviceRO(host=dev)
    dev_connect = Netmiko(**device.__dict__)
    bgp_out = dev_connect.send_command("show ip bgp vrf all")
    bgp_parsed = parse_output(platform="cisco_nxos", command="show ip bgp", data=bgp_out)
    dev_connect.disconnect()
    print ("Collected BGP table for " + dev)
    bgpasns = [ sub['as_path'] for sub in bgp_parsed ]
    for asn in bgpasns:
        asnsplit = asn.split()
        for asnum in asnsplit:
            if asnum not in aslist and int(asnum) >=64512 and int(asnum) <=65535:
                aslist.append(asnum)
as_map = map(int, aslist)
as_sort = sorted(as_map)
print ("Requested ASN Number: " + input_as)
if input_as in aslist:
    print ("AS **NOT** AVAIALABLE")
else:
    print ("AS is availble")
avail = 64512
avail_count = 5
print ("Next 5 available Private ASNs from range 64512-65535")
while avail_count > 0:
    if str(avail) not in aslist:
        print (avail)
        avail = avail +1
        avail_count = avail_count -1
    else:
        avail = avail +1       
ascount = str(len(aslist))
print ("Number of unique Private ASNs across all Devices: " + ascount)
print ("Ordered List of AS in use: ")
print(as_sort)
print ()
